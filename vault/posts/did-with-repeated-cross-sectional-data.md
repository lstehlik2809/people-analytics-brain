---
title: What a European cigarette tax study taught me about employee listening
description: Why our new pulse architecture isn't a methodological downgrade, and what Difference-in-Differences with Double Machine Learning has to do with it.
date: '2026-04-15'
tags:
- causal-inference
- panel-data
- employee-survey
- difference-in-differences
- double-machine-learning
original: https://blog-about-people-analytics.netlify.app/posts/2026-04-15-did-with-repeated-cross-sectional-data/
---

Recently, a LinkedIn recommendation algo brought a [working paper](https://arxiv.org/abs/2604.05841) by Stoller and Huber (April 2026) to my feed. It's a Difference-in-Differences study estimating how cigarette tax increases affected smoking rates across 27 EU countries between 2012 and 2020. The topic was outside my day job at Sanofi. The methodology wasn't. By the second read, I was redrawing how we should think about impact evaluation in our employee listening architecture.

Here's why a tobacco policy paper belongs on the reading list of I/O psychologists working with modern pulse survey data.

## The paper, and the part that matters for us

Stoller and Huber use Eurobarometer survey waves (repeated cross-sections, meaning *different* individuals in each wave) and compare smoking rates in countries that experienced a large cigarette tax increase against countries with stable taxes. They find tax increases reduced smoking by roughly 3.4 percentage points, concentrated in the 15–24 age group.

The substantive finding isn't the point. The methodological anchor is: they use an estimator proposed by [Zimmert (2020)](https://arxiv.org/abs/1809.01643), called **DiDDML** (Difference-in-Differences with Double Machine Learning), built specifically for repeated cross-sections. It combines:

- A DiD identification strategy (treated units vs. control units, pre- vs. post-period)
- Machine learning (random forests, lasso, or gradient boosting) to model confounding relationships flexibly
- Cross-fitting to avoid overfitting
- A doubly robust, Neyman-orthogonal score function that tolerates moderate errors in the ML step

In one sentence: it's a causal estimator purpose-built for data where you can't follow the same people over time, but you do have covariates, unit-level group structure, and time.

## Why this speaks to our listening architecture

Many organizations, ours included, are shifting to:

- **One larger annual census** (broad, deep, benchmark-quality)
- **Smaller quarterly pulses** (faster, more focused)
- **Random, partially overlapping samples** in the pulses, often anonymous

For I/O psychologists, the trade-offs are familiar. We lose individual-level longitudinal tracking. No more cross-lagged panel models on individuals. No more within-person growth trajectories on engagement. What we gain is cadence, lower respondent burden, and honest anonymous responding.

What I hadn't appreciated until reading this paper: **our new pulse architecture is structurally identical to the Eurobarometer data.** Repeated cross-sections with stable unit identifiers (teams, business units, countries), a covariate set, and time. That means there's an off-the-shelf estimator designed for exactly our data structure, with a maintained open-source implementation ([`causalweight::didDML`](https://cran.r-project.org/package=causalweight) in R, plus related methods in Python via [`DoubleML`](https://docs.doubleml.org/) and [`EconML`](https://github.com/py-why/EconML)).

That reframes what impact evaluation can look like for us.

## What counts as an "event"

Anyone in people analytics faces the same question constantly: *did that thing we did work?* With a DiD design, credible answers become possible whenever an event hits some units at a known time and leaves others unaffected:

- **Reorganizations** that roll out unevenly across functions or regions
- **Return-to-office or hybrid policy changes** applied differently across geographies
- **New manager transitions** in some teams but not others
- **Compensation or benefits changes** affecting specific job families
- **Leadership changes** in certain functions or BUs
- **Wellbeing or DEI program rollouts** staggered across the organization
- **Layoff announcements** in specific units (the impact we most want to measure and least want to confront)
- **Performance management system pilots** introduced in a subset of units before being scaled

The common thread: a discrete event, a known date, treated units, and untreated units. That's a natural experiment, and it's exactly the structure DiD (including modern variants that handle staggered rollouts) is built for.

## Three lessons I'm carrying over from the paper

### 1. Binary treatments beat continuous ones for discrete events

The paper's most striking internal finding has nothing to do with tobacco. When they compare a binary treatment specification ("did a large tax increase occur, yes or no") against a continuous specification ("what's the absolute tax share"), **the continuous version attenuates the estimated effect by more than half on the same data.** The linearity assumption (that each marginal unit of treatment has the same effect across the entire range) is rarely defensible for real-world events.

For us, this is liberating. An RTO mandate is binary for a given unit. A new manager either started or didn't. A reorg either landed or didn't. Stop trying to scale treatments into continuous regressors. Define the event as binary, define pre- and post-periods, define treated and control units, and run the analysis on a restricted sample.

### 2. Let ML handle the confounders

In I/O practice, we typically control for confounders by adding them as linear terms to a regression. That works if we're confident the relationships are linear, additive, and correctly specified. For age, tenure, level, span of control, and most categorical HR variables, we're often wrong. We just can't see the misspecification bias in the output.

Double machine learning lets flexible learners estimate the nuisance relationships, then uses a doubly robust correction to produce the causal estimate. The Neyman orthogonality property means moderate errors in the ML step don't propagate to the treatment effect estimate.

I know "throw random forests at it" triggers reasonable skepticism in I/O audiences, and it should. The discipline here isn't black-box prediction. It's a specific statistical structure (cross-fitting plus orthogonal scores) that delivers valid inference even with the ML step. It doesn't replace theory-driven modeling of the outcome. It replaces hand-coded functional form assumptions we couldn't justify anyway.

### 3. Use placebo tests when parallel trends can't be tested classically

Parallel trends (the assumption that treated and control units would have moved in parallel absent the event) is the load-bearing assumption of any DiD. With only one or two pre-periods (true for most quarterly pulses), we can't test it the standard way.

The paper adapts a technique from [Callison and Kaestner (2014)](https://doi.org/10.1111/ecin.12027): **assign placebo treatments to random control units, estimate the effect, and check that placebo effects cluster around zero.** This is a discipline worth building into every internal causal claim as a mandatory robustness check.

## What I/O psychology has to add

Econometricians don't talk about the things we lose sleep over. If we're going to use DiDDML responsibly in employee listening, four I/O concerns have to be built in up front.

**Measurement invariance across waves.** If we change items, response scales, or item ordering between waves, we don't have the same construct over time, and no estimator can rescue us. Configural and metric invariance testing is a prerequisite for longitudinal claims. That said, the temptation to demand full scalar invariance before any analysis is a form of perfectionism that leads to paralysis. Document changes, treat drift as a source of uncertainty, and be explicit about which outcomes are genuinely comparable versus which ones need caveats.

**Multilevel structure.** Employees nest in teams in BUs in countries. DiDDML clusters standard errors at the treatment assignment level, but it doesn't otherwise model the hierarchy. If treatment is assigned at the team level, your effective sample size is teams, not respondents. This has brutal implications for power. A pulse with 5,000 respondents across 20 treated teams is not a study with n = 5,000.

**Psychological confounds bundled with the event.** A reorg plus poor leader communication looks identical in survey data to a reorg alone. Be specific about what you're claiming the "treatment" is. Most of the time it's a bundle: the event *plus* its communication *plus* its change management. Either own that framing or design the evaluation to separate them (rarely feasible).

**Selection into response.** Anonymous pulses protect honesty but create selection. If an event changes who responds (say, engaged employees tune out while disgruntled ones respond more), the pre-to-post shift partly reflects sample composition rather than construct change. Response propensity modeling, non-response weighting, and sensitivity analyses should be standard, not optional.

## What the pipeline needs

Three things have to be in place before the first event evaluation can be credible:

- **Stable unit identifiers in every wave:** team, BU, country, function. Treatment is defined at the unit, and respondents inherit assignment. This design is ideal for anonymous surveys.
- **A standing covariate set:** same demographics, tenure bands, level, function captured every wave. If the questionnaire reshapes each pulse, the confounding controls go with it.
- **A structured event log:** what happened, when, to which units. Captured as events occur, not reconstructed from Slack six months later.

## Honest caveats

**Endogeneity.** If an event is triggered by the outcome (a reorg in response to low engagement), the design breaks. Many of our most interesting events are endogenous like this.

**Spillovers.** In a connected organization, employees in "control" units talk to employees in "treated" units, read the same Slack channels, attend the same town halls. The sharp treatment/control boundary DiD assumes is a convenient fiction. The bias is usually toward zero, but not always.

**Power.** Unit-level treatment assignment collapses effective sample size. For anything below country-level treatment, run the power calculation *before* fielding the pulse, not afterward when you're rationalizing a null.

**Multiple testing.** Every event × every outcome × every subgroup inflates the false positive rate. Benjamini-Hochberg adjustments, as the paper uses, aren't a nice-to-have.

## The reframe

The shift to pulse-based listening can feel like a methodological downgrade because we lose the individual panel. For some questions, it is. But for evaluating the effects of unit-level events, it gives us data whose structure matches a modern causal inference toolkit better than many of us might assume. Most I/O curricula still barely touch it. The paper that pointed me there happened to be about cigarettes 😅

<!-- RELATED:BEGIN -->
## Related notes
- [[cross-lagged-panel-modeling|Getting (more) causal insights from employee survey data (without an RCT)]]
- [[visual-diff-in-diff|Causal insights with no code?]]
- [[mixed-level-ml|Beyond the “flat Earth”]]
- [[multilevel-modeling|Multilevel modeling in people analytics]]
- [[dag-and-double-ml|A plausible model of data-generating process eats ML algorithms for breakfast]]
<!-- RELATED:END -->

---
> 📄 Read the [original post with full outputs](https://blog-about-people-analytics.netlify.app/posts/2026-04-15-did-with-repeated-cross-sectional-data/) on my blog.
