"""Embed vault notes (incrementally, content-hash cached) and inject
semantic 'Related notes' wikilinks between RELATED markers.

Usage: python pipeline/embed_link.py [--top-k 5] [--min-sim 0.3]
"""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

import numpy as np
import tiktoken
from dotenv import dotenv_values
from openai import OpenAI

ROOT = Path(__file__).resolve().parent.parent
NOTES_DIR = ROOT / "vault" / "posts"
CACHE = ROOT / "pipeline" / "cache"
EMB_CACHE = CACHE / "embeddings.json"
EXPORT = CACHE / "search_index.json"  # shipped later for client-side search

RELATED_RE = re.compile(r"<!-- RELATED:BEGIN -->.*?<!-- RELATED:END -->", re.S)
MAX_TOKENS = 8000  # embedding model hard limit is 8192
_ENC = tiktoken.get_encoding("cl100k_base")


def note_text_for_embedding(text: str) -> str:
    # strip the related block and footer so link updates don't change the hash
    text = RELATED_RE.sub("", text)
    text = re.sub(r"\n---\n> 📄.*$", "", text, flags=re.S)
    toks = _ENC.encode(text, disallowed_special=())
    return _ENC.decode(toks[:MAX_TOKENS])


def parse_note(path: Path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.S)
    title = re.search(r"^title:\s*(.+)$", m.group(1), re.M).group(1).strip().strip("'\"")
    return title, text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--top-k", type=int, default=5)
    ap.add_argument("--min-sim", type=float, default=0.3)
    args = ap.parse_args()

    env = dotenv_values(ROOT / ".env")
    client = OpenAI(api_key=env["OPENAI_API_KEY"])
    model = env.get("OPENAI_EMBEDDING_MODEL", "text-embedding-3-large")

    cache = json.loads(EMB_CACHE.read_text()) if EMB_CACHE.exists() else {}
    notes = {}  # slug -> (title, full_text, emb_text, hash)
    for path in sorted(NOTES_DIR.glob("*.md")):
        slug = path.stem
        title, text = parse_note(path)
        emb_text = note_text_for_embedding(text)
        h = hashlib.sha256((model + emb_text).encode("utf-8")).hexdigest()
        notes[slug] = (title, text, emb_text, h)

    # embed new/changed notes in batches
    todo = [s for s, (_, _, _, h) in notes.items()
            if s not in cache or cache[s]["hash"] != h]
    print(f"{len(notes)} notes, {len(todo)} need embedding")
    for i in range(0, len(todo), 64):
        batch = todo[i:i + 64]
        resp = client.embeddings.create(
            model=model, input=[notes[s][2] for s in batch])
        for s, d in zip(batch, resp.data):
            cache[s] = {"hash": notes[s][3], "vector": d.embedding}
        print(f"  embedded {min(i + 64, len(todo))}/{len(todo)}")
    # drop deleted notes
    cache = {s: v for s, v in cache.items() if s in notes}
    EMB_CACHE.write_text(json.dumps(cache), encoding="utf-8")

    # cosine similarity matrix
    slugs = sorted(notes)
    mat = np.array([cache[s]["vector"] for s in slugs])
    mat = mat / np.linalg.norm(mat, axis=1, keepdims=True)
    sims = mat @ mat.T

    changed = 0
    for i, slug in enumerate(slugs):
        order = np.argsort(-sims[i])
        links = []
        for j in order:
            if j == i or sims[i][j] < args.min_sim:
                continue
            other = slugs[j]
            links.append(f"- [[{other}|{notes[other][0]}]]")
            if len(links) >= args.top_k:
                break
        block = "<!-- RELATED:BEGIN -->\n## Related notes\n" + \
            "\n".join(links) + "\n<!-- RELATED:END -->" if links else \
            "<!-- RELATED:BEGIN -->\n<!-- RELATED:END -->"
        _, text, _, _ = notes[slug]
        new_text = RELATED_RE.sub(lambda _: block, text, count=1)
        if new_text != text:
            (NOTES_DIR / f"{slug}.md").write_text(new_text, encoding="utf-8", newline="\n")
            changed += 1

    # export compact index for client-side semantic search (vectors rounded)
    export = [{"slug": s, "title": notes[s][0],
               "vector": [round(x, 5) for x in cache[s]["vector"]]}
              for s in slugs]
    EXPORT.write_text(json.dumps(export), encoding="utf-8")
    print(f"done: related-links updated in {changed} notes; search index exported")


if __name__ == "__main__":
    sys.exit(main())
