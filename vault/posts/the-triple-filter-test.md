---
title: 'The Triple-Filter Test: How to prioritize HR interventions with panel data'
description: About a data-driven framework for prioritizing HR interventions with limited budget.
date: '2026-02-12'
tags:
- evidence-based-management
- panel-data
- employee-survey
- causal-inference
original: https://blog-about-people-analytics.netlify.app/posts/2026-02-12-the-triple-filter-test/
---

As People Analytics practitioners, we’re often asked: “*Which lever should we pull to drive engagement, retention, productivity… [fill in your favorite outcome]?*”

[Recently](https://blog-about-people-analytics.netlify.app/posts/2025-10-21-cross-lagged-panel-modeling/), I shared how RI-CLPM (*Random Intercept Cross-Lagged Panel Models*) can move us beyond simple correlations by using survey data collected over time to separate stable differences from within-person change. As I’ve gone deeper into the model’s mechanics, I’ve realized it can help not only with identifying potential “drivers,” but also with prioritizing where to spend budget - as long as we’re careful about what the model can and can’t claim and we interpret results in the context of business strategy.

<div style="text-align:center">
![](./the-triple-filter-test/ri_clpm_scheme_full.png)
</div>

Here’s the approach I’m experimenting with: applying a triple filter to every relevant survey variable before recommending action.

### 1) The Asymmetry Test (The “Direction” Filter) 
We should prioritize levers where the effect from the Lever in period 1 to the Outcome in period 2 is meaningfully stronger than the reverse. But I don’t treat this as a simple yes/no gate. The degree of asymmetry can be used as a weighting signal: a lever with a moderate effect but strong directional dominance can outrank one with a larger effect that appears equally bidirectional.

The Logic: If “Manager Support” this quarter predicts next quarter’s “Productivity” more than the reverse pathway does, that pattern is more consistent with a directional influence in the within-person dynamics - and it may be a better candidate for intervention testing.
Important Caveat: Asymmetry is suggestive, not definitive. Time-varying confounds (reorgs, comp changes, manager changes), measurement issues, and differences in reliability can still produce apparent directionality. So I treat this as “where to place bets and run tests,” not “proof of causality.”

The Goal: Stop over-investing in ambiguous feedback loops where the direction is unclear, and rank the candidates you do find by how strongly directional the within-person dynamics appear.

### 2) The Malleability Filter (The “Inertia vs. Flux” Filter) 
In RI-CLPM, we separate stable differences across people/contexts (the between-person component) from within-person fluctuations over time (the part that moves relative to someone’s own baseline). The ratio of within-person variance to total variance tells us how much of a variable’s movement is actually “in play” for change efforts.

The Logic: If most variance in a variable sits in the stable component, we have evidence of Contextual Inertia. This often reflects stable structural factors like personality, role design, team composition, manager assignment, or baseline culture. The key point is: individual training is often the wrong tool when the signal is dominated by Contextual Inertia.

The Goal: Avoid spending intervention budget on variables where the "system" creates too much drag for individual-level programs to succeed. This filter answers: Is there enough within-person signal to work with - or are we fighting structural gravity?

### 3) The Autoregressive Check (The “Lift vs. Maintenance” Filter) 
This filter goes one level deeper: of the within-person fluctuation that exists, how strongly does it carry forward from year to year?

The Logic: Autoregression tells you the intervention economics (stickiness).

**High Stickiness (High Persistence)**: Changes tend to endure; the decay rate is slow. This is where structural, high-dose upfront interventions can have a durable payoff.

**Low Stickiness (Low Persistence)**: Deviations reset toward baseline quickly. These are “leaky bucket” variables - best suited for continuous/pulse-style reinforcement rather than one-off programs.

Example: Perceived growth opportunities can fluctuate across people and time (it looks malleable). But if negative deviations strongly persist year over year, a standalone career workshop is unlikely to break the pattern. You may need structural changes: clearer mobility paths, internal marketplace design, manager incentives, or staffing processes. Conversely, a metric with low persistence might respond quickly to a nudge - just don’t expect it to last without ongoing reinforcement.

The Goal: Match the intervention design to the dynamic: decide whether you’re signing up for a heavy lift with long persistence or a lighter lift with ongoing maintenance. This filter answers: Is this a “move it once and it sticks” lever, or a “keep watering it” lever?

### The “Structural Pivot”
Here’s the counter-intuitive part: what looks like a “failure” for an L&D team can be a gold mine for Talent Acquisition or Org Design.

If analysis suggests a factor has high directional association with performance (Filter 1) but is dominated by Contextual Inertia (Filter 2), stop trying to force-fit it into a training program. You are likely hitting a structural constraint, not a skill gap. This means the driver is better addressed via structural levers: selection, placement, role design, manager assignment, or team composition.

In some cases, the fix is Who: “Hire for this trait” or “Staff for this mix.” In other cases, the fix is Where: “Redesign the role” or “Build the environment where this behavior naturally emerges.” Either way, you’ve learned something valuable: this lever is not a target for individual interventions, but it is critical for how you staff and structure the work.

❓ I'm curious: Does this approach make sense to you? Do I read too much from the model? Does anyone here systematically use criteria like these when prioritizing actions based on survey panel data? If you do, what’s your rubric - and what pitfalls have you run into (e.g., time-varying confounds, survey changes, cadence issues)?

<!-- RELATED:BEGIN -->
## Related notes
- [[cross-lagged-panel-modeling|Getting (more) causal insights from employee survey data (without an RCT)]]
- [[did-with-repeated-cross-sectional-data|What a European cigarette tax study taught me about employee listening]]
- [[encouragement-design-and-ivs|Encouragement Design using instrumental variables]]
- [[you-said-we-did|‘You Said, We Did’ matters - maybe just not as distinctly as we assume]]
- [[visual-diff-in-diff|Causal insights with no code?]]
<!-- RELATED:END -->

---
> 📄 Read the [original post with full outputs](https://blog-about-people-analytics.netlify.app/posts/2026-02-12-the-triple-filter-test/) on my blog.
