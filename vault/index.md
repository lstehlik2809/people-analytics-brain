---
title: Welcome to my People Analytics Second Brain 🧠
description: A public second brain built from my people analytics blog — browsable as a knowledge graph, searchable, and open to AI agents.
---

This is the interconnected, "second brain" version of my [blog about people analytics](https://blog-about-people-analytics.netlify.app/) — <!--N-->206<!--/N--> posts on **people analytics, statistics, causal inference, psychometrics, machine learning, and AI**, rebuilt as a network of linked notes.

## How to explore

- 🕸️ **Graph view** — the graph on each page shows how notes connect; click any node to jump, or use the icon in its corner to open the whole network. Reading the nodes: **hollow rings are topics**, solid dots are posts; the **dark node is the page you're on**, **green ones are posts you've already opened** (remembered privately in your own browser), and grey ones are still unread. **Bigger nodes have more connections.**
- 🔍 **Search** — press `Ctrl+K` (or `⌘K`) for full-text search across all notes.
- 🔎 **<a href="./semantic-search.html" data-router-ignore>Hybrid search</a>** — combines semantic similarity with BM25 keyword ranking; runs entirely in your browser (no server involved).
- 🏷️ **Tags** — every note is tagged by topic (e.g. [[tags/causal-inference]], [[tags/employee-turnover]], [[tags/psychometrics]]); tag pages collect everything on a theme.
- 🔗 **Related notes** — each note ends with its semantically closest neighbors, computed from overlapping passages across its cleaned prose rather than a truncated prefix.

Each note links back to the original blog post, where you'll find the full rendered outputs (charts, interactive apps, etc.).

## For AI agents

The whole brain is machine-readable:

- **MCP server** — add `https://people-analytics-brain-mcp.ludek-stehlik.workers.dev/mcp` as a remote MCP server (Streamable HTTP, no auth) and your agent can query the brain with `search_notes`, `get_note`, `list_notes`, and `list_tags`.
- **Plain text** — [llms.txt](./llms.txt) provides a structured index, and [llms-full.txt](./llms-full.txt) contains the complete corpus for retrieval or context loading.

## About me

I'm **Ludek Stehlik** — people analytics practitioner and psychologist. You can find me on [LinkedIn](https://www.linkedin.com/in/ludekstehlik/) or read the [source blog](https://blog-about-people-analytics.netlify.app/).
