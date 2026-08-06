---
title: Conspiracy theories as a specific example of overfitting?
description: An interesting perspective on the nature of conspiracy theories, in the spirit of the book 'Algorithms to Live By' from Brian Christian and Tom Griffiths.
date: '2025-09-29'
tags:
- cognitive-science
- data-science
- critical-thinking
- well-being
original: https://blog-about-people-analytics.netlify.app/posts/2025-09-29-conspiracy-theories-and-overfitting/
---

I came across this idea when reading another great book, [*A Trick of the Mind*](https://www.amazon.com/Trick-Mind-Brain-Invents-Reality/dp/1538725207) by Daniel Yon.

One currently popular [conception of mind](https://en.wikipedia.org/wiki/Bayesian_approaches_to_brain_function) treats human experience as a result of (Bayesian) combination of higher-level world models and lower-level incoming information originating from the world around us, the former trying to predict the latter, with errors leading to model adjustments and better future predictions.

But when people try to reconcile existing world models with new incoming data, they must decide what they will give bigger weight. Is contradictory new data just a random fluke that doesn’t invalidate existing beliefs or is it something that should lead us to come up with new models that will better fit the world around us? You can imagine that a bad decision in this respect can quickly lead to crazy beliefs trying to explain each random fluke or, on the other hand, to a fixed mind that fails to adapt to new information and circumstances.

There is experimental evidence that when making this decision, people take into account (meta)information about how uncertain, volatile, and unpredictable the world around them is. The more predictable it is, the more weight is given to existing beliefs, and the more volatile and unpredictable, the more weight is given to new incoming information, which is a rational way to combine these two, as we should lean more toward updating our world models when the world is in flux and likely to change.

However, what if situational circumstances or biological predispositions lead you to believe that the world around you is uncertain and unpredictable? In that case, you can end up with very peculiar theories, as each data point loudly calls for revision of existing beliefs. There is some evidence that this can really happen:

1. [Suthaharan et al. (2021)](https://www.nature.com/articles/s41562-021-01176-8?utm_source=chatgpt.com) found that during the COVID-19 pandemic, paranoia among the study participants increased and was linked to more erratic belief updating in experimental tasks. People with higher paranoia tended to treat the world as unstable — a bias also associated with greater endorsement of conspiracy theories.
2. [Browning et al. (2015)](https://www.nature.com/articles/nn.3961) showed that anxious individuals struggled to adapt their learning to the stability of the environment. Instead of learning slowly in predictable settings and quickly in volatile ones, they showed a more rigid learning style, failing to make this crucial adjustment between different contexts.

From this perspective, eccentric conspiracy theories are a specific example of overfitting when we give too much weight to random noise in the world. Thinking now what we could get from this insight. In data science, we fight overfitting usually with regularization, decreasing learning rate, model simplification, cross-validation, ensembling models, feature selection & engineering, getting more and better data, noise injection to inputs or model parameters. Can there be analogs of some of these techniques that could be used in the case of human cognition? Or am I pushing the analogy too far?

P.S. This is also a topic close to me personally. In my Ph.D. dissertation, I looked at whether human thinking is truly irrational or whether it just sometimes looks that way. Using Bayesian models, I studied how people interpret coincidences: do they dismiss them as random noise, or take them as evidence for hidden causes? What I found is that people often follow rational principles, but the “dials” of the system can be miscalibrated. I also explored how these miscalibrations are linked to dispositional factors (like stable personality traits or cognitive styles) and situational factors (like how comprehensible or uncertain the context feels). For example, if someone consistently overestimates the prior plausibility of hidden causes, coincidences easily turn into superstitions. Conspiracy theories, in this light, can be seen as the same kind of miscalibration — not irrationality in the sense of broken reasoning, but an overfitting problem, where too much weight is given to noise in the environment.

<!-- RELATED:BEGIN -->
## Related notes
- [[trust-errors-learning-reflection|When to forgive, when to close the book]]
- [[ai-and-bullshit-asymmetry|Can AI help us fight the bullshit asymmetry?]]
- [[latent-class-analysis|Latent Class Analysis of responses from employee surveys]]
- [[matthew-effect-and-success-stories|Luck, cutoffs, and the stories we tell about success]]
- [[job-fit|Are you crazy enough and in the right way to fit the craziness required by your job?]]
<!-- RELATED:END -->

---
> 📄 Read the [original post with full outputs](https://blog-about-people-analytics.netlify.app/posts/2025-09-29-conspiracy-theories-and-overfitting/) on my blog.
