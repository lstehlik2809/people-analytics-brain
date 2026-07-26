"""Generate llms.txt (index) and llms-full.txt (complete corpus) for AI agents.

Outputs to pipeline/cache/; the build script copies them into the site's
public/ folder after Quartz builds.
"""

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
NOTES_DIR = ROOT / "vault" / "posts"
CACHE = ROOT / "pipeline" / "cache"
SITE_URL = "https://lstehlik2809.github.io/people-analytics-brain"

RELATED_RE = re.compile(r"<!-- RELATED:BEGIN -->.*?<!-- RELATED:END -->\n?", re.S)


def parse(path: Path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.S)
    meta = yaml.safe_load(m.group(1))
    body = RELATED_RE.sub("", text[m.end():]).strip()
    return meta, body


def main():
    CACHE.mkdir(parents=True, exist_ok=True)
    notes = []
    for path in sorted(NOTES_DIR.glob("*.md")):
        meta, body = parse(path)
        notes.append((path.stem, meta, body))
    notes.sort(key=lambda n: n[1].get("date", ""), reverse=True)

    index = [
        "# Ludek's People Analytics Brain",
        "",
        "> A public second brain of 200+ posts on people analytics, statistics, "
        "causal inference, psychometrics, machine learning, and AI by Luděk Stehlík. "
        f"Browsable knowledge graph at {SITE_URL}. "
        "The complete corpus is in /llms-full.txt.",
        "",
        "## Notes",
        "",
    ]
    full = [
        "# Ludek's People Analytics Brain — complete corpus",
        "",
        f"Source: {SITE_URL} | Author: Luděk Stehlík "
        "(https://www.linkedin.com/in/ludekstehlik/)",
        "",
    ]
    for slug, meta, body in notes:
        url = f"{SITE_URL}/posts/{slug}"
        desc = str(meta.get("description", "")).strip()
        index.append(f"- [{meta['title']}]({url}): {desc}")
        full.extend([
            "---",
            "",
            f"# {meta['title']}",
            f"URL: {url}",
            f"Date: {meta.get('date', '')}",
            f"Tags: {', '.join(meta.get('tags', []))}",
            f"Original post: {meta.get('original', '')}",
            "",
            body,
            "",
        ])

    (CACHE / "llms.txt").write_text("\n".join(index), encoding="utf-8", newline="\n")
    (CACHE / "llms-full.txt").write_text("\n".join(full), encoding="utf-8", newline="\n")
    size = (CACHE / "llms-full.txt").stat().st_size
    print(f"llms.txt: {len(notes)} entries; llms-full.txt: {size/1e6:.1f} MB")


if __name__ == "__main__":
    sys.exit(main())
