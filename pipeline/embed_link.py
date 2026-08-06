"""Embed cleaned note prose in chunks and inject semantic related-note links.

Embeddings are incrementally content-hash cached. Long notes are represented by
multiple passages instead of being truncated at the embedding model's context
window. Usage: python pipeline/embed_link.py [--top-k 5] [--min-sim 0.3]
"""

import argparse
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

import numpy as np
import tiktoken
import yaml
from dotenv import dotenv_values
from openai import OpenAI

ROOT = Path(__file__).resolve().parent.parent
NOTES_DIR = ROOT / "vault" / "posts"
CACHE = ROOT / "pipeline" / "cache"
EMB_CACHE = CACHE / "embeddings.json"
EMB_BACKUP = CACHE / "backups" / "embeddings-single-vector.json"
EXPORT = CACHE / "search_index.json"  # local/debug export; not deployed

CACHE_SCHEMA = 2
CLEANING_SCHEMA = 1
CHUNK_TOKENS = 800
CHUNK_OVERLAP = 100
MAX_CHUNKS = 24
PAIR_TOP_MATCHES = 2

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.S)
RELATED_RE = re.compile(r"<!-- RELATED:BEGIN -->.*?<!-- RELATED:END -->", re.S)
FOOTER_RE = re.compile(r"\n---\n> 📄.*$", re.S)
FENCED_CODE_RE = re.compile(r"```[^\n]*\n.*?```", re.S)
IMAGE_RE = re.compile(r"!\[([^\]]*)\]\([^)]*\)")
LINK_RE = re.compile(r"\[([^\]]+)\]\([^)]*\)")
WIKILINK_RE = re.compile(r"\[\[(?:[^\]|]+\|)?([^\]]+)\]\]")
HTML_TAG_RE = re.compile(r"<[^>]+>")
INLINE_CODE_RE = re.compile(r"`([^`]+)`")
_ENC = tiktoken.get_encoding("cl100k_base")


def clean_prose(text: str) -> str:
    """Remove retrieval noise while retaining human-readable semantic text."""
    text = RELATED_RE.sub(" ", text)
    text = FOOTER_RE.sub(" ", text)
    text = FENCED_CODE_RE.sub(" ", text)
    text = IMAGE_RE.sub(r" \1 ", text)  # chart/image captions are meaningful
    text = LINK_RE.sub(r" \1 ", text)
    text = WIKILINK_RE.sub(r" \1 ", text)
    text = INLINE_CODE_RE.sub(r" \1 ", text)
    text = HTML_TAG_RE.sub(" ", text)
    return re.sub(r"\s+", " ", text).strip()


def bounded_chunk_starts(length: int, size: int, overlap: int,
                         max_chunks: int) -> list[int]:
    """Return full-coverage starts, or evenly sampled starts when capped."""
    if length <= size:
        return [0]
    stride = size - overlap
    starts = list(range(0, length - size + 1, stride))
    final_start = length - size
    if starts[-1] != final_start:
        starts.append(final_start)
    if len(starts) <= max_chunks:
        return starts
    # Preserve beginning and end while sampling evenly across an extreme note.
    indices = [round(i * (len(starts) - 1) / (max_chunks - 1))
               for i in range(max_chunks)]
    return [starts[i] for i in indices]


def chunk_prose(text: str) -> list[str]:
    tokens = _ENC.encode(text, disallowed_special=())
    if not tokens:
        return [""]
    starts = bounded_chunk_starts(
        len(tokens), CHUNK_TOKENS, CHUNK_OVERLAP, MAX_CHUNKS)
    return [_ENC.decode(tokens[start:start + CHUNK_TOKENS])
            for start in starts]


def parse_note(path: Path, model: str):
    text = path.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(text)
    if not match:
        raise ValueError(f"missing frontmatter: {path}")
    meta = yaml.safe_load(match.group(1)) or {}
    title = str(meta.get("title", path.stem))
    description = str(meta.get("description", "")).strip()
    tags = [str(tag) for tag in (meta.get("tags") or [])]
    header = f"{title}. {description} Topics: {', '.join(tags)}".strip()
    prose = clean_prose(text[match.end():])
    chunks = [f"{header}\n\n{chunk}".strip() for chunk in chunk_prose(prose)]

    hasher = hashlib.sha256(
        f"schema={CACHE_SCHEMA};cleaning={CLEANING_SCHEMA};model={model};tokens={CHUNK_TOKENS};"
        f"overlap={CHUNK_OVERLAP};max={MAX_CHUNKS}".encode("utf-8"))
    for chunk in chunks:
        hasher.update(b"\0")
        hasher.update(chunk.encode("utf-8"))
    return {
        "title": title,
        "text": text,
        "chunks": chunks,
        "hash": hasher.hexdigest(),
    }


def load_cache() -> dict:
    if not EMB_CACHE.exists():
        return {}
    raw = json.loads(EMB_CACHE.read_text(encoding="utf-8"))
    if (isinstance(raw, dict) and raw.get("schema") == CACHE_SCHEMA and
            isinstance(raw.get("notes"), dict)):
        return raw["notes"]

    # Preserve the last single-vector cache before the one-time schema upgrade.
    EMB_BACKUP.parent.mkdir(parents=True, exist_ok=True)
    if not EMB_BACKUP.exists():
        shutil.copy2(EMB_CACHE, EMB_BACKUP)
        print(f"legacy embedding cache backed up to {EMB_BACKUP}")
    return {}


def save_cache(cache: dict, model: str):
    payload = {
        "schema": CACHE_SCHEMA,
        "cleaningSchema": CLEANING_SCHEMA,
        "model": model,
        "chunking": {
            "tokens": CHUNK_TOKENS,
            "overlap": CHUNK_OVERLAP,
            "maxChunks": MAX_CHUNKS,
            "overflow": "evenly-spaced",
        },
        "notes": cache,
    }
    EMB_CACHE.write_text(json.dumps(payload), encoding="utf-8")


def pair_score(cross_similarities: np.ndarray) -> float:
    """Symmetric mean of each note's strongest passage matches."""
    a_best = np.max(cross_similarities, axis=1)
    b_best = np.max(cross_similarities, axis=0)

    def strongest_mean(values):
        count = min(PAIR_TOP_MATCHES, len(values))
        return float(np.mean(np.partition(values, -count)[-count:]))

    return (strongest_mean(a_best) + strongest_mean(b_best)) / 2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--top-k", type=int, default=5)
    ap.add_argument("--min-sim", type=float, default=0.3)
    args = ap.parse_args()

    env = dotenv_values(ROOT / ".env")
    client = OpenAI(api_key=env["OPENAI_API_KEY"])
    model = env.get("OPENAI_EMBEDDING_MODEL", "text-embedding-3-large")

    cache = load_cache()
    notes = {path.stem: parse_note(path, model)
             for path in sorted(NOTES_DIR.glob("*.md"))}

    todo = [slug for slug, note in notes.items()
            if (slug not in cache or cache[slug].get("hash") != note["hash"] or
                len(cache[slug].get("vectors", [])) != len(note["chunks"]))]
    passages = [(slug, index, chunk)
                for slug in todo
                for index, chunk in enumerate(notes[slug]["chunks"])]
    print(f"{len(notes)} notes, {len(todo)} need embedding "
          f"({len(passages)} passages)")

    pending = {slug: [None] * len(notes[slug]["chunks"]) for slug in todo}
    for offset in range(0, len(passages), 64):
        batch = passages[offset:offset + 64]
        resp = client.embeddings.create(
            model=model, input=[item[2] for item in batch])
        for (slug, index, _), data in zip(batch, resp.data):
            pending[slug][index] = data.embedding
        print(f"  embedded {min(offset + 64, len(passages))}/{len(passages)} passages")
    for slug in todo:
        cache[slug] = {"hash": notes[slug]["hash"],
                       "vectors": pending[slug]}

    cache = {slug: value for slug, value in cache.items() if slug in notes}
    save_cache(cache, model)

    # Build one chunk-level cosine matrix, then aggregate each note pair with a
    # symmetric strongest-passages score to avoid truncation and length bias.
    slugs = sorted(notes)
    rows, ranges = [], {}
    for slug in slugs:
        start = len(rows)
        rows.extend(cache[slug]["vectors"])
        ranges[slug] = slice(start, len(rows))
    matrix = np.asarray(rows, dtype=np.float32)
    matrix /= np.linalg.norm(matrix, axis=1, keepdims=True)
    chunk_sims = matrix @ matrix.T
    note_sims = np.full((len(slugs), len(slugs)), -np.inf, dtype=np.float32)
    for i, left in enumerate(slugs):
        for j in range(i + 1, len(slugs)):
            right = slugs[j]
            score = pair_score(chunk_sims[ranges[left], ranges[right]])
            note_sims[i, j] = note_sims[j, i] = score

    changed = 0
    for i, slug in enumerate(slugs):
        links = []
        for j in np.argsort(-note_sims[i]):
            if note_sims[i, j] < args.min_sim:
                continue
            other = slugs[j]
            links.append(f"- [[{other}|{notes[other]['title']}]]")
            if len(links) >= args.top_k:
                break
        block = ("<!-- RELATED:BEGIN -->\n## Related notes\n" +
                 "\n".join(links) + "\n<!-- RELATED:END -->" if links else
                 "<!-- RELATED:BEGIN -->\n<!-- RELATED:END -->")
        text = notes[slug]["text"]
        new_text = RELATED_RE.sub(lambda _: block, text, count=1)
        if new_text != text:
            (NOTES_DIR / f"{slug}.md").write_text(
                new_text, encoding="utf-8", newline="\n")
            changed += 1

    export = {
        "schema": CACHE_SCHEMA,
        "model": model,
        "notes": [{
            "slug": slug,
            "title": notes[slug]["title"],
            "vectors": [[round(x, 5) for x in vector]
                        for vector in cache[slug]["vectors"]],
        } for slug in slugs],
    }
    EXPORT.write_text(json.dumps(export), encoding="utf-8")
    print(f"done: {len(rows)} passages; related-links updated in "
          f"{changed} notes; search index exported")


if __name__ == "__main__":
    sys.exit(main())
