"""Convert distill .Rmd blog posts into a Quartz-ready markdown vault.

Idempotent: re-run any time; only notes whose source .Rmd or rendered .html
changed are rewritten.
Usage: python pipeline/convert.py [--force]
"""

import argparse
import base64
import binascii
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

import yaml
from bs4 import BeautifulSoup
from urllib.parse import unquote, unquote_to_bytes

BLOG_POSTS = Path(r"D:\_WORKFORCE_ANALYTICS\People_Analytics_Blog\_posts")
BLOG_BASE_URL = "https://blog-about-people-analytics.netlify.app/posts/"
ROOT = Path(__file__).resolve().parent.parent
VAULT = ROOT / "vault"
NOTES_DIR = VAULT / "posts"
CACHE = ROOT / "pipeline" / "cache"
MANIFEST = CACHE / "manifest.json"

# target is parsed in img_sub, so filenames containing spaces still match
IMG_RE = re.compile(r"!\[([^\]]*)\]\(([^)]*)\)")
TITLE_RE = re.compile(r"\s+\"[^\"]*\"\s*$")
HTML_IMG_RE = re.compile(r"<img\b([^>]*?)/?>", re.I)
ATTR_KV_RE = re.compile(r"""([\w-]+)\s*=\s*(["'])(.*?)\2""")
ATTR_RE = re.compile(r"(\)|\`)\{[^{}\n]*\}")  # pandoc attribute blocks after ) or `
CHUNK_RE = re.compile(r"^```\{(r|R)\b[^}]*\}\s*$", re.M)
PY_CHUNK_RE = re.compile(r"^```\{python[^}]*\}\s*$", re.M)
OTHER_CHUNK_RE = re.compile(r"^```\{[^}]*\}\s*$", re.M)
# Distill sometimes embeds knitr figures directly into the rendered HTML even
# when other post assets are external. Including a converter marker in the
# content hash rebuilds only posts with this representation when support for it
# changes, rather than invalidating the entire manifest.
EMBEDDED_FIGURE_RE = re.compile(
    rb"<div[^>]*class=[\"'][^\"']*\bfigure\b[^\"']*[\"'][^>]*>"
    rb".*?<img[^>]+src=[\"']data:image/",
    re.I | re.S,
)
EMBEDDED_FIGURE_HASH_MARKER = b"\0embedded-generated-figures-v1"
DATA_IMAGE_RE = re.compile(
    r"^data:(image/[a-z0-9.+-]+)((?:;[^,]*)?),(.*)$", re.I | re.S)


def slugify_tag(tag: str) -> str:
    # "/" must not survive: Quartz reads it as tag hierarchy, so a category
    # like "i/o psychology" would spawn a nonsensical parent tag "i"
    return re.sub(r"[^a-z0-9]+", "-", tag.lower().strip()).strip("-")


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

    def copy_asset(path: str):
        """Copy a local image into the note's asset dir; return its new ref,
        or None if it is remote or missing."""
        if path.startswith(("http://", "https://", "data:")):
            return None
        src = post_dir / unquote(path)
        if not src.exists():
            warnings.append(f"{slug}: missing image {path}")
            return None
        # spaces in a filename break markdown links, so normalize on copy
        dest_name = src.name.replace(" ", "-")
        asset_dir.mkdir(parents=True, exist_ok=True)
        dest = asset_dir / dest_name
        if not dest.exists() or src.read_bytes() != dest.read_bytes():
            shutil.copy2(src, dest)
        return f"./{slug}/{dest_name}"

    def img_sub(m):
        alt, target = m.group(1), m.group(2).strip()
        path = TITLE_RE.sub("", target).strip().strip("<>")
        return f"![{alt}]({copy_asset(path) or path})"

    body = IMG_RE.sub(img_sub, body)

    # posts also embed figures with raw <img src="..."> tags; rewrite them as
    # markdown so Quartz resolves their paths the same way it does elsewhere
    def html_img_sub(m):
        attrs = dict((k.lower(), v) for k, _, v in ATTR_KV_RE.findall(m.group(1)))
        new = copy_asset(attrs.get("src", "").strip())
        return f"![{attrs.get('alt', '')}]({new})" if new else m.group(0)

    body = HTML_IMG_RE.sub(html_img_sub, body)
    # strip pandoc attribute blocks like ){width=100%}
    body = ATTR_RE.sub(r"\1", body)
    body = escape_inline_hashtags(body)
    body = blank_pad_html_wrappers(body)
    return body.strip()


FENCE_SPLIT_RE = re.compile(r"(```.*?```)", re.S)
# a decorative hashtag in prose (e.g. "#HappySummer"); Quartz would turn it
# into a real tag, polluting the tag list and graph. Headings are safe: they
# require a space after the hashes. URLs are safe: "#" follows "/" or a word.
INLINE_HASHTAG_RE = re.compile(r"(^|[ \t])#([A-Za-z][\w-]*)", re.M)


def escape_inline_hashtags(body: str) -> str:
    parts = FENCE_SPLIT_RE.split(body)
    for i in range(0, len(parts), 2):  # even indices are outside code fences
        parts[i] = INLINE_HASHTAG_RE.sub(r"\1\\#\2", parts[i])
    return "".join(parts)


WRAP_OPEN_RE = re.compile(r"^<(div|center|aside|p)\b[^>]*>$", re.I)
WRAP_CLOSE_RE = re.compile(r"^</(div|center|aside|p)>$", re.I)


def blank_pad_html_wrappers(body: str) -> str:
    """Pandoc parses markdown inside HTML blocks; CommonMark does not unless
    the markdown is separated from the wrapper tags by blank lines. Pad them
    so e.g. images centered via <div> wrappers still render on the site."""
    lines = body.split("\n")
    out = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if WRAP_CLOSE_RE.match(stripped) and out and out[-1].strip():
            out.append("")
        out.append(line)
        if (WRAP_OPEN_RE.match(stripped)
                and i + 1 < len(lines) and lines[i + 1].strip()):
            out.append("")
    return "\n".join(out)


def norm_code(text: str) -> str:
    lines = [ln.rstrip() for ln in text.replace("\xa0", " ").strip().splitlines()]
    return "\n".join(ln for ln in lines if ln)


def extract_generated_figures(post_dir: Path, base_name: str):
    """Find knitr figures, whether external or embedded as image data.

    Each figure is anchored to the code block that precedes it in the rendered
    HTML (None = no code anchor). Embedded data images are accepted only inside
    a knitr ``div.figure`` so ordinary inline images are not duplicated.
    """
    html_path = post_dir / f"{base_name}.html"
    if not html_path.exists():
        return []
    soup = BeautifulSoup(
        html_path.read_text(encoding="utf-8", errors="replace"), "html.parser")
    figs, last_pre = [], None
    for el in soup.find_all(["pre", "img"]):
        if el.name == "pre":
            last_pre = norm_code(el.get_text())
        else:
            src = el.get("src") or ""
            external = (f"{base_name}_files/" in src and
                        src.lower().endswith(
                            (".png", ".jpg", ".jpeg", ".svg", ".gif")))
            embedded = (src.lower().startswith("data:image/") and
                        el.find_parent("div", class_="figure") is not None)
            if external or embedded:
                alt = el.get("alt") or el.get("aria-label") or ""
                figs.append((last_pre, src, alt))
    return figs


FENCE_RE = re.compile(r"```[a-z]*\n(.*?)\n```", re.S)


def decode_data_image(src: str):
    """Return ``(bytes, extension)`` for a data-image URI, else ``None``."""
    match = DATA_IMAGE_RE.match(src)
    if not match:
        return None
    mime, params, payload = match.groups()
    subtype = mime.split("/", 1)[1].lower()
    extension = {
        "jpeg": "jpg",
        "jpg": "jpg",
        "png": "png",
        "gif": "gif",
        "svg+xml": "svg",
        "webp": "webp",
    }.get(subtype)
    if extension is None:
        return None
    try:
        if ";base64" in params.lower():
            data = base64.b64decode(re.sub(r"\s+", "", payload), validate=True)
        else:
            data = unquote_to_bytes(payload)
    except (binascii.Error, ValueError):
        return None
    return (data, extension) if data else None


def inject_figures(body: str, figs, post_dir: Path, asset_dir: Path,
                   slug: str, warnings: list) -> str:
    if not figs:
        return body
    fences = [(norm_code(m.group(1)), m.end()) for m in FENCE_RE.finditer(body)]
    used = set()
    insertions, appendix = [], []
    for figure_number, (anchor, src, alt) in enumerate(figs, start=1):
        asset_dir.mkdir(parents=True, exist_ok=True)
        if src.lower().startswith("data:image/"):
            decoded = decode_data_image(src)
            if decoded is None:
                warnings.append(
                    f"{slug}: invalid or unsupported embedded generated figure")
                continue
            data, extension = decoded
            dest_name = f"generated-figure-{figure_number:02d}.{extension}"
            dest = asset_dir / dest_name
            if not dest.exists() or dest.read_bytes() != data:
                dest.write_bytes(data)
        else:
            img = post_dir / unquote(src)
            if not img.exists():
                warnings.append(f"{slug}: missing generated figure {src}")
                continue
            dest_name = img.name.replace(" ", "-")
            dest = asset_dir / dest_name
            if not dest.exists() or img.read_bytes() != dest.read_bytes():
                shutil.copy2(img, dest)
        md_img = f"![{alt}](./{slug}/{dest_name})"
        pos = None
        if anchor:
            for i, (code, end) in enumerate(fences):
                if code == anchor and i not in used:
                    used.add(i)
                    pos = end
                    break
            if pos is None:  # same chunk emitted several figures
                for code, end in fences:
                    if code == anchor:
                        pos = end
                        break
        if pos is None:
            appendix.append(md_img)
        else:
            insertions.append((pos, len(insertions), md_img))
    # insert back-to-front; reverse tiebreak keeps same-anchor figures in order
    for pos, _, md_img in sorted(insertions, key=lambda x: (-x[0], -x[1])):
        body = body[:pos] + f"\n\n{md_img}" + body[pos:]
    if appendix:
        body += "\n\n## Figures\n\n" + "\n\n".join(appendix)
    return body


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
    figs = extract_generated_figures(post_dir, rmds[0].stem)
    converted = inject_figures(converted, figs, post_dir, NOTES_DIR / slug,
                               slug, warnings)
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
        # hash .Rmd + rendered .html so re-rendered figures also trigger updates
        h = hashlib.sha256(b"v2:" + rmds[0].read_bytes())
        html = post_dir / f"{rmds[0].stem}.html"
        if html.exists():
            html_bytes = html.read_bytes()
            h.update(html_bytes)
            if EMBEDDED_FIGURE_RE.search(html_bytes):
                h.update(EMBEDDED_FIGURE_HASH_MARKER)
        src_hash = h.hexdigest()
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
        print(f"  wrote: {slug}")

    MANIFEST.write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    print(f"done: {written} notes written, {skipped} unchanged, {len(seen_slugs)} total")


if __name__ == "__main__":
    sys.exit(main())
