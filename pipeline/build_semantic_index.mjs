// Build the client-side hybrid search index. It retains cleaned passage text
// for BM25 and embeds the same passages with the model used by the browser page
// (Xenova/all-MiniLM-L6-v2 via transformers.js), so query and corpus vectors
// live in the same space. Output: pipeline/cache/semantic_index.json
//
// Usage: node pipeline/build_semantic_index.mjs

import { pipeline } from "@huggingface/transformers";
import { readdirSync, readFileSync, writeFileSync, statSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";
import {
  CHUNK_CHARS,
  CHUNK_OVERLAP,
  MAX_CHUNKS,
  chunkBody,
  cleanBody,
} from "./semantic_text.mjs";

const ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const NOTES = path.join(ROOT, "vault", "posts");
const OUT = path.join(ROOT, "pipeline", "cache", "semantic_index.json");
const MODEL = "Xenova/all-MiniLM-L6-v2";
const INDEX_SCHEMA = 3;

function parseNote(file) {
  const text = readFileSync(file, "utf-8");
  const fm = text.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n/);
  const head = fm[1];
  const get = (key) =>
    (head.match(new RegExp(`^${key}:\\s*(.+)$`, "m")) || [])[1]?.trim().replace(/^['"]|['"]$/g, "") ?? "";
  const tags = [...head.matchAll(/^- (.+)$/gm)].map((m) => m[1].trim());
  const body = cleanBody(text.slice(fm[0].length));
  return { title: get("title"), description: get("description"), date: get("date"), tags, body };
}

const files = readdirSync(NOTES).filter((f) => f.endsWith(".md"));
console.log(`Embedding ${files.length} notes with ${MODEL}...`);
const extractor = await pipeline("feature-extraction", MODEL);

const posts = [];
let vecCount = 0;
let passageCount = 0;
let cappedCount = 0;
for (const file of files) {
  const slug = file.replace(/\.md$/, "");
  const n = parseNote(path.join(NOTES, file));
  const bodyChunks = chunkBody(n.body);
  const uncappedCount = n.body.length <= CHUNK_CHARS
    ? (n.body.length ? 1 : 0)
    : Math.ceil((n.body.length - CHUNK_CHARS) / (CHUNK_CHARS - CHUNK_OVERLAP)) + 1;
  if (uncappedCount > MAX_CHUNKS) cappedCount++;
  passageCount += bodyChunks.length;
  const passages = [
    `${n.title}. ${n.description} Topics: ${n.tags.join(", ")}`,
    ...bodyChunks,
  ];
  const out = await extractor(passages, { pooling: "mean", normalize: true });
  const [rows, dims] = out.dims;
  const data = out.data;
  const vecs = [];
  for (let r = 0; r < rows; r++) {
    vecs.push(Array.from(data.slice(r * dims, (r + 1) * dims), (x) => +x.toFixed(4)));
  }
  vecCount += rows;
  posts.push({
    slug,
    title: n.title,
    description: n.description,
    date: n.date,
    tags: n.tags,
    passages,
    vecs,
  });
  if (posts.length % 50 === 0) console.log(`  ${posts.length}/${files.length}`);
}

writeFileSync(OUT, JSON.stringify({
  schema: INDEX_SCHEMA,
  model: MODEL,
  dims: 384,
  vectorCount: vecCount,
  passageCount,
  chunking: {
    chars: CHUNK_CHARS,
    overlap: CHUNK_OVERLAP,
    maxChunks: MAX_CHUNKS,
    overflow: "evenly-spaced",
  },
  posts,
}));
console.log(`done: ${posts.length} notes, ${passageCount} body passages, ${vecCount} total vectors, ${cappedCount} capped notes, ${(statSync(OUT).size / 1e6).toFixed(1)} MB -> ${OUT}`);
