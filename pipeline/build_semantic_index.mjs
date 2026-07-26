// Build the client-side semantic search index.
// Embeds every vault note with the same model the browser page uses
// (Xenova/all-MiniLM-L6-v2 via transformers.js), so query and corpus
// vectors live in the same space. Output: pipeline/cache/semantic_index.json
//
// Usage: node pipeline/build_semantic_index.mjs

import { pipeline } from "@huggingface/transformers";
import { readdirSync, readFileSync, writeFileSync, statSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";

const ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const NOTES = path.join(ROOT, "vault", "posts");
const OUT = path.join(ROOT, "pipeline", "cache", "semantic_index.json");
const MODEL = "Xenova/all-MiniLM-L6-v2";
const MAX_CHUNKS = 3; // body chunks per note, besides the title+description vector
const CHUNK_CHARS = 1100; // ~256 tokens, the model's effective window

function parseNote(file) {
  const text = readFileSync(file, "utf-8");
  const fm = text.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n/);
  const head = fm[1];
  const get = (key) =>
    (head.match(new RegExp(`^${key}:\\s*(.+)$`, "m")) || [])[1]?.trim().replace(/^['"]|['"]$/g, "") ?? "";
  const tags = [...head.matchAll(/^- (.+)$/gm)].map((m) => m[1].trim());
  let body = text.slice(fm[0].length);
  body = body
    .replace(/<!-- RELATED:BEGIN -->[\s\S]*?<!-- RELATED:END -->/, "")
    .replace(/\n---\n> 📄[\s\S]*$/, "")
    .replace(/```[\s\S]*?```/g, " ") // code blocks are noise for a 256-token model
    .replace(/!\[[^\]]*\]\([^)]*\)/g, " ")
    .replace(/\[([^\]]*)\]\([^)]*\)/g, "$1")
    .replace(/\s+/g, " ")
    .trim();
  return { title: get("title"), description: get("description"), date: get("date"), tags, body };
}

function chunk(body) {
  const chunks = [];
  for (let i = 0; i < body.length && chunks.length < MAX_CHUNKS; i += CHUNK_CHARS) {
    chunks.push(body.slice(i, i + CHUNK_CHARS));
  }
  return chunks;
}

const files = readdirSync(NOTES).filter((f) => f.endsWith(".md"));
console.log(`Embedding ${files.length} notes with ${MODEL}...`);
const extractor = await pipeline("feature-extraction", MODEL);

const posts = [];
let vecCount = 0;
for (const file of files) {
  const slug = file.replace(/\.md$/, "");
  const n = parseNote(path.join(NOTES, file));
  const texts = [
    `${n.title}. ${n.description} Topics: ${n.tags.join(", ")}`,
    ...chunk(n.body),
  ];
  const out = await extractor(texts, { pooling: "mean", normalize: true });
  const [rows, dims] = out.dims;
  const data = out.data;
  const vecs = [];
  for (let r = 0; r < rows; r++) {
    vecs.push(Array.from(data.slice(r * dims, (r + 1) * dims), (x) => +x.toFixed(4)));
  }
  vecCount += rows;
  posts.push({ slug, title: n.title, description: n.description, date: n.date, tags: n.tags, vecs });
  if (posts.length % 50 === 0) console.log(`  ${posts.length}/${files.length}`);
}

writeFileSync(OUT, JSON.stringify({ model: MODEL, dims: 384, posts }));
console.log(`done: ${posts.length} notes, ${vecCount} vectors, ${(statSync(OUT).size / 1e6).toFixed(1)} MB -> ${OUT}`);
