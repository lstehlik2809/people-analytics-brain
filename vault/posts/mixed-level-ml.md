---
title: Beyond the “flat Earth”
description: Most ML workflows assume the world is "flat". People data isn't.
date: '2026-03-23'
tags:
- machine-learning
- multilevel-modeling
- causal-inference
- predictive-analytics
original: https://blog-about-people-analytics.netlify.app/posts/2026-03-23-mixed-level-ml/
---

I have to reluctantly admit that, until recently, my approach to predictive machine learning (ML) tasks relied on one major simplification: I ignored the hierarchical structure in my data and treated observations as [i.i.d.](https://en.wikipedia.org/wiki/Independent_and_identically_distributed_random_variables) Part of that was convenience, and part of it was the practical belief that standard ML often captures most of the predictive signal while being much simpler to implement than a full mixed-effects model.

But once I started using ML not just for prediction, but also for causal inference, the limits of that “flat-earth” view became hard to ignore. In People Analytics, data is usually nested: individuals within teams, teams within departments, and sometimes departments within business units. Ignoring that structure means ignoring a big part of the context that shapes human behavior.

## Grouped Cross-Validation

The first requirement for working with clustered data in this context is recognizing that standard cross-validation (CV) can be misleading when observations within a cluster are correlated. If members of the same team appear in both the training and test sets, the model can effectively “peek” at the test distribution through shared group structure. That usually leads to performance estimates that are too optimistic.

The first practical fix is to move from standard K-fold CV to `GroupKFold`. This keeps entire clusters together, so the model is evaluated on genuinely unseen groups.

**Advantage:** Grouped CV does not improve the model itself, but it gives you a much more honest estimate of whether the model will hold up on new teams or departments. In other words, it is less about boosting performance and more about avoiding self-deception.

### Example: GroupKFold + XGBoost

```python
# Synthetic data generator for the GroupKFold + XGBoost example

import numpy as np
import pandas as pd

def make_grouped_prediction_data(
    n_teams=40,
    min_team_size=15,
    max_team_size=30,
    seed=42,
):
    rng = np.random.default_rng(seed)

    team_sizes = rng.integers(min_team_size, max_team_size + 1, size=n_teams)
    team_id = np.repeat(np.arange(n_teams), team_sizes)
    n = len(team_id)

    # Create team-level latent effects so observations within the same
    # team are meaningfully correlated.
    team_baseline = rng.normal(0.0, 1.5, size=n_teams)
    team_skill = rng.normal(0.0, 1.0, size=n_teams)

    # Generate individual-level predictors with partial dependence on team.
    tenure = rng.gamma(shape=2.5, scale=2.0, size=n) + 0.7 * team_skill[team_id]
    base_salary = rng.normal(
        loc=60000 + 5000 * team_skill[team_id],
        scale=7000,
        size=n,
    )
    engagement = rng.normal(loc=team_skill[team_id], scale=1.0, size=n)
    workload = rng.normal(loc=0.0, scale=1.0, size=n)

    # Build a nonlinear target that combines individual predictors,
    # team-specific effects, and random noise.
    y = (
        1.2 * np.sin(engagement)
        + 0.35 * np.log1p(np.maximum(tenure, 0))
        + 0.00003 * base_salary
        - 0.5 * workload
        + team_baseline[team_id]
        + rng.normal(0.0, 1.0, size=n)
    )

    df = pd.DataFrame(
        {
            "team_id": team_id,
            "tenure": tenure,
            "base_salary": base_salary,
            "engagement": engagement,
            "workload": workload,
            "performance": y,
        }
    )

    X = df[["tenure", "base_salary", "engagement", "workload"]]
    y = df["performance"].to_numpy()

    return df, X, y

# Run grouped cross-validation so that entire teams are held out together.
# This avoids leakage that would occur if rows from the same team appeared
# in both training and validation folds.

from xgboost import XGBRegressor
from sklearn.model_selection import GroupKFold, cross_val_score

df, X, y = make_grouped_prediction_data()

groups = df["team_id"]
model = XGBRegressor(
    n_estimators=100,
    learning_rate=0.05,
    max_depth=4,
    subsample=0.9,
    colsample_bytree=0.9,
    random_state=42,
)
cv = GroupKFold(n_splits=5)

scores = cross_val_score(model, X, y, groups=groups, cv=cv)
print(f"Grouped-CV R^2: {scores.mean():.3f}")
print("Fold scores:", np.round(scores, 3))
```

One important caveat: this is the right validation strategy if your real deployment target is **new groups**. If the model will be used within already-seen teams, the validation design may need to reflect that instead.

## Mixed-Effects ML

Grouped CV fixes the evaluation problem, but it does not change the model itself. For some problems, especially when group-level heterogeneity matters, it can be useful to fit models that explicitly separate two sources of signal:

* **Fixed effects**: global patterns learned from predictors
* **Random effects**: group-specific deviations, such as team-level intercepts

Libraries such as `GPBoost` or `MERF` let you combine flexible ML models with random effects using a structure like:
$$
y = F(X) + Zb + \epsilon
$$
Here, \(F(X)\) is a nonlinear prediction function, such as a random forest or gradient-boosted tree, and \(Zb\) represents group-level random effects.

**Advantage:** Mixed-effects ML can improve performance when groups have persistent baseline differences, because it lets the model learn both global patterns and group-level structure. It also gives you a more interpretable decomposition of what is happening at the individual level versus the team or department level.

### Example: Mixed Effects Random Forest (MERF)

```python
# Synthetic data generator for the MERF example

import numpy as np
import pandas as pd

def make_merf_data(
    n_teams=30,
    min_team_size=20,
    max_team_size=35,
    seed=42,
):
    rng = np.random.default_rng(seed)

    team_sizes = rng.integers(min_team_size, max_team_size + 1, size=n_teams)
    team_id = np.repeat(np.arange(n_teams), team_sizes)
    n = len(team_id)

    # Assign a random intercept to each team to introduce cluster-specific
    # variation that the mixed-effects model should recover.
    b_team = rng.normal(0.0, 2.0, size=n_teams)

    # Generate fixed-effect predictors.
    x1 = rng.normal(0, 1, size=n)
    x2 = rng.normal(0, 1, size=n)
    x3 = rng.normal(0, 1, size=n)

    # Define a nonlinear fixed-effect signal and combine it with the
    # team-level random intercept and observation noise.
    f_x = 2.0 * x1 + x2**2 + 4.0 * (x3 > 0).astype(float) + 1.5 * np.log1p(np.abs(x1)) * x3
    y = f_x + b_team[team_id] + rng.normal(0.0, 1.0, size=n)

    df = pd.DataFrame(
        {
            "team_id": team_id,
            "x1": x1,
            "x2": x2,
            "x3": x3,
            "performance": y,
        }
    )

    X = df[["x1", "x2", "x3"]].to_numpy()
    Z = np.ones((n, 1))  # Random-intercept design matrix.
    clusters = df["team_id"]
    y = df["performance"].to_numpy()

    return df, X, Z, clusters, y

# Fit MERF with a random forest as the fixed-effects learner.
# This example shows how to combine nonlinear prediction with
# cluster-specific random intercepts.

from merf import MERF
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score

df, X, Z, clusters, y = make_merf_data()

rf_engine = RandomForestRegressor(n_estimators=100, random_state=42)
merf_model = MERF(fixed_effects_model=rf_engine, max_iterations=20)

merf_model.fit(X, Z, clusters=clusters, y=y)

y_hat = merf_model.predict(X, Z, clusters=clusters)
print(f"In-sample R^2: {r2_score(y, y_hat):.3f}")

# Inspect the estimated random effects over iterations using a portable,
# dataframe-based summary.
print(merf_model.get_bhat_history_df().tail())
```

## Cluster-Aware Causal ML

The hardest problem in People Analytics is usually causal: for example, estimating the effect of a leadership intervention. Standard ML is not enough here. It must be harnessed in a specialized way, as in the Double Machine Learning (DML) framework, for example. 

DML helps by residualizing both the treatment (\(T\)) and the outcome (\(Y\)) using flexible nuisance models. However, with hierarchical data, those nuisance models and the sample-splitting strategy should respect the cluster structure. The final inference step should also account for within-cluster dependence so that standard errors and p-values are better calibrated.

What cluster-aware causal ML gives you is better inference under clustered dependence. What it does <ins>not</ins> do is magically eliminate bias from unobserved cluster-level confounding. That still depends on whether your identification assumptions are credible.

**Advantage:** Cluster-aware causal ML does not make causal identification easy, but it does make ML-based causal estimation more defensible when your data are nested and observations within groups are dependent.

### Example: Cluster-Aware DML

```python
# Synthetic data generator for the cluster-aware DoubleML example

import numpy as np
import pandas as pd

def make_clustered_dml_data(
    n_teams=80,
    min_team_size=10,
    max_team_size=20,
    true_theta=1.5,
    seed=42,
):
    rng = np.random.default_rng(seed)

    team_sizes = rng.integers(min_team_size, max_team_size + 1, size=n_teams)
    team_id = np.repeat(np.arange(n_teams), team_sizes)
    n = len(team_id)

    # Create an observed team-level covariate that influences both
    # treatment assignment and outcomes.
    manager_quality = rng.normal(0.0, 1.0, size=n_teams)

    # Generate individual-level covariates.
    tenure = rng.gamma(shape=2.5, scale=2.0, size=n)
    base_salary = rng.normal(
        loc=65000 + 4000 * manager_quality[team_id],
        scale=8000,
        size=n,
    )
    potential = rng.normal(0.0, 1.0, size=n)

    tenure_z = (tenure - tenure.mean()) / tenure.std()
    salary_z = (base_salary - base_salary.mean()) / base_salary.std()
    manager_q = manager_quality[team_id]

    # Simulate treatment assignment from observed covariates so the setup
    # resembles a realistic observational treatment mechanism.
    logits = 0.8 * manager_q + 0.5 * tenure_z - 0.3 * salary_z + 0.6 * potential
    p = 1.0 / (1.0 + np.exp(-logits))
    intervention_treated = rng.binomial(1, p, size=n)

    # Add team-level shocks to the outcome to create within-cluster
    # dependence without introducing hidden confounding by design.
    team_error = rng.normal(0.0, 1.0, size=n_teams)

    performance = (
        true_theta * intervention_treated
        + 0.6 * np.log1p(tenure)
        - 0.25 * salary_z
        + 0.7 * manager_q
        + 0.5 * potential
        + team_error[team_id]
        + rng.normal(0.0, 1.0, size=n)
    )

    df = pd.DataFrame(
        {
            "team_id": team_id,
            "performance": performance,
            "intervention_treated": intervention_treated,
            "tenure": tenure,
            "base_salary": base_salary,
            "potential": potential,
            "manager_quality": manager_q,
        }
    )

    return df, true_theta

# Fit a partially linear DoubleML model with cluster-aware inference.
# The goal is to recover the treatment effect while respecting the
# grouped structure in the data.

from doubleml import DoubleMLData, DoubleMLPLR
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier

df, true_theta = make_clustered_dml_data()

obj_dml_data = DoubleMLData(
    df,
    y_col="performance",
    d_cols="intervention_treated",
    x_cols=["tenure", "base_salary", "potential", "manager_quality"],
    cluster_cols="team_id",
)

ml_l = RandomForestRegressor(max_depth=5, n_estimators=200, random_state=42)
ml_m = RandomForestClassifier(max_depth=5, n_estimators=200, random_state=42)

dml_plr = DoubleMLPLR(obj_dml_data, ml_l, ml_m)
dml_plr.fit()

print(f"True treatment effect: {true_theta:.4f}")
print(f"Estimated treatment effect: {dml_plr.coef[0]:.4f}")
print(f"SE: {dml_plr.se[0]:.4f}")
print(f"t-stat: {dml_plr.t_stat[0]:.4f}")
print(f"P-value: {dml_plr.pval[0]:.4f}")

print(dml_plr.summary)
```

## My Key Takeway

For me, the progression now looks something like this:

* If I just want a more realistic estimate of predictive performance across teams, I start with **grouped cross-validation**.
* If I want the model itself to reflect stable group-level differences, I look at **mixed-effects ML**.
* If I care about causal effects and the data are nested, I consider **cluster-aware causal ML**.

That is not because hierarchy always makes models better. It is because, in many real-world settings, hierarchy is part of the data-generating process, and pretending otherwise usually comes back to bite you.

❓Curious what your usual approach is to ML tasks with hierarchical data.

<!-- RELATED:BEGIN -->
## Related notes
- [[multilevel-modeling|Multilevel modeling in people analytics]]
- [[dag-and-double-ml|A plausible model of data-generating process eats ML algorithms for breakfast]]
- [[cross-lagged-panel-modeling|Getting (more) causal insights from employee survey data (without an RCT)]]
- [[did-with-repeated-cross-sectional-data|What a European cigarette tax study taught me about employee listening]]
- [[span-of-control-and-managerial-behavior|Can flatter orgs undermine people management?]]
<!-- RELATED:END -->

---
> 📄 Read the [original post with full outputs](https://blog-about-people-analytics.netlify.app/posts/2026-03-23-mixed-level-ml/) on my blog.
