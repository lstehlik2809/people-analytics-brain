import assert from "node:assert/strict";
import test from "node:test";

import {
  bm25PostScores,
  buildBm25Index,
  hybridSearch,
  tokenize,
  withBigrams,
} from "./static/hybrid-search.mjs";

function post(title, description, passages, vecs, tags = []) {
  return { title, description, tags, passages, vecs };
}

test("tokenization retains Unicode terms and adds phrase bigrams", () => {
  const tokens = tokenize("DIF and psychometrics in Praha");
  assert.deepEqual(tokens, ["dif", "and", "psychometrics", "in", "praha"]);
  assert.ok(withBigrams(tokens).includes("dif~and"));
});

test("BM25 finds an exact term in a later body passage", () => {
  const posts = [
    post("General modelling", "Broad overview", ["meta", "ordinary regression material"], [[1, 0], [1, 0]]),
    post("Survey measurement", "Reliability", ["meta", "intro", "differential item functioning DIF"], [[0, 1], [0, 1], [0, 1]]),
  ];
  const scores = bm25PostScores("DIF", buildBm25Index(posts));

  assert.equal(scores[0].score, 0);
  assert.ok(scores[1].score > 0);
  assert.equal(scores[1].passageIndex, 2);
});

test("hybrid RRF rewards a result supported by both retrieval signals", () => {
  const posts = [
    post("Semantic only", "employee departures", ["meta", "why workers leave"], [[0.99, 0.1], [0.99, 0.1]]),
    post("Lexical only", "attrition terminology", ["meta", "attrition"], [[0, 1], [0, 1]]),
    post("Attrition", "retention evidence", ["meta", "attrition among employees"], [[1, 0], [1, 0]]),
  ];
  const results = hybridSearch(
    "attrition",
    [1, 0],
    posts,
    buildBm25Index(posts),
    { resultLimit: 3 },
  );

  assert.equal(results[0].post.title, "Attrition");
  assert.notEqual(results[0].semanticRank, null);
  assert.notEqual(results[0].lexicalRank, null);
});
