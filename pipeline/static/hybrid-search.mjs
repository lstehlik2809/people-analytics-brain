// Lightweight passage-level BM25 and reciprocal-rank fusion for the
// browser-only hybrid search page. Kept dependency-free so the same module
// can be exercised directly by Node's test runner.

export const DEFAULT_RRF_K = 60;
export const DEFAULT_CANDIDATE_LIMIT = 50;

export function tokenize(text) {
  return (String(text).toLowerCase().match(/[\p{L}\p{N}]+/gu) || [])
    .filter((token) => token.length > 1);
}

export function withBigrams(tokens) {
  const terms = tokens.slice();
  for (let index = 0; index + 1 < tokens.length; index++) {
    terms.push(`${tokens[index]}~${tokens[index + 1]}`);
  }
  return terms;
}

function lexicalPassages(post) {
  const metadata = [
    `${post.title || ""} `.repeat(3),
    `${(post.tags || []).join(" ")} `.repeat(2),
    post.description || "",
  ].join(" ");
  const body = Array.isArray(post.passages) ? post.passages.slice(1) : [];
  return [metadata, ...body];
}

export function buildBm25Index(posts) {
  const docs = [];
  const postings = new Map();

  posts.forEach((post, postIndex) => {
    lexicalPassages(post).forEach((text, passageIndex) => {
      const terms = withBigrams(tokenize(text));
      if (terms.length === 0) return;

      const tf = new Map();
      for (const term of terms) tf.set(term, (tf.get(term) || 0) + 1);
      const docIndex = docs.length;
      docs.push({ postIndex, passageIndex, len: terms.length });
      for (const [term, frequency] of tf) {
        const termPostings = postings.get(term) || [];
        termPostings.push({ docIndex, frequency });
        postings.set(term, termPostings);
      }
    });
  });

  const avgLen = docs.reduce((sum, doc) => sum + doc.len, 0) / (docs.length || 1);
  return { docs, postings, avgLen, postCount: posts.length };
}

export function bm25PostScores(query, index, { k1 = 1.4, b = 0.75 } = {}) {
  const docScores = new Float64Array(index.docs.length);
  const queryTerms = new Set(withBigrams(tokenize(query)));
  const documentCount = index.docs.length;

  for (const term of queryTerms) {
    const termPostings = index.postings.get(term);
    if (!termPostings) continue;
    const documentFrequency = termPostings.length;
    const idf = Math.log(
      1 + (documentCount - documentFrequency + 0.5) / (documentFrequency + 0.5),
    );

    for (const { docIndex, frequency } of termPostings) {
      const doc = index.docs[docIndex];
      const denominator = frequency + k1 * (1 - b + (b * doc.len) / index.avgLen);
      docScores[docIndex] += idf * ((frequency * (k1 + 1)) / denominator);
    }
  }

  const best = Array.from(
    { length: index.postCount },
    () => ({ score: 0, passageIndex: 0 }),
  );
  index.docs.forEach((doc, docIndex) => {
    if (docScores[docIndex] > best[doc.postIndex].score) {
      best[doc.postIndex] = {
        score: docScores[docIndex],
        passageIndex: doc.passageIndex,
      };
    }
  });
  return best;
}

export function semanticPostScores(queryVector, posts) {
  return posts.map((post) => {
    let score = -Infinity;
    let passageIndex = 0;
    for (let vectorIndex = 0; vectorIndex < post.vecs.length; vectorIndex++) {
      const vector = post.vecs[vectorIndex];
      let dot = 0;
      for (let dim = 0; dim < vector.length; dim++) dot += vector[dim] * queryVector[dim];
      if (dot > score) {
        score = dot;
        passageIndex = vectorIndex;
      }
    }
    return { score, passageIndex };
  });
}

function rankedPostIndexes(scores, include) {
  return scores
    .map(({ score }, postIndex) => ({ postIndex, score }))
    .filter(({ score }) => include(score))
    .sort((left, right) => right.score - left.score)
    .map(({ postIndex }) => postIndex);
}

export function hybridSearch(
  query,
  queryVector,
  posts,
  bm25Index,
  {
    resultLimit = 15,
    candidateLimit = DEFAULT_CANDIDATE_LIMIT,
    rrfK = DEFAULT_RRF_K,
  } = {},
) {
  const semantic = semanticPostScores(queryVector, posts);
  const lexical = bm25PostScores(query, bm25Index);
  const semanticRanking = rankedPostIndexes(semantic, Number.isFinite);
  const lexicalRanking = rankedPostIndexes(lexical, (score) => score > 0);
  const fused = new Map();

  const addRanking = (ranking, signal) => {
    ranking.slice(0, candidateLimit).forEach((postIndex, zeroBasedRank) => {
      const row = fused.get(postIndex) || {
        postIndex,
        score: 0,
        semanticRank: null,
        lexicalRank: null,
      };
      const rank = zeroBasedRank + 1;
      row.score += 1 / (rrfK + rank);
      row[`${signal}Rank`] = rank;
      fused.set(postIndex, row);
    });
  };

  addRanking(semanticRanking, "semantic");
  addRanking(lexicalRanking, "lexical");

  return [...fused.values()]
    .sort((left, right) =>
      right.score - left.score ||
      semantic[right.postIndex].score - semantic[left.postIndex].score)
    .slice(0, resultLimit)
    .map((row) => {
      const semanticPassage = semantic[row.postIndex].passageIndex;
      const lexicalPassage = lexical[row.postIndex].passageIndex;
      const passageIndex = row.lexicalRank !== null && lexicalPassage > 0
        ? lexicalPassage
        : semanticPassage;
      return {
        ...row,
        post: posts[row.postIndex],
        passageIndex,
        semanticScore: semantic[row.postIndex].score,
        lexicalScore: lexical[row.postIndex].score,
      };
    });
}
