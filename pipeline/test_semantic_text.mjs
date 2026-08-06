import assert from "node:assert/strict";
import test from "node:test";

import {
  CHUNK_CHARS,
  CHUNK_OVERLAP,
  MAX_CHUNKS,
  boundedChunkStarts,
  chunkBody,
  cleanBody,
} from "./semantic_text.mjs";

test("cleanBody removes retrieval noise but preserves meaningful labels", () => {
  const cleaned = cleanBody([
    "Intro [useful link](https://example.com).",
    "```r\nsecret_code()\n```",
    "![Important chart caption](chart.png)",
    "<!-- RELATED:BEGIN -->ignore me<!-- RELATED:END -->",
  ].join("\n"));

  assert.match(cleaned, /useful link/);
  assert.match(cleaned, /Important chart caption/);
  assert.doesNotMatch(cleaned, /secret_code/);
  assert.doesNotMatch(cleaned, /ignore me/);
});

test("ordinary notes are chunked through their final character", () => {
  const body = "a".repeat(CHUNK_CHARS * 4 + 73);
  const chunks = chunkBody(body);
  const starts = boundedChunkStarts(
    body.length,
    CHUNK_CHARS,
    CHUNK_OVERLAP,
    MAX_CHUNKS,
  );

  assert.equal(starts[0], 0);
  assert.equal(starts.at(-1) + CHUNK_CHARS, body.length);
  assert.equal(chunks.at(-1), body.slice(-CHUNK_CHARS));
});

test("extreme notes respect the cap while sampling beginning through end", () => {
  const length = CHUNK_CHARS * 100;
  const starts = boundedChunkStarts(
    length,
    CHUNK_CHARS,
    CHUNK_OVERLAP,
    MAX_CHUNKS,
  );

  assert.equal(starts.length, MAX_CHUNKS);
  assert.equal(starts[0], 0);
  assert.equal(starts.at(-1), length - CHUNK_CHARS);
  assert.deepEqual(starts, [...new Set(starts)].sort((a, b) => a - b));
});
