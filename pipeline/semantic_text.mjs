// Shared text preparation for the browser semantic index.
// Keep this aligned with clean_prose() in embed_link.py.

export const CHUNK_CHARS = 1100;
export const CHUNK_OVERLAP = 150;
export const MAX_CHUNKS = 64;

export function cleanBody(text) {
  return text
    .replace(/<!-- RELATED:BEGIN -->[\s\S]*?<!-- RELATED:END -->/g, " ")
    .replace(/\r?\n---\r?\n> 📄[\s\S]*$/, " ")
    .replace(/```[^\r\n]*\r?\n[\s\S]*?```/g, " ")
    .replace(/!\[([^\]]*)\]\([^)]*\)/g, " $1 ")
    .replace(/\[([^\]]+)\]\([^)]*\)/g, " $1 ")
    .replace(/\[\[(?:[^\]|]+\|)?([^\]]+)\]\]/g, " $1 ")
    .replace(/`([^`]+)`/g, " $1 ")
    .replace(/<[^>]+>/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

export function boundedChunkStarts(length, size, overlap, maxChunks) {
  if (length <= size) return [0];
  if (size <= 0 || overlap < 0 || overlap >= size || maxChunks <= 0) {
    throw new RangeError("invalid chunk configuration");
  }

  const stride = size - overlap;
  const starts = [];
  for (let start = 0; start + size <= length; start += stride) {
    starts.push(start);
  }
  const finalStart = length - size;
  if (starts.at(-1) !== finalStart) starts.push(finalStart);
  if (starts.length <= maxChunks) return starts;
  if (maxChunks === 1) return [0];

  // Extreme future notes retain beginning and end, with the remaining
  // passages sampled uniformly across the document instead of truncating it.
  return Array.from({ length: maxChunks }, (_, index) => {
    const sourceIndex = Math.round(index * (starts.length - 1) / (maxChunks - 1));
    return starts[sourceIndex];
  });
}

export function chunkBody(body) {
  if (!body) return [];
  return boundedChunkStarts(
    body.length,
    CHUNK_CHARS,
    CHUNK_OVERLAP,
    MAX_CHUNKS,
  ).map((start) => body.slice(start, start + CHUNK_CHARS));
}
