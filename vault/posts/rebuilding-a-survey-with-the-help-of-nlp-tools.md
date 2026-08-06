---
title: Rebuilding an employee survey with the help of NLP tools
description: Using LLM and text embeddings to assist in implementing new constructs into the existing employee survey.
date: '2023-11-27'
tags:
- employee-survey
- nlp
- generative-ai
- psychometrics
original: https://blog-about-people-analytics.netlify.app/posts/2023-11-27-rebuilding-a-survey-with-the-help-of-nlp-tools/
---

Sometimes you need to incorporate a new construct into an existing employee survey, but you also don't want to burden respondents with too many items. 

One way to avoid this is to reuse existing survey items to cover all or some of the facets of the new construct of interest. When you have many items, it can be quite challenging to figure out which items might be good candidates for such reuse. However, with the new NLP tools, this is now much easier. 

To achieve this, in one of my projects, I combined a prompt requesting the LLM to semantically compare all existing items and facets of a new construct with a semantic similarity comparison of the two using text embeddings. Both approaches provided me with a pre-selected list of promising candidate items, which I then evaluated myself.

This way, I significantly reduced the time it takes to figure out which items I can reuse and which I'll have to write from scratch. But LLM can help with that, too - see, for example, this [article from Hernandez & Nie (2022)](https://onlinelibrary.wiley.com/doi/10.1111/peps.12543).
 
I know this use case is not that common, but IMO still enough to make it worth knowing that this option exists. Happy prompting and cosine similarity computing 🖖

<!-- RELATED:BEGIN -->
## Related notes
- [[nlp-llm-and-onboarding|Using NLP & LLM to combat 'tip-of-the-tongue' moments during onboarding]]
- [[employee-feedback-analysis-using-openai|Employee feedback analysis using tools from OpenAI]]
- [[chatgpt-and-employee-feedback|Using ChatGPT to summarize and explore employee feedback?]]
- [[linkedin-contacts-job-positions|Analyzing LinkedIn connections' jobs using LLMs and the BERTopic package]]
- [[network-graph-employee-comments|Using network graph modeling to capture overarching thematic clusters in employee comments]]
<!-- RELATED:END -->

---
> 📄 Read the [original post with full outputs](https://blog-about-people-analytics.netlify.app/posts/2023-11-27-rebuilding-a-survey-with-the-help-of-nlp-tools/) on my blog.
