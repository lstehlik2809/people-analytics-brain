---
title: A way to make prediction models more precise and interpretable at the same time?
description: An interesting and potentially useful combination of causal identification algorithms and prediction modeling in the machine learning pipeline.
date: '2025-02-13'
tags:
- causal-inference
- machine-learning
- predictive-analytics
- interpretability
original: https://blog-about-people-analytics.netlify.app/posts/2025-02-13-causal-identification-and-feature-selection/
---

I just came across an interesting paper by [Ding, Zhang, & Bos (2018)](https://arxiv.org/abs/1712.07708?utm_source=chatgpt.com), who used automatic causal identification algorithms for feature selection and achieved better prediction performance with models based on these features than with models built in a more traditional way.

The authors specifically studied the experiences and choices of 3,293 visitors at a large theme park and attempted to use them to predict their Big Five personality characteristics. First, they applied two algorithms for causal identification—the [PC algorithm](https://mschauer.github.io/CausalInference.jl/latest/examples/pc_basic_examples/) and the [Fast Greedy Equivalence Search algorithm](https://github.com/juangamella/ges?tab=readme-ov-file)—to narrow down the candidate DAGs that explain the data. Then, they used the outputs from these algorithms to identify features that were causally impacted by the personality characteristic of interest. Finally, they built prediction models using only these features.

<div style="text-align:center">
![](./causal-identification-and-feature-selection/fig1.png)
</div>

The authors found that their ML pipeline, which incorporated causal identification for feature selection, outperformed baseline models in predicting individual characteristics (specifically, they used [LASSO linear regression](https://en.wikipedia.org/wiki/Lasso_(statistics))) as the baseline model, which also performs automatic feature selection). Beyond that, these models, according to the authors, provided more human-interpretable results. A win-win.

<div style="text-align:center">
![](./causal-identification-and-feature-selection/fig2.png)
</div>

For me, these results are quite surprising, as I would expect that if prediction performance were the only criterion, a purely “correlational” approach without causal constraints would perform better. I’m curious how these alleged benefits generalize to other types of situations—such as cases with less noise in the data. Definitely worth trying in one of my future projects.

Does anyone have experience with this specific approach to feature selection? Feel free to share your insights.

<!-- RELATED:BEGIN -->
## Related notes
- [[econml-and-employee-attriton|How to get causal interpretation for the Employee Attrition dataset?]]
- [[causal-impact-of-leadership-skills|Novel way to measure leadership skills via causal inference (and AI)?]]
- [[visual-diff-in-diff|Causal insights with no code?]]
- [[dag-and-double-ml|A plausible model of data-generating process eats ML algorithms for breakfast]]
- [[self-selection-and-proxy-measures|When self-selected behavior is a blessing, not a headache]]
<!-- RELATED:END -->

---
> 📄 Read the [original post with full outputs](https://blog-about-people-analytics.netlify.app/posts/2025-02-13-causal-identification-and-feature-selection/) on my blog.
