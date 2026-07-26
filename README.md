# Ludek's People Analytics Brain 🧠

A public, Obsidian-style second brain built from 200+ posts on
[my people analytics blog](https://blog-about-people-analytics.netlify.app/) —
browsable as an interactive knowledge graph, full-text searchable, and
machine-readable for AI agents.

**Live site:** https://lstehlik2809.github.io/people-analytics-brain

## How it works

```
People_Analytics_Blog/_posts/*.Rmd        (source of truth)
        │  pipeline/convert.py            → clean markdown notes + assets
        ▼
vault/posts/*.md                          (the second brain)
        │  pipeline/embed_link.py         → OpenAI embeddings + semantic "Related notes" wikilinks
        │  pipeline/build_llms.py         → llms.txt / llms-full.txt for AI agents
        ▼
site/ (Quartz 5)                          → static site with graph view, search, tag pages
        │  GitHub Actions (deploy.yml)
        ▼
GitHub Pages
```

- **For people:** graph view, backlinks, tags, and `Ctrl+K` search on the site.
- **For AI agents:** [`/llms.txt`](https://lstehlik2809.github.io/people-analytics-brain/llms.txt)
  (index) and [`/llms-full.txt`](https://lstehlik2809.github.io/people-analytics-brain/llms-full.txt)
  (complete corpus, ~1.2 MB).

## Updating after publishing a new blog post

```powershell
.\update.ps1
```

This incrementally converts new/changed posts (content-hash based), embeds only
what changed, refreshes related-note links, regenerates llms.txt, and pushes —
GitHub Actions then rebuilds and deploys the site.

Requires: Python 3.10+ (`pyyaml`, `openai`, `numpy`, `tiktoken`, `python-dotenv`)
and a `.env` with `OPENAI_API_KEY` and `OPENAI_EMBEDDING_MODEL`.
