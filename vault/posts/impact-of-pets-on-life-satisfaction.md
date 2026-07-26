---
title: Before you believe the £70,000 cat
description: A brief causal sanity check of the £70,000 cat claim - and a reminder that sophisticated methods still depend on believable assumptions.
date: '2026-06-14'
tags:
- causal-inference
- research-methods
- critical-thinking
original: https://blog-about-people-analytics.netlify.app/posts/2026-06-14-impact-of-pets-on-life-satisfaction/
---

We are about to get a cat for our son, so it is no big surprise that the Internet started feeding us more information about pets even without being asked. Normal stuff in the algorithmic age, I suppose.

One of these pieces was [a 2025 paper on the benefits of having a pet for life satisfaction](https://link.springer.com/article/10.1007/s11205-025-03574-1). The headline claim was huge: in the main estimates, **having a dog or cat is worth 3 to 4 points on a 1–7 self-reported life satisfaction scale**, and **around £70,000 per year in life-satisfaction-equivalent income**.

Of course, this looked like excellent evidence for my son’s lobbying campaign. But not so fast.

Here is the thing I actually want to share, and it has very little to do with pets. Most of us will never re-run a study's regressions. But all of us can train the instinct that fires before we believe a number - the same instinct that kicks in when a too-good-to-be-true email lands in your inbox. That instinct is worth more than any single statistical method. So let me walk through it, using one cat as the worked example.

**First instinct: is the effect even physically plausible?** A 3-4 point move on a 1-7 scale is not "pets make people a bit happier." It is closer to moving someone from "quite dissatisfied" to "almost completely satisfied." The scale is only six points wide. An effect that large, as an average, would push people off the top of the ruler. That alone should slow you down.

**Second instinct: is it bigger than things we already know are big?** In the authors' own IV models, the estimated pet effect is larger, in absolute size, than the effect of their poor-mental-health indicator. That does not make it impossible. But when a cat appears to matter more than mental health, you check the wiring.

Now, to be fair, the authors earned a closer look. They did not simply correlate pet ownership with happiness - they knew that was a trap. Happier people might be more likely to get pets. Or lonelier, less satisfied people might get pets to cope. The direction of causality is genuinely not obvious. To deal with this, they used an **instrumental-variable design**. Their instrument was whether people watch over their neighbors' property when the neighbor is away. The rough idea: people who help neighbors may also be exposed to neighbors' pets, and that exposure may nudge them into getting a pet themselves. That is clever. It is also where the problem begins.

For an instrument to work, it has to meet a demanding condition: it should affect life satisfaction **only through pet ownership**. In plain English, "watching over neighbors' property" should make you happier only because it makes you more likely to own a pet. That seems hard to believe. People who watch over neighbors' property are probably different in other ways too. They may live in more trusting neighborhoods, have stronger social ties, be more helpful, be more embedded in their community, or simply have better relationships with the people around them. Any of these could lift life satisfaction directly. So the instrument may be picking up **social capital**, not only pets. The authors are aware of this and try to control for neighborhood cohesion. That helps, but it does not close the hole. "Do you live in a close-knit neighborhood?" is a rough proxy for the deeper reality of being trusted, connected, useful, and supported.

There is a second issue, and it is the one that turns a small flaw into a big number. The instrument predicts pet ownership, **but not very strongly**. Switching it on raises the likelihood of owning a cat by only about 4 percentage points, and a dog by about 5. Statistically significant, yes. Substantively small. Why does that matter? Because IV estimates work by dividing the outcome shift by the treatment shift. If the treatment shift is tiny, even a small amount of contamination in the instrument gets divided by something close to zero. That is how **a small leak becomes a huge estimated effect**. More precisely: a weak first stage makes the IV estimate fragile; if the instrument also leaks even a little bit of social capital, that leak gets scaled up by the tiny treatment shift. The two flaws do not simply add - they **multiply**.

Which brings me to the loudest alarm of all. In the raw data, pet owners are actually slightly less satisfied than non-owners. In the OLS regression, pets have basically no relationship with life satisfaction. Only after the instrument is applied does the estimate **flip sign and explode** into a large positive effect of 3 to 4 points. When a method reverses the direction of the raw result and inflates it this dramatically, the professional default should be "**maybe the instrument is broken**," not "we found a hidden causal truth."

And the £70,000 is more fragile still, because it is not observed at all. It is **a ratio**: the estimated pet effect divided by the estimated income effect. If either piece is shaky, the price tag is shaky too.

To be clear: **I am not arguing that pets do nothing**. They probably help many people - routine, affection, touch, purpose, social contact, and, for dogs, exercise. I am very open to the idea that pets improve wellbeing. My point is narrower. The paper is interesting and far more thoughtful than a simple correlation study, but **the headline effect is probably too large to take literally** - even within the narrow subgroup the IV is trying to describe: people whose pet ownership is nudged by watching over neighbors’ property.

None of this required redoing anyone’s statistics. It only required a straightforward causal sanity check: **Is the effect plausible? Is the comparison clean? What else could be driving it? Is the key assumption believable?** And then, sadly, resisting the temptation to use the £70,000 cat as scientific cover for surrendering to my son’s lobbying campaign 😉

P.S. For our household, the causal model is simpler: *Child wants cat → parents eventually surrender → cat becomes true treatment condition*. Effect size still unknown. Expected purring coefficient positive 😻

<!-- RELATED:BEGIN -->
## Related notes
- [[systematic-review-of-happiness-interventions|What actually makes us happier?]]
- [[happiness-and-income|Happy today, richer tomorrow?]]
- [[nudge-effectiveness|Signal vs. Noise: Why we can’t yet identify effective nudges]]
- [[did-with-repeated-cross-sectional-data|What a European cigarette tax study taught me about employee listening]]
- [[ai-and-bullshit-asymmetry|Can AI help us fight the bullshit asymmetry?]]
<!-- RELATED:END -->

---
> 📄 Read the [original post with full outputs](https://blog-about-people-analytics.netlify.app/posts/2026-06-14-impact-of-pets-on-life-satisfaction/) on my blog.
