---
title: Dimensional Traits vs. Personality Types
description: Sharing an interactive dataviz showing why cramming the complexity of personality into a few types just doesn’t work.
date: '2025-09-09'
tags:
- personality
- big-five
- machine-learning
- psychometrics
original: https://blog-about-people-analytics.netlify.app/posts/2025-09-09-dimensional-traits-vs-personality-types/
---

For a guest lecture I’m giving on personality in the business world, I built a [simple interactive dataviz](https://sanofi-people-analytics.shinyapps.io/personality-mapping/) that clearly demonstrates just how futile (and a bit naïve) it is to try to squeeze the huge variability of personality characteristics into a handful of types like… [insert your favorite typology 😉].

The dashboard uses a random sample of 10k Big Five profiles from [Johnson’s IPIP-NEO-300 dataset](https://osf.io/wxvth/files/osfstorage). With a 3D scatter plot, profile line chart, UMAP dimensionality reduction, and the HDBSCAN clustering algorithm, it shows that even when groups of people with similar profiles do appear—and are large enough to matter (say, at least 1% of the population)—they still show pretty high within-group variability. On top of that, a big chunk (actually, the majority) of profiles can’t be assigned to any stable cluster at all, ending up as “noise” points in HDBSCAN’s terms.

<div style="text-align:center">
![](./dimensional-traits-vs-personality-types/interactive_dataviz.gif)
</div>

If you find it useful for your teaching or training, check out the dataviz [here](https://sanofi-people-analytics.shinyapps.io/personality-mapping/). If you want to download the data and code to run it locally, take a look at [this GitHub repo](https://github.com/lstehlik2809/personality-mapping.git).

<!-- RELATED:BEGIN -->
## Related notes
- [[team-maps|Experiencing and seeing team similarities and differences]]
- [[detecting-personality-in-the-face|Can a simple algorithm read your personality from your face?]]
- [[personality-and-non-linearities|Nonlinear relationships between personality traits and business outcomes seem to be the norm rather than the exception]]
- [[job-personality-fit|Do people’s personalities vary across different jobs?]]
- [[kohonen-self-organizing-maps|Kohonen's Self-Organizing Maps]]
<!-- RELATED:END -->

---
> 📄 Read the [original post with full outputs](https://blog-about-people-analytics.netlify.app/posts/2025-09-09-dimensional-traits-vs-personality-types/) on my blog.
