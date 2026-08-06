---
title: Themes in Deloitte's Global Human Capital Trends between 2011 and 2023
description: Reading the latest release of Deloitte Global HC Trends made me wonder what common themes this regular series has been covering throughout its 12 years long history.
date: '2023-06-27'
tags:
- future-of-work
- generative-ai
- r
- python
original: https://blog-about-people-analytics.netlify.app/posts/2023-06-27-deloitte-hc-trends-themes/
---

Aside from satisfying a simple curiosity, it was also a good opportunity to try out a nerdy combination of various cool DS tools: openAI’s embeddings for determining trends similarity, UMAP for dimensionality reduction, DBSCAN for cluster analysis, openAI’s chat completion for cluster summarization and naming, Plotly for interactive dataviz, Shiny for dashboarding, and Python and R for orchestrating it all.

The result? The analysis revealed 13 distinct themes among the 118 specific trends:

1. Global Talent Management Strategies (23)
2. Leadership Development and Talent Management (16)
3. HR Transformation and Innovation (15)
4. Human Capital and Workforce Strategies (12)
5. Workforce Data and Analytics (10)
6. Cognitive Technologies and Workforce (8)
7. Employee-Centric Learning and Development (7)
8. Performance Management and Compensation (7)
9. Improving Employee Experience and Well-being (6)
10. Cloud Computing and HR Transformation (4)
11. Employee Engagement and Retention (4)
12. Diversity in Business Strategy (3)
13. Workplace Flexibility Strategies (3)

![](./deloitte-hc-trends-themes/plot.png)

It's no wonder I've had dejavu feelings about some trends over the years, but that's why they are called trends, because they persist over time, right? 😉

If you would like to check the analysis output interactively and in greater detail, you can use [this simple dashboard](https://lsanalytics.shinyapps.io/trendsApp/).

![](./deloitte-hc-trends-themes/dashboard.png)

<!-- RELATED:BEGIN -->
## Related notes
- [[hr-tech-ai-shift|How AI is reshaping HR-tech]]
- [[people-analytics-popularity-after-covid|The impact of the COVID pandemic on the popularity of people analytics]]
- [[siop-2026-reflection|SIOP through the wisdom of crowds: What I may have missed]]
- [[network-graph-employee-comments|Using network graph modeling to capture overarching thematic clusters in employee comments]]
- [[big-consultancies-in-the-skills-semantic-space|Big consultancies in the skills semantic space]]
<!-- RELATED:END -->

---
> 📄 Read the [original post with full outputs](https://blog-about-people-analytics.netlify.app/posts/2023-06-27-deloitte-hc-trends-themes/) on my blog.
