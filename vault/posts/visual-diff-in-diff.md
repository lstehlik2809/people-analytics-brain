---
title: Causal insights with no code?
description: Causal insights without writing a single line of code? Well… maybe. In this post, I walk through how a simplified, visual version of a method called difference-in-differences can help you better understand cause and effect—even if you're not a data scientist. Using just a BI tool and some domain knowledge, you can sometimes identify meaningful patterns that suggest whether a policy or change truly made a difference. It's not perfect, and it won't replace rigorous analysis—but in the right context, it can be a surprisingly useful starting point.
date: '2025-04-15'
tags:
- data-science
- causal-inference
- difference-in-differences
- people-analytics
- evidence-based-management
original: https://blog-about-people-analytics.netlify.app/posts/2025-04-15-visual-diff-in-diff/
---

If there’s one causal inference method that is both intuitive and easy to explain—even to non-data folks—it’s difference-in-differences (DiD).

For those who haven’t come across it yet: DiD compares how things change over time for a group affected by an intervention (the treatment group) versus one that isn’t (the control group). The key assumption is that both groups would have followed similar trends if the intervention hadn’t occurred. This can be partially validated by checking whether their trends were similar *before* the change. If that holds, and we observe a notable shift in the treatment group *after* the intervention—beyond the usual trend—we can reasonably attribute the difference to the intervention.

Besides the “parallel trends” assumption, there are a few other important ones—like no spillover effects, no simultaneous interventions, common shocks, and stable group composition—but these can usually be assessed with solid domain knowledge.

Given the intuitive nature of DiD, even those who don’t work with data every day—like HRBPs and similar roles—can, IMO, apply a lighter, visual version of this method on their own in BI tools like Tableau, Power BI, or—specifically for people analytics—platforms like Visier or OneModel.

As an example, check out the chart below. It was created in one of those BI platforms just by picking a relevant metric and filtering for the right departments and time period. It shows the trailing 12-month voluntary attrition rate for two departments—only one of which was supposed to be affected by a policy change, based on the nature of their work. Before the policy change, Department A had slightly higher attrition than Department B, but both were trending downward in parallel. After the change, the trend diverged sharply: attrition in Department B went up, while it continued downward in Department A. If we can reasonably confirm the other DiD assumptions, this gives us pretty solid evidence that the policy change caused the increase in attrition in Department B.

<div style="text-align:center">

![](./visual-diff-in-diff/plot2.png)

</div>

I'm definitely not saying this lighter version of DiD is a silver bullet for all causal questions in people analytics—especially since it depends on specific quasi-experimental setups, like the one shown above, and doesn’t deal with the uncertainty present in the data. That said, IMO, it can still help non-technical folks handle some of the lower-stakes cases on their own, giving data science teams more room to focus on the big stuff. 

What do you think? Could this be a useful piece of the puzzle in boosting data literacy among HR professionals? Do you see any substantial risks?

<!-- RELATED:BEGIN -->
## Related notes
- [[causal-inference-in-people-analytics|Beyond prediction: Exploiting organizational events for causal inference in people analytics]]
- [[app-piloting-and-dif|Estimating the impact of a new business app by piloting & method of difference-in-differences]]
- [[did-with-repeated-cross-sectional-data|What a European cigarette tax study taught me about employee listening]]
- [[econml-and-employee-attriton|How to get causal interpretation for the Employee Attrition dataset?]]
- [[cross-lagged-panel-modeling|Getting (more) causal insights from employee survey data (without an RCT)]]
<!-- RELATED:END -->

---
> 📄 Read the [original post with full outputs](https://blog-about-people-analytics.netlify.app/posts/2025-04-15-visual-diff-in-diff/) on my blog.
