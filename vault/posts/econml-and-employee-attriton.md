---
title: How to get causal interpretation for the Employee Attrition dataset?
description: An interesting demonstration of causal inference in the People Analytics space using the famous IBM Employee Attrition dataset.
date: '2025-03-18'
tags:
- causal-inference
- python
- employee-turnover
original: https://blog-about-people-analytics.netlify.app/posts/2025-03-18-econml-and-employee-attriton/
---

To be honest, whenever I see an analysis using the popular [IBM Employee Attrition dataset](https://www.kaggle.com/datasets/pavansubhasht/ibm-hr-analytics-attrition-dataset), I tend to ignore it and quickly skip to something more interesting and engaging. A classic search for shiny new things in action. 😉

Btw, did you know this dataset has already been with us for about 10 years? Pretty nice milestone anniversary! At least, that's what my OpenAI deep research found—it seems it was first released by IBM around September 2015 on its blog to showcase the IBM Watson Analytics platform's capabilities in an HR context. So, please take this finding with a grain of salt. However, after checking the sources (including my own memory), it seems pretty plausible to me. But feel free to correct me/us if I’m/we’re wrong.

Recently, however, I broke this habit when I came across a [Jupyter notebook on EconML’s GitHub](https://github.com/py-why/EconML/blob/main/notebooks/Solutions/Causal%20Interpretation%20for%20Employee%20Attrition%20Dataset.ipynb) showcasing how to effectively combine classical ML—providing a list of strongest predictors—with their subsequent causal interpretation using [Double ML (DML)](https://docs.doubleml.org/stable/index.html) and [Heterogeneous Treatment Effect (HTE)](https://www.sciencedirect.com/science/article/pii/S0049089X22001211) estimation, nicely packaged into the [CausalAnalysis class](https://econml.azurewebsites.net/_autosummary/econml.solutions.causal_analysis.CausalAnalysis.html).

The entire pipeline includes the following steps:

1. Fine-tuning and training a traditional ML model.
2. Using [SHAP values](https://shap.readthedocs.io/en/latest/index.html) for correlation interpretation of the results, identifying the top predictors highlighted by the ML model.
3. Employing DML combined with HTE to test whether these top predictors actually have a direct causal effect on attrition. While these may be strong predictors of employee departure, they don't necessarily drive employees to leave.
4. Using the HTE component for employee segmentation by specific risk factors, enabling individualized plans to reduce attrition. For instance, salary might have a higher causal impact on shorter-tenured employees, whereas overtime could show the opposite pattern.
5. Finally, cohort analysis, enabling assessment of causal effects of selected factors on new datasets, even down to the individual employee level.

<div style="text-align:center">
![](./econml-and-employee-attriton/causal_effect_chart_combo.png)
</div>

IMO, pretty cool stuff. It seems we indeed live not only in an AI revolution but also in a causal one ✊🙂

⚠️ Just a small (or big?) warning at the end: Despite the smooth and easy analytical workflow enabled by the CausalAnalysis class, it doesn't replace the need for strong domain knowledge and understanding which variables make sense to include in the model in the first place.

<!-- RELATED:BEGIN -->
## Related notes
- [[visual-diff-in-diff|Causal insights with no code?]]
- [[dag-and-double-ml|A plausible model of data-generating process eats ML algorithms for breakfast]]
- [[causal-identification-and-feature-selection|A way to make prediction models more precise and interpretable at the same time?]]
- [[interpretable-ml|Interpretable machine learning with modelStudio]]
- [[encouragement-design-and-ivs|Encouragement Design using instrumental variables]]
<!-- RELATED:END -->

---
> 📄 Read the [original post with full outputs](https://blog-about-people-analytics.netlify.app/posts/2025-03-18-econml-and-employee-attriton/) on my blog.
