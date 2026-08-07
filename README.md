# Ludek's People Analytics Second Brain 🧠

A public, Obsidian-style second brain built from the <!--N-->206<!--/N--> posts on
[my people analytics blog](https://blog-about-people-analytics.netlify.app/) —
browsable as an interactive knowledge graph, full-text searchable, and
machine-readable for AI agents.

**Live site:** https://lstehlik2809.github.io/people-analytics-second-brain

## How it works

```
People_Analytics_Blog/_posts/*.Rmd        (source of truth)
        │  pipeline/convert.py            → clean markdown notes + assets + figures
        ▼
vault/posts/*.md                          (the second brain)
        │  pipeline/embed_link.py         → chunked full-note embeddings + semantic "Related notes"
        │  pipeline/build_llms.py         → llms.txt / llms-full.txt for AI agents
        │  pipeline/build_semantic_index.mjs → chunked hybrid browser search index
        ▼
site/ (Quartz 5)                          → static site with graph view, search, tag pages
        │  GitHub Actions (deploy.yml)
        ▼
GitHub Pages
```

- **For people:** graph view, backlinks, tags, `Ctrl+K` full-text search, and
  [in-browser hybrid search](https://lstehlik2809.github.io/people-analytics-second-brain/semantic-search.html)
  (BM25 + transformers.js/MiniLM, no server). Hybrid retrieval and related-note
  matching both index overlapping passages across each note's cleaned prose,
  so exact terminology and semantic paraphrases can surface later sections of
  long posts.
- **For AI agents:** a public [MCP server](https://people-analytics-brain-mcp.ludek-stehlik.workers.dev)
  (`https://people-analytics-brain-mcp.ludek-stehlik.workers.dev/mcp`, Streamable HTTP, no auth) with
  `search_notes` / `get_note` / `list_notes` / `list_tags` tools, plus
  [`/llms.txt`](https://lstehlik2809.github.io/people-analytics-second-brain/llms.txt)
  (index) and [`/llms-full.txt`](https://lstehlik2809.github.io/people-analytics-second-brain/llms-full.txt)
  (complete corpus). The worker ([mcp-server/](mcp-server/)) fetches the corpus from the
  live site, so it needs no redeploys when content changes.
