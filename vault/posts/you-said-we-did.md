---
title: ‘You Said, We Did’ matters - maybe just not as distinctly as we assume
description: A brief look at whether perceived responsiveness to employee feedback really predicts future survey participation - or mostly rides along with general engagement.
date: '2026-07-07'
tags:
- employee-survey
- employee-engagement
- employee-experience
- employee-listening
- survey-participation
- regression-analysis
- psychometrics
- statistics
original: https://blog-about-people-analytics.netlify.app/posts/2026-07-07-you-said-we-did/
---

If there is one piece of widely accepted wisdom in the employee listening space, it is this: *organizations need to respond visibly and credibly to employee input, or employees will eventually stop giving it*.

That claim is repeated so often that it almost reads as self-evident. Still, I wanted to see how far it would hold up against real data.

One imperfect, but still directionally informative, way to examine this is to ask whether employees’ prior-year survey responses predict participation in the following year’s engagement survey among continuing employees who had responded previously.

I approached that question in two steps.

In the primary analysis, I used a raw prior-year survey item reflecting employees’ belief that their input would lead to a visible organizational response, together with common demographic and organizational covariates, to predict next-year survey participation. This provides the more substantively direct test of the practical wisdom itself: whether employees who believed their input would go somewhere were more likely to participate again the following year.

In the secondary analysis, I took a narrower decomposition approach. For each survey item, I residualized it against a leave-one-item-out one-factor model estimated from the other survey items, using the complete-case subset required for that factor step and an organizational-cluster bootstrap to reflect uncertainty from both parts of the residualization-and-modeling pipeline. In practical terms, the secondary predictor captures the item-specific residual signal: whether an employee scored that item higher or lower than would be expected from their broader response pattern across the rest of the survey. That second specification is not a stronger causal design; it is a more specific shared-versus-residual signal test.

The contrast between the two analyses is where things become interesting.

In the primary model, the focal responsiveness item is clearly positively associated with next-year participation. Employees who scored higher on that item were more likely to respond again the following year, even after adjustment for standard demographic and organizational covariates. The association was statistically detectable but modest in size, so I would read it as evidence of a repeat-participation pattern rather than a large practical shift (one possible positive interpretation being that lower perceived responsiveness does not appear to translate into broad withdrawal from the survey as a channel for voice). At a broad level, the data are therefore consistent with the conventional wisdom.

<div style="text-align:center">

![](./you-said-we-did/pic1.png)

</div>
*Fig. 1: Average marginal effects from the primary model predicting next-year survey participation from prior-year survey items. Items are anonymized for public sharing; Action Taken Item is the focal perceived-responsiveness item. Horizontal bars show 95% confidence intervals.*

At the same time, that item was not the strongest item-level predictor in the raw analysis. Several other item scales measuring specific aspects of the employee experience appeared more strongly linked to repeat participation. That matters, because it suggests that future participation is not most tightly linked to a single responsiveness signal in isolation. It may be more strongly tied to a wider set of experiences that collectively shape whether employees remain willing to re-engage.

And the secondary model sharpens that point further.

Once the shared general engagement factor is removed, the focal responsiveness item no longer stands out as a distinct residual predictor. Its residual association is essentially null. By contrast, some other item-specific residual signals continued to show clearer associations with repeat participation.

<div style="text-align:center">

![](./you-said-we-did/pic2.png)

</div>
*Fig. 2: Average marginal effects from the secondary residual-signal model, where each item is adjusted for the broader survey-response pattern using a leave-one-item-out factor approach. Items use the same anonymized labels as in the primary chart; Action Taken Item is the focal perceived-responsiveness item. Horizontal bars show 95% cluster-bootstrap confidence intervals.*

That difference in findings changes the interpretation. If we stop at the primary model, the story is straightforward: employees who believe in some visible response to their input are more likely to participate again the next year. But once we compare the primary and secondary analyses, a more nuanced picture emerges. Much of the predictive association attached to that item appears to be shared with the broader employee-experience response pattern with which it co-moves, rather than providing clearly distinct incremental predictive information. In other words, perceived responsiveness still matters descriptively, but it appears less distinctive as a standalone predictive signal once its shared variation with the broader engagement-related survey pattern is removed.

That, to me, is the deeper insight. The practical takeaway is not that visible response is unimportant. It is that organizations may overstate its uniqueness. If the goal is to sustain future participation, the stronger predictive signals may sit less in any single “you said, we did” item and more in the broader relational and organizational environment - or in other common factors reflected across employees’ survey responses.

A final caveat is important. Neither analysis is causal. These are observational, associational models of repeat participation among continuing employees, based on a single year-over-year transition rather than a longer longitudinal window. They are not estimates of whether actual organizational responsiveness causes future survey participation.

Still, even with these limitations, I think the comparison is useful. The primary analysis captures the total predictive signal attached to perceived responsiveness. The secondary analysis asks whether the item adds predictive information beyond the dominant common pattern reflected in the rest of the survey. Taken together, they suggest a more disciplined version of the standard wisdom: responsiveness likely matters, but much of its observed predictive association may be shared with the wider organizational context, general engagement, response tendencies, or related features of how employees experience the survey process.

For many people working in employee listening, this may not be so surprising. But it’s still useful to see the pattern show up in the data 😉

Curious if anyone has done a similar exercise, and with what results.

<!-- RELATED:BEGIN -->
## Related notes
- [[probability-of-comments-in-a-survey|What makes people more likely to comment on a question in an employee survey?]]
- [[honesty-in-engagement-vs-exit-surveys|Are people during exit surveys more honest in their responses than in engagement surveys?]]
- [[glassdoor|When flawed statistical & causal reasoning leads to a valid conclusion anyway]]
- [[psw-and-selection-bias-in-employee-surveys|How to analyze employee survey results with less (selection) bias?]]
- [[cross-lagged-panel-modeling|Getting (more) causal insights from employee survey data (without an RCT)]]
<!-- RELATED:END -->

---
> 📄 Read the [original post with full outputs](https://blog-about-people-analytics.netlify.app/posts/2026-07-07-you-said-we-did/) on my blog.
