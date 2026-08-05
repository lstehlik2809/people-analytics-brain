---
title: Excel + Python = Word Document
description: Using combination of Excel and Python for semi-automatic Word document generation.
date: '2023-04-11'
tags:
- data-science
- python
- ai
original: https://blog-about-people-analytics.netlify.app/posts/2023-04-11-excel-and-python/
---

In the spirit of "Excel isn't dead and is actually doing well" posts, I'm sharing one practical example of combining Excel and Python to do one specific job. It's not as exciting and sexy as ChatGPT, but it may still come in handy for someone, as it did for one of my friends.

A friend of mine who works in psychological counselling has to write a large number of reports which, among other things, contain many recommendations for various compensations and interventions depending on established diagnosis.

To make his job easier, he created a simple Excel spreadsheet with a list of diagnoses and corresponding recommendations. He needed to generate a simple Word document listing and describing the appropriate compensations and interventions after he had marked the appropriate diagnoses for the client in Excel.  

I originally wanted to do it all in Excel, but since I'm not the best friend with VBA, I couldn't get rid of the various text formatting issues. So I reached for Python and one of its document-related libraries and linked it via macro to Excel, which acts only as a source of input data, based on which Python generates a simple report when a button is pressed in Excel. Once generated, the document is ready for further editing and tuning.

If you are interested in technical details, you can check [my GitHub page](https://github.com/lstehlik2809/Excel-and-Python-Combination-for-Document-Generation.git).  

May the Excel be with you 🙂

<!-- RELATED:BEGIN -->
## Related notes
- [[employee-feedback-analysis-using-openai|Employee feedback analysis using tools from OpenAI]]
- [[cv-job-match-career-site|Improving a company career site with tools from OpenAI]]
- [[chatgpt-emails-and-causalpy|ChatGPT as a new email writing coach?]]
- [[ai-powered-data-exploration-assistant|Testing my GenAI skepticism]]
- [[nlp-llm-and-onboarding|Using NLP & LLM to combat 'tip-of-the-tongue' moments during onboarding]]
<!-- RELATED:END -->

---
> 📄 Read the [original post with full outputs](https://blog-about-people-analytics.netlify.app/posts/2023-04-11-excel-and-python/) on my blog.
