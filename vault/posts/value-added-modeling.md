---
title: Goals saved above expected… for managers?
description: What hockey goalies can teach People Analytics about manager evaluation, context, and the dangers of high-stakes metrics.
date: '2026-05-12'
tags:
- performance-management
- people-management
- statistics
- causal-inference
- ai
original: https://blog-about-people-analytics.netlify.app/posts/2026-05-12-value-added-modeling/
---

A hockey stat sent me down a rabbit hole this weekend 🤓

It started with goalie trivia and ended with manager evaluation.

The trivia: you can't judge a goalie on save percentage alone - a goalie behind a leaky defense faces harder shots and can look worse than he is. So analysts built models that score every shot's observable difficulty - distance, angle, shot type, rebound/previous-event context, manpower, and in richer datasets, pre-shot movement - and predict the [probability it becomes a goal](https://hockey-graphs.com/2019/08/12/expected-goals-model-with-pre-shot-movement-part-1-the-model/). Sum the differences between expected and actual outcomes, and you've partially separated goalie performance from shot volume and shot quality (*[Goals Saved Above Expected](https://moneypuck.com/glossary.htm)*).

Then I learned this same basic logic has been [used in education for ~30 years](https://link.springer.com/article/10.1007/BF00973726). It's called *[Value-Added Modeling](https://www.rand.org/education-employment-infrastructure/projects/measuring-teacher-effectiveness/value-added-modeling.html)*. Predict each student's expected test score from prior achievement, demographics, peers, and other available context - then estimate the teacher effect from the remaining classroom-level difference.

The People Analytics application is obvious: strip out tenure, role, comp, market, etc. - and the residual may contain a manager effect.

Tempting, but also dangerous. What VAM taught education the hard way:️

* Single-year estimates are noisy: year-to-year [stability for individual teachers](https://files.eric.ed.gov/fulltext/ED530401.pdf) is often around 0.2-0.5, sometimes higher depending on grade, subject, and model.️
* Three years of data materially improves [reliability](https://ies.ed.gov/use-work/resource-library/report/technical-methods-report/error-rates-measuring-teacher-and-school-performance-using-value-added-models?utm_source=chatgpt.com) - patience beats better models - but it doesn't eliminate bias.️
* When test-based metrics became high-stakes, they created predictable gaming: more test prep, narrowed instruction, and in the broader test-based-accountability era, outright cheating scandals like [Atlanta](https://kappanonline.org/saultz-murphy-aronson-what-can-we-learn-from-atlanta-cheating-scandal/)`.️
* The American Statistical Association issued a [formal caution in 2014](https://www.amstat.org/asa/files/pdfs/POL-ASAVAM-Statement.pdf) about overinterpreting VAMs for high-stakes individual decisions.️
* [Houston teachers](https://journals.sagepub.com/doi/10.3102/0013189X20923046) later won a favorable due-process ruling and settlement because the proprietary model/data behind their scores could not be meaningfully challenged.

Every one of those lessons applies to manager scorecards. The model can be useful, but the governance around it is where things usually break. I can see this working for surfacing patterns, validating training programs, and allocating coaching - but going wrong at the predictable next step: using it to gate promotions or trigger PIPs on thin data, which is where many orgs will be tempted to go first, for understandable reasons.

Question for the PA folks here: Are you using "above expected" style models in PA today? For what - retention, hiring, sales, something else? If you tried and walked away, what was the deal-breaker? Sample size? Politics? Legal? The metric got gamed?

<!-- RELATED:BEGIN -->
## Related notes
- [[the-triple-filter-test|The Triple-Filter Test: How to prioritize HR interventions with panel data]]
- [[managerial-quality|Unexpected protective effect of having a good manager?]]
- [[impact-of-leaders|Want to maximize your impact as a leader?]]
- [[contagious-turnover|Is contagious turnover overrated? Probably only if you ignore the managers.]]
- [[genai-and-leadership-judgement|Can genAI help people managers lead better?]]
<!-- RELATED:END -->

---
> 📄 Read the [original post with full outputs](https://blog-about-people-analytics.netlify.app/posts/2026-05-12-value-added-modeling/) on my blog.
