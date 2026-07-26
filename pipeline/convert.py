"""Convert distill .Rmd blog posts into a Quartz-ready markdown vault.

Idempotent: re-run any time; only notes whose source .Rmd changed are rewritten.
Usage: python pipeline/convert.py [--force]
"""

import argparse
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

import yaml

BLOG_POSTS = Path(r"D:\_WORKFORCE_ANALYTICS\People_Analytics_Blog\_posts")
BLOG_BASE_URL = "https://blog-about-people-analytics.netlify.app/posts/"
ROOT = Path(__file__).resolve().parent.parent
VAULT = ROOT / "vault"
NOTES_DIR = VAULT / "posts"
CACHE = ROOT / "pipeline" / "cache"
MANIFEST = CACHE / "manifest.json"

IMG_RE = re.compile(r"!\[([^\]]*)\]\(\s*(\./)?([^)\s\"']+)(\s+\"[^\"]*\")?\s*\)")
ATTR_RE = re.compile(r"(\)|\`)\{[^{}\n]*\}")  # pandoc attribute blocks after ) or `
CHUNK_RE = re.compile(r"^```\{(r|R)\b[^}]*\}\s*$", re.M)
PY_CHUNK_RE = re.compile(r"^```\{python[^}]*\}\s*$", re.M)
OTHER_CHUNK_RE = re.compile(r"^```\{[^}]*\}\s*$", re.M)


def slugify_tag(tag: str) -> str:
    return re.sub(r"[^a-z0-9/]+", "-", tag.lower().strip()).strip("-")


def note_slug(post_dir_name: str) -> str:
    return re.sub(r"^\d{4}-\d{2}-\d{2}-", "", post_dir_name)


def split_frontmatter(text: str):
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.S)
    if not m:
        return None, text
    meta = yaml.safe_load(m.group(1))
    return meta, text[m.end():]


def clean_description(desc) -> str:
    if not desc:
        return ""
    return re.sub(r"\s+", " ", str(desc)).strip()


def convert_body(body: str, post_dir: Path, asset_dir: Path, slug: str, warnings: list) -> str:
    # code chunk headers -> plain fenced blocks
    body = CHUNK_RE.sub("```r", body)
    body = PY_CHUNK_RE.sub("```python", body)
    body = OTHER_CHUNK_RE.sub("```", body)

    # copy local images and rewrite refs
    def img_sub(m):
        alt, _, path, _title = m.group(1), m.group(2), m.group(3), m.group(4)
        if path.startswith(("http://", "https://", "data:")):
            return f"![{alt}]({path})"
        src = post_dir / path
        if not src.exists():
            warnings.append(f"{slug}: missing image {path}")
            return f"![{alt}]({path})"
        asset_dir.mkdir(parents=True, exist_ok=True)
        dest = asset_dir / src.name
        if not dest.exists():
            shutil.copy2(src, dest)
        return f"![{alt}](./{slug}/{src.name})"

    body = IMG_RE.sub(img_sub, body)
    # strip pandoc attribute blocks like ){width=100%}
    body = ATTR_RE.sub(r"\1", body)
    return body.strip()


def build_note(post_dir: Path) -> tuple[str, str] | None:
    rmds = sorted(post_dir.glob("*.Rmd"))
    if not rmds:
        return None
    text = rmds[0].read_text(encoding="utf-8", errors="replace")
    meta, body = split_frontmatter(text)
    if meta is None:
        return None

    slug = note_slug(post_dir.name)
    # dir names always start with an ISO date; source YAML dates are mixed-format
    m = re.match(r"^\d{4}-\d{2}-\d{2}", post_dir.name)
    date = m.group(0) if m else str(meta.get("date", ""))
    tags = [slugify_tag(c) for c in (meta.get("categories") or [])]
    original_url = f"{BLOG_BASE_URL}{post_dir.name}/"
    warnings = []
    converted = convert_body(body, post_dir, NOTES_DIR / slug, slug, warnings)
    for w in warnings:
        print(f"  warn: {w}")

    fm = {
        "title": str(meta.get("title", slug)),
        "description": clean_description(meta.get("description")),
        "date": date,
        "tags": tags,
        "original": original_url,
    }
    front = yaml.safe_dump(fm, sort_keys=False, allow_unicode=True, width=10000).strip()
    note = (
        f"---\n{front}\n---\n\n"
        f"{converted}\n\n"
        f"<!-- RELATED:BEGIN -->\n<!-- RELATED:END -->\n\n"
        f"---\n"
        f"> 📄 Read the [original post with full outputs]({original_url}) on my blog.\n"
    )
    return slug, note


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="rebuild all notes")
    args = ap.parse_args()

    NOTES_DIR.mkdir(parents=True, exist_ok=True)
    CACHE.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(MANIFEST.read_text()) if MANIFEST.exists() and not args.force else {}

    seen_slugs = {}
    written = skipped = 0
    for post_dir in sorted(p for p in BLOG_POSTS.iterdir() if p.is_dir()):
        rmds = sorted(post_dir.glob("*.Rmd"))
        if not rmds:
            print(f"  warn: no .Rmd in {post_dir.name}")
            continue
        src_hash = hashlib.sha256(rmds[0].read_bytes()).hexdigest()
        slug = note_slug(post_dir.name)
        if slug in seen_slugs:
            slug = post_dir.name  # de-collide by keeping the date prefix
        seen_slugs[slug] = post_dir.name

        if manifest.get(slug) == src_hash and (NOTES_DIR / f"{slug}.md").exists():
            skipped += 1
            continue
        result = build_note(post_dir)
        if result is None:
            print(f"  warn: could not parse {post_dir.name}")
            continue
        _, note = result
        (NOTES_DIR / f"{slug}.md").write_text(note, encoding="utf-8", newline="\n")
        manifest[slug] = src_hash
        written += 1

    MANIFEST.write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    print(f"done: {written} notes written, {skipped} unchanged, {len(seen_slugs)} total")


if __name__ == "__main__":
    sys.exit(main())
