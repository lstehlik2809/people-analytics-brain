---
title: My second People Analytics brain - both for people and AI agents
description: So I finally gave the “second brain” idea a try - to see how it works in practice and whether it’s actually useful.
date: '2026-07-28'
tags:
- people-analytics
- ai
- agentic-ai
- embeddings
- nlp
- knowledge-management
- data-visualization
original: https://blog-about-people-analytics.netlify.app/posts/2026-07-28-people-analytics-second-brain/
---

Specifically, I built a public knowledge base from more than 200 posts on this People Analytics blog. It is browsable as a knowledge graph, searchable by keywords or meaning, and accessible to AI agents through a public MCP server. The complete corpus is also available as `llms-full.txt` - roughly 290k tokens, so it fits in one go only in the largest context windows - plus a compact `llms.txt` index.

I used a small pipeline that converts the .Rmd sources of my blog posts into clean Markdown notes, embeds each note, and links it to its closest semantic neighbours. Post categories become topic nodes, so themes like causal inference, psychometrics or employee turnover turn into hubs in the network. The result is published with Quartz on GitHub Pages, and semantic search runs entirely in the visitor's browser (transformers.js + a small MiniLM model - no server, no API keys). The MCP server is a tiny Cloudflare Worker that fetches the published corpus at runtime and indexes it in memory, so new posts show up without redeploying it. Its tools are shaped for how agents actually work: search for candidates, triage them by snippet, then read the one or two notes that matter in full.

In this setting, it enables two ways of using it:

🧠 **Directly** - explore the graph to see how ~300 notes and topics connect, jump between them, search by keyword or by meaning, and follow the related-notes trail at the end of each note. Every note links back to the original post with the full outputs.

🤖 **Via AI agents** - add the MCP server as a connector in any MCP-capable AI client (e.g., Claude Code/Cowork, Codex/Work, Cursor, etc.) and just ask questions. The agent can search the knowledge base, retrieve the relevant full notes, and produce an answer grounded in them - with links back to the original sources. If MCP isn’t available in your preferred tool, you can instead point an LLM with a sufficiently large context window at `llms-full.txt`.

It’s too early to make any definite judgments, but so far this setup seems pretty useful for ideation, discovering connections across topics, reusing previous work instead of starting from scratch, and grounding AI-agent outputs in domain-specific knowledge that was curated independently of the agent itself 🤔  

Everything is publicly available, so feel free to give it a try for yourself
👉 https://lstehlik2809.github.io/people-analytics-second-brain

MCP endpoint, streamable HTTP, no authentication required
👉 https://people-analytics-brain-mcp.ludek-stehlik.workers.dev/mcp

GitHub repo
👉 https://github.com/lstehlik2809/people-analytics-second-brain

<object
  data="files/people_analytics_second_brain_prezi.pdf"
  type="application/pdf"
  width="100%"
  height="800px">

  <p>

    Your browser cannot display this PDF.
    <a href="files/people_analytics_second_brain_prezi.pdf" download>Download the PDF</a>.

  </p>
</object>

<p>

  <a href="files/people_analytics_second_brain_prezi.pdf" download>
    Download the PDF
  </a>

</p>

<!-- RELATED:BEGIN -->
## Related notes
- [[searching-and-querying-aihr-blog-posts|Searching & querying AIHR blog posts on People Analytics topics]]
- [[hr-tech-ai-shift|How AI is reshaping HR-tech]]
- [[agentic-ai-for-visual-data-exploration|Agentic AI for visual data exploration]]
- [[employee-feedback-analysis-using-openai|Employee feedback analysis using tools from OpenAI]]
- [[nlp-llm-and-onboarding|Using NLP & LLM to combat 'tip-of-the-tongue' moments during onboarding]]
<!-- RELATED:END -->

---
> 📄 Read the [original post with full outputs](https://blog-about-people-analytics.netlify.app/posts/2026-07-28-people-analytics-second-brain/) on my blog.
