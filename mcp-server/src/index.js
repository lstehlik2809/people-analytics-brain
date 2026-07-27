// Public MCP server for Ludek's People Analytics Brain.
//
// Speaks MCP Streamable HTTP (stateless JSON mode) at POST /mcp.
// Content is never bundled: the worker pulls llms-full.txt from the live
// GitHub Pages site and indexes it in memory, so publishing a new blog
// post updates this server automatically — no redeploys.

const SITE = "https://lstehlik2809.github.io/people-analytics-second-brain";
const CORPUS_URL = `${SITE}/llms-full.txt`;
const INDEX_TTL_MS = 15 * 60 * 1000;
const PROTOCOL_VERSIONS = ["2025-06-18", "2025-03-26"];

const SERVER_INFO = {
  name: "people-analytics-brain",
  title: "Ludek's People Analytics Second Brain",
  version: "1.1.0",
};

const TOOLS = [
  {
    name: "search_notes",
    description:
      "Full-text search (BM25) across all notes on people analytics, statistics, " +
      "causal inference, psychometrics, machine learning, and AI by Ludek Stehlik. " +
      "Each result carries the best-matching snippet, the section (heading) it came from, and " +
      "`chars` — the note's full length, so you can judge the cost of get_note before calling it. " +
      "Code blocks are excluded from the index but returned by get_note.",
    inputSchema: {
      type: "object",
      properties: {
        query: { type: "string", description: "Search terms (keywords work best)" },
        top_k: { type: "number", description: "Max results (default 8, max 25)" },
        tag: { type: "string", description: "Optional: restrict to one tag (see list_tags)" },
      },
      required: ["query"],
    },
  },
  {
    name: "get_note",
    description: "Fetch the complete markdown of one note by its slug.",
    inputSchema: {
      type: "object",
      properties: {
        slug: { type: "string", description: "Note slug, e.g. 'conditional-inference-tree'" },
      },
      required: ["slug"],
    },
  },
  {
    name: "get_section",
    description:
      "Read one section of a note instead of the whole thing — use this for long notes rather " +
      "than spending the context on get_note. Call with only a slug to get the note's outline " +
      "(headings and their sizes), then call again with a heading to get that section's markdown " +
      "(including any subsections). The `section` field on a search_notes result can be passed " +
      "here directly. Notes without headings return their full text.",
    inputSchema: {
      type: "object",
      properties: {
        slug: { type: "string", description: "Note slug, e.g. 'causal-inference-in-people-analytics'" },
        heading: {
          type: "string",
          description:
            "Heading to read. Case-insensitive, and a distinctive fragment is enough. " +
            "Omit to list the available headings.",
        },
      },
      required: ["slug"],
    },
  },
  {
    name: "list_notes",
    description:
      "List notes (title, slug, date, tags, description), newest first. Optionally filter by tag.",
    inputSchema: {
      type: "object",
      properties: {
        tag: { type: "string", description: "Optional tag filter" },
        limit: { type: "number", description: "Max notes (default 30, max 250)" },
      },
    },
  },
  {
    name: "list_tags",
    description: "All topic tags with note counts — the map of what this brain covers.",
    inputSchema: { type: "object", properties: {} },
  },
];

// ---------- corpus loading & indexing ----------

let cached = null; // { at, notes, index }

function tokenize(text) {
  return (text.toLowerCase().match(/[a-z0-9]+/g) || []).filter((t) => t.length > 1);
}

// Records emitted by pipeline/build_llms.py look like:
//   ---\n\n# {title}\nURL: …\nDate: …\nTags: …\nOriginal post: …\n\n{body}
// A body may itself contain a "---" horizontal rule, so records are matched by
// their full header and terminated by a lookahead for the *next* header —
// splitting on "---" alone silently truncates such notes.
const RECORD_START_RE = /\n(?=---\n\n# [^\n]*\nURL: )/;
const RECORD_RE =
  /^---\n\n# (.+)\nURL: (.+)\nDate: (.*)\nTags: (.*)\nOriginal post: (.*)\n\n([\s\S]*)$/;

// URLs are dead weight in the search text: their path segments tokenize into
// junk terms, and a single long query string (ResearchGate's base64 `_tp=…`,
// for instance) can eat an entire 300-character snippet. Markdown links keep
// their label, which is the part that actually describes the target.
function stripUrls(text) {
  return text
    .replace(/!\[([^\]]*)\]\([^)]*\)/g, "$1")   // images → alt text
    .replace(/\[([^\]]*)\]\([^)]*\)/g, "$1")    // links → label
    .replace(/<https?:\/\/[^>]*>/g, " ")        // autolinks
    .replace(/https?:\/\/\S+/g, " ");           // bare URLs
}

function parseCorpus(text) {
  const notes = [];
  for (const chunk of text.split(RECORD_START_RE)) {
    const m = chunk.match(RECORD_RE);
    if (!m) continue; // the file preamble
    const [, title, url, date, tags, original, body] = m;
    notes.push({
      slug: url.trim().split("/").pop(),
      title: title.trim(),
      url: url.trim(),
      date: date.trim(),
      tags: tags.split(",").map((t) => t.trim()).filter(Boolean),
      original: original.trim(),
      body: body.trim(),
      // code and URLs are kept in `body` (get_note still returns them) but
      // excluded from the searchable text: identifiers like a variable named
      // `cutoff` otherwise produce false positives for technical queries
      text: stripUrls(body.replace(/```[\s\S]*?```/g, " ")).trim(),
    });
  }
  return notes;
}

// adjacent token pairs make multi-word method names ("regression discontinuity",
// "difference in differences") behave like bound terms, without a curated list
function withBigrams(tokens) {
  const out = tokens.slice();
  for (let i = 0; i + 1 < tokens.length; i++) out.push(`${tokens[i]}~${tokens[i + 1]}`);
  return out;
}

function buildIndex(notes) {
  const docs = notes.map((n) => {
    // weight title/tags/description-ish head of the body by repeating them
    const head = `${n.title} ${n.tags.join(" ")} `;
    const tf = new Map();
    const tokens = withBigrams(tokenize(head.repeat(3) + n.text));
    for (const t of tokens) tf.set(t, (tf.get(t) || 0) + 1);
    return { tf, len: tokens.length };
  });
  const df = new Map();
  for (const d of docs) for (const t of d.tf.keys()) df.set(t, (df.get(t) || 0) + 1);
  const avgLen = docs.reduce((a, d) => a + d.len, 0) / (docs.length || 1);
  return { docs, df, avgLen, n: docs.length };
}

async function getCorpus() {
  if (cached && Date.now() - cached.at < INDEX_TTL_MS) return cached;
  const resp = await fetch(CORPUS_URL, { cf: { cacheTtl: 600 } });
  if (!resp.ok) throw new Error(`corpus fetch failed: HTTP ${resp.status}`);
  const notes = parseCorpus(await resp.text());
  if (notes.length === 0) throw new Error("corpus parse produced 0 notes");
  cached = { at: Date.now(), notes, index: buildIndex(notes) };
  return cached;
}

function bm25(queryTokens, { docs, df, avgLen, n }) {
  const k1 = 1.4, b = 0.75;
  const scores = new Array(n).fill(0);
  for (const q of new Set(queryTokens)) {
    const dfq = df.get(q);
    if (!dfq) continue;
    const idf = Math.log(1 + (n - dfq + 0.5) / (dfq + 0.5));
    docs.forEach((d, i) => {
      const f = d.tf.get(q);
      if (!f) return;
      scores[i] += idf * ((f * (k1 + 1)) / (f + k1 * (1 - b + (b * d.len) / avgLen)));
    });
  }
  return scores;
}

const HEADING_RE = /^(#{1,6})\s+(.+)$/gm;

/**
 * Sections of a note. Each runs from its heading to the next heading of the
 * same or higher level, so asking for a parent returns its subsections too.
 */
function parseSections(body) {
  const heads = [];
  HEADING_RE.lastIndex = 0;
  for (let m; (m = HEADING_RE.exec(body)); ) {
    heads.push({ level: m[1].length, heading: m[2].trim(), start: m.index });
  }
  return heads.map((h, i) => {
    let end = body.length;
    for (let j = i + 1; j < heads.length; j++) {
      if (heads[j].level <= h.level) { end = heads[j].start; break; }
    }
    return { ...h, end, chars: end - h.start };
  });
}

const normHeading = (s) => s.toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();

/** Markdown heading containing `pos`, or null when the note has no sections. */
function sectionAt(text, pos) {
  let current = null;
  HEADING_RE.lastIndex = 0;
  for (let m; (m = HEADING_RE.exec(text)); ) {
    if (m.index > pos) break;
    current = m[2].trim();
  }
  return current;
}

/**
 * Window with the most *distinct* query terms rather than the first match:
 * taking the earliest hit surfaces whichever term happens to appear first,
 * which on a long note is usually the wrong section.
 */
function snippet(text, queryTokens, width = 300) {
  const lower = text.toLowerCase();
  const hits = [];
  for (const q of new Set(queryTokens)) {
    for (let i = lower.indexOf(q); i !== -1; i = lower.indexOf(q, i + q.length)) {
      hits.push({ at: i, q });
      if (hits.length > 400) break; // guard against pathological repetition
    }
  }
  let start = 0;
  if (hits.length) {
    let best = -1;
    for (const h of hits) {
      const w0 = Math.max(0, h.at - Math.floor(width / 3));
      const inWindow = hits.filter((x) => x.at >= w0 && x.at < w0 + width);
      // distinct terms dominate; raw density breaks ties
      const score = new Set(inWindow.map((x) => x.q)).size * 1000 + inWindow.length;
      if (score > best) { best = score; start = w0; }
    }
  }
  const cut = text.slice(start, start + width).replace(/\s+/g, " ").trim();
  return {
    text: (start > 0 ? "…" : "") + cut + (start + width < text.length ? "…" : ""),
    section: sectionAt(text, start),
  };
}

// ---------- tool implementations ----------

async function runTool(name, args) {
  const { notes, index } = await getCorpus();
  switch (name) {
    case "search_notes": {
      const query = String(args?.query ?? "").trim();
      if (!query) throw new Error("query is required");
      const topK = Math.min(Math.max(1, args?.top_k ?? 8), 25);
      const tag = args?.tag ? String(args.tag).toLowerCase() : null;
      const qTokens = tokenize(query);
      const scores = bm25(withBigrams(qTokens), index);
      const matched = notes
        .map((note, i) => ({ note, score: scores[i] }))
        .filter((h) => h.score > 0 && (!tag || h.note.tags.includes(tag)))
        .sort((a, b) => b.score - a.score);
      const hits = matched.slice(0, topK).map(({ note, score }) => {
        const s = snippet(note.text, qTokens);
        return {
          slug: note.slug,
          title: note.title,
          date: note.date,
          tags: note.tags,
          url: note.url,
          score: +score.toFixed(2),
          section: s.section,
          snippet: s.text,
          chars: note.body.length,
        };
      });
      // count every match, not just the returned page, so an agent can tell
      // "nothing here" apart from "more available"
      return { query, total_matches: matched.length, returned: hits.length, results: hits };
    }
    case "get_note": {
      const note = notes.find((n) => n.slug === String(args?.slug ?? "").trim());
      if (!note) throw new Error(`no note with slug '${args?.slug}' — use search_notes or list_notes to find slugs`);
      return {
        slug: note.slug, title: note.title, date: note.date, tags: note.tags,
        url: note.url, original_post: note.original, markdown: note.body,
      };
    }
    case "get_section": {
      const slug = String(args?.slug ?? "").trim();
      const note = notes.find((n) => n.slug === slug);
      if (!note) throw new Error(`no note with slug '${slug}' — use search_notes or list_notes to find slugs`);
      const sections = parseSections(note.body);
      const outline = sections.map((s) => ({ heading: s.heading, level: s.level, chars: s.chars }));

      const wanted = args?.heading ? String(args.heading).trim() : null;
      if (!wanted) {
        // no heading asked for: hand back the outline (or the whole note when
        // it has no sections and is small enough to be worth returning)
        return sections.length
          ? { slug, title: note.title, url: note.url, chars: note.body.length,
              sections: outline,
              hint: "Call get_section again with one of these headings to read just that part." }
          : { slug, title: note.title, url: note.url, chars: note.body.length,
              sections: [], markdown: note.body,
              note: "This note has no headings, so its full text is returned." };
      }

      const target = normHeading(wanted);
      const hit =
        sections.find((s) => normHeading(s.heading) === target) ??
        sections.find((s) => normHeading(s.heading).includes(target)) ??
        sections.find((s) => target.includes(normHeading(s.heading)));
      if (!hit) {
        throw new Error(
          `no heading matching '${wanted}' in '${slug}'. Available: ` +
          (outline.length ? outline.map((s) => s.heading).join(" | ") : "(none — this note has no headings)"),
        );
      }
      return {
        slug, title: note.title, url: note.url,
        heading: hit.heading, level: hit.level,
        chars: hit.chars, note_chars: note.body.length,
        markdown: note.body.slice(hit.start, hit.end).trim(),
      };
    }
    case "list_notes": {
      const tag = args?.tag ? String(args.tag).toLowerCase() : null;
      const limit = Math.min(Math.max(1, args?.limit ?? 30), 250);
      const rows = notes
        .filter((n) => !tag || n.tags.includes(tag))
        .sort((a, b) => b.date.localeCompare(a.date))
        .slice(0, limit)
        .map((n) => ({
          slug: n.slug, title: n.title, date: n.date, tags: n.tags,
          description: snippet(n.text, [], 180).text,
          chars: n.body.length,
        }));
      return { count: rows.length, notes: rows };
    }
    case "list_tags": {
      const counts = {};
      for (const n of notes) for (const t of n.tags) counts[t] = (counts[t] || 0) + 1;
      const tags = Object.entries(counts)
        .sort((a, b) => b[1] - a[1])
        .map(([tagName, count]) => ({ tag: tagName, count }));
      return { total_notes: notes.length, tags };
    }
    default:
      return null; // unknown tool
  }
}

// ---------- MCP JSON-RPC over Streamable HTTP ----------

function rpcResult(id, result) {
  return { jsonrpc: "2.0", id, result };
}
function rpcError(id, code, message) {
  return { jsonrpc: "2.0", id, error: { code, message } };
}

async function handleRpc(msg) {
  const { id, method, params } = msg;
  switch (method) {
    case "initialize": {
      const requested = params?.protocolVersion;
      let size = "";
      try {
        // keep the corpus size accurate rather than hard-coded
        size = ` (${(await getCorpus()).notes.length} notes)`;
      } catch {
        // handshake must not depend on the corpus being reachable
      }
      return rpcResult(id, {
        protocolVersion: PROTOCOL_VERSIONS.includes(requested) ? requested : PROTOCOL_VERSIONS[0],
        capabilities: { tools: {} },
        serverInfo: SERVER_INFO,
        instructions:
          `Search and read Ludek Stehlik's public second brain${size} on people analytics, ` +
          "statistics, causal inference, psychometrics, machine learning, and AI.\n\n" +
          "How to use it well:\n" +
          "1. For a specific question, call search_notes with concise keywords, not a full " +
          "conversational sentence. Search is lexical (BM25), so wording matters; the optional " +
          "tag argument narrows results.\n" +
          "2. Use the ranked snippets only to choose candidates. Before answering anything " +
          "substantive, read the full text of the one or two most relevant results: a snippet is " +
          "~300 characters and routinely omits the caveats, assumptions and limitations that make " +
          "these notes worth citing. Each result reports `chars` and the `section` it matched — " +
          "for a long note prefer get_section(slug, section) over pulling the whole thing; " +
          "get_note is the right call for short notes or when you need the whole argument.\n" +
          "3. If a search returns little, retry with related terminology (e.g. \"attrition\" vs " +
          "\"turnover\") or run several narrower searches.\n" +
          "4. For broad or exploratory questions, start with list_tags to see the topic map, or " +
          "list_notes to browse; both accept a tag filter.\n" +
          "5. Ground answers in the retrieved notes, keep their caveats, and cite the titles and " +
          "URLs the tools return so readers can check the source.\n\n" +
          `The complete corpus is also available as plain text at ${SITE}/llms-full.txt.`,
      });
    }
    case "ping":
      return rpcResult(id, {});
    case "tools/list":
      return rpcResult(id, { tools: TOOLS });
    case "tools/call": {
      const name = params?.name;
      try {
        const out = await runTool(name, params?.arguments ?? {});
        if (out === null) return rpcError(id, -32602, `unknown tool: ${name}`);
        return rpcResult(id, { content: [{ type: "text", text: JSON.stringify(out, null, 2) }] });
      } catch (e) {
        return rpcResult(id, { content: [{ type: "text", text: `Error: ${e.message}` }], isError: true });
      }
    }
    default:
      if (id === undefined) return null; // notification — no response
      return rpcError(id, -32601, `method not found: ${method}`);
  }
}

const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Accept, Authorization, Mcp-Session-Id, Mcp-Protocol-Version",
  "Access-Control-Expose-Headers": "Mcp-Session-Id",
};

export default {
  async fetch(request) {
    const url = new URL(request.url);
    if (request.method === "OPTIONS") return new Response(null, { headers: CORS });

    if (url.pathname === "/mcp") {
      if (request.method !== "POST") {
        return new Response("Method Not Allowed", { status: 405, headers: CORS });
      }
      let body;
      try {
        body = await request.json();
      } catch {
        return new Response(JSON.stringify(rpcError(null, -32700, "parse error")), {
          status: 400, headers: { "Content-Type": "application/json", ...CORS },
        });
      }
      const messages = Array.isArray(body) ? body : [body];
      const replies = (await Promise.all(messages.map(handleRpc))).filter(Boolean);
      if (replies.length === 0) return new Response(null, { status: 202, headers: CORS });
      const payload = Array.isArray(body) ? replies : replies[0];
      return new Response(JSON.stringify(payload), {
        headers: { "Content-Type": "application/json", ...CORS },
      });
    }

    // human-facing root
    return new Response(
      `Ludek's People Analytics Second Brain — MCP server\n\n` +
      `MCP endpoint (Streamable HTTP): POST ${url.origin}/mcp\n` +
      `Tools: ${TOOLS.map((t) => t.name).join(", ")}\n\n` +
      `Browse as a human instead: ${SITE}\n` +
      `Plain-text corpus for AI: ${SITE}/llms-full.txt\n`,
      { headers: { "Content-Type": "text/plain; charset=utf-8", ...CORS } },
    );
  },
};
