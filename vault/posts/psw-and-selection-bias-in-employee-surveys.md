---
title: How to analyze employee survey results with less (selection) bias?
description: About a simple method for correcting non-response bias in employee survey analysis, based on causal inference, that estimates the average satisfaction if everyone had responded.
date: '2025-03-10'
tags:
- employee-survey
- causal-inference
original: https://blog-about-people-analytics.netlify.app/posts/2025-03-10-psw-and-selection-bias-in-employee-surveys/
---

When analyzing employee survey results, do you systematically account for the fact that your response rate isn't 100% and that participation isn't random, as employees probably decide to participate based on their satisfaction levels—the very thing you're aiming to measure?

Personally, I haven't been rigorous about this. At best, I've checked the representativeness of survey respondents across various demographic factors. This allowed me to identify which groups within the organization were underrepresented and speculate which might be less satisfied, assuming less satisfied employees are less likely to participate (though it's possible the opposite scenario could be true as well!).

Recently, while exploring [propensity score weighting](https://pmc.ncbi.nlm.nih.gov/articles/PMC3144483/) (PSW) in the context of causal inference, I discovered that this method isn't only useful for reducing confounding bias but also selection bias. This makes it highly relevant for analysis of employee surveys, where a significant portion of the workforce often doesn't participate, and participation itself is likely linked to the very attitudes and behaviors you're investigating.

By modeling response behavior using demographic and other relevant variables and weighting responses inversely to the employees’ probability of participating, you can achieve a more accurate—neither overly optimistic nor pessimistic—estimate of average employee satisfaction, essentially approximating what you would observe if everyone had participated. (You can hear in this the echoes of causal inference—aiming to estimate a counterfactual scenario, one that didn't actually happen but is important to consider to make proper conclusions about the world).

The implementation isn't overly complex. If you're interested in a quick start, you can check out illustrative Python code I've prepared using dummy data that simulates employee responses with a non-random likelihood of participation.

First, let's prepare the data to fit our selection bias scenario—left-skewed engagement scores of 10,000 employees, along with demographic variables that influence the probability of employees' participation in the survey.

```r
# reticulate library for running Python in .Rmd file
library(reticulate)

```

```python
# importing libraries to be used
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
import matplotlib.pyplot as plt
import seaborn as sns

# setting random seed for reproducibility
np.random.seed(2025)

# simulating employee data
n_employees = 10000

data = pd.DataFrame({
    "employee_id": np.arange(n_employees),
    "gender": np.random.choice(["Male", "Female"], size=n_employees, p=[0.5, 0.5]),
    "age": np.random.randint(20, 65, size=n_employees),
    "department": np.random.choice(["Manufacturing", "Sales", "IT", "HR"], size=n_employees, p=[0.4, 0.3, 0.2, 0.1]),
})

# defining base participation probability (100%)
data["base_prob"] = 1

# adjusting participation probability based on bias factors
data.loc[data["gender"] == "Female", "base_prob"] -= 0.2  # lower participation for females
data.loc[data["age"] < 30, "base_prob"] -= 0.35  # lower participation for younger employees
data.loc[data["department"] == "Manufacturing", "base_prob"] -= 0.4  # lower participation in Manufacturing

data["base_prob"] = np.clip(data["base_prob"], 0.1, 0.99)  # ensuring probabilities stay in a reasonable range

# simulating left-skewed engagement scores with beta distribution
raw_engagement = np.random.beta(a=2, b=10, size=n_employees) * 10  
raw_engagement = np.max(raw_engagement) - raw_engagement
# standardizing raw engagement scores to be between 0 and 10
raw_engagement = 10 * (raw_engagement - np.min(raw_engagement)) / (np.max(raw_engagement) - np.min(raw_engagement))

```

```python
# plotting distribution of engagement scores
sns.kdeplot(raw_engagement, label="Raw Engagement", fill=True, color='#a0cbe8', alpha=1)
plt.xlabel("Engagement Score")
plt.ylabel("Density")
plt.title("Engagement Score Distribution")
plt.show()

```

![](./psw-and-selection-bias-in-employee-surveys/unnamed-chunk-3-1.png)

Now, let's introduce a negative correlation between the engagement score and participation probability and verify that employees who didn't participate indeed have lower engagement scores on average.

```python
# introducing correlation between engagement score and participation probability
data["engagement"] = raw_engagement + 5 * (data["base_prob"] - np.mean(data["base_prob"]))
data["engagement"] = np.clip(data["engagement"], 0, 10)  # keeping engagement scores in range

# simulating participation
data["participated"] = np.random.rand(n_employees) < data["base_prob"]
data['participated_num'] = data['participated'].astype(int)

# comparing engagement by participation
# preparing data for plotting
data_x = [data[data['participated_num'] == 0]['engagement'],
          data[data['participated_num'] == 1]['engagement']]
# creating the raincloud plot
fig, ax = plt.subplots(figsize=(10, 6))
# defining colors
boxplots_colors = ['#f28e2b', '#4e79a7']
violin_colors = ['#f28e2b', '#4e79a7']
scatter_colors = ['#f28e2b', '#4e79a7']
# adding boxplot
bp = ax.boxplot(data_x, patch_artist=True, vert=False, showfliers=False, 
                medianprops={'color': 'black', 'linewidth': 1.5})
for patch, color in zip(bp['boxes'], boxplots_colors):
    patch.set_facecolor(color)
    patch.set_alpha(0.4)
# adding half of the violin plot
vp = ax.violinplot(data_x, points=500, showmeans=False, showextrema=False, showmedians=False, vert=False)
for idx, b in enumerate(vp['bodies']):
    m = np.mean(b.get_paths()[0].vertices[:, 0])
    b.get_paths()[0].vertices[:, 1] = np.clip(b.get_paths()[0].vertices[:, 1], idx + 1, idx + 2)
    b.set_color(violin_colors[idx])
# adding scatter plot
for idx, features in enumerate(data_x):
    y = np.full(len(features), idx + .8)
    idxs = np.arange(len(y))
    out = y.astype(float)
    out.flat[idxs] += np.random.uniform(low=-.05, high=.05, size=len(idxs))
    y = out
    plt.scatter(features, y, s=.3, c=scatter_colors[idx])
# adding mean values inside the boxplots
means = [np.mean(features) for features in data_x]
for idx, mean in enumerate(means):
    ax.scatter(mean, idx + 1, color='red', s=50, zorder=3)
# adding labels and title
plt.yticks(np.arange(1, 3, 1), ['Not Participated', 'Participated']);
plt.xlabel('Engagement Score')
plt.title("Engagement by Participation")
plt.show()

```

![](./psw-and-selection-bias-in-employee-surveys/unnamed-chunk-4-3.png)

We can clearly see in the raincloud plots above that non-participants indeed have significantly lower engagement scores than participants. This discrepancy naturally results in a difference between the average engagement score of the full population and that of our observed, biased sample, as illustrated in the chart below.

```python
# computing engagement means before adjustment for the full population and observed sample
observed_mean = data.loc[data["participated"], "engagement"].mean()
true_mean = data["engagement"].mean()

# plotting engagement scores before weighting
sns.kdeplot(data.loc[data["participated"], "engagement"], label="Biased Sample", fill=False)
sns.kdeplot(data["engagement"], label="Full Population", fill=False)
# adding vertical lines for mean values
plt.axvline(observed_mean, color='#4e79a7', linestyle='dotted', label='Observed Mean')
plt.axvline(true_mean, color='#f28e2b', linestyle='dotted', label='True Mean')
plt.legend()
plt.xlabel("Engagement Score")
plt.ylabel("Density")
plt.title("Engagement Score Distribution Before Weighting")
plt.show()

```

![](./psw-and-selection-bias-in-employee-surveys/unnamed-chunk-5-5.png)

To improve our estimation, let's use PSW, which will enable us to approximate a scenario in which all employees participate, while relying solely on data from participating employees.

```python
# fitting logistic regression to estimate propensity scores
X = pd.get_dummies(data[["gender", "age", "department"]], drop_first=True)
y = data["participated"].astype(int)
logit = LogisticRegression()
logit.fit(X, y)

# computing propensity scores (predicted probabilities of participation)
data["propensity_score"] = logit.predict_proba(X)[:, 1]
data["weight"] = 1 / data["propensity_score"]  # Inverse probability weighting
data["weight"] = np.clip(data["weight"], 1, 5)  # Prevent extreme weights

# computing weighted engagement mean for observed sample
weighted_mean = np.average(data.loc[data["participated"], "engagement"], weights=data.loc[data["participated"], "weight"])

# displaying results
print(f"True engagement mean (full population): {true_mean:.2f}")
print(f"Observed engagement mean (biased sample): {observed_mean:.2f}")
print(f"Weighted engagement mean (after adjustment): {weighted_mean:.2f}")

# plotting engagement scores before/after weighting
sns.kdeplot(data.loc[data["participated"], "engagement"], label="Biased Sample", fill=False)
sns.kdeplot(data["engagement"], label="Full Population", fill=False)
# adding vertical lines for mean values
plt.axvline(observed_mean, color='#4e79a7', linestyle='dotted', label='Observed Mean')
plt.axvline(true_mean, color='#f28e2b', linestyle='dotted', label='True Mean')
plt.axvline(weighted_mean, color='black', linestyle='dotted', label='Adjusted Observed Mean')
plt.legend()
plt.xlabel("Engagement Score")
plt.ylabel("Density")
plt.title("Engagement Score Distribution Before/After Weighting")
plt.show()

```

As the numbers and chart above clearly show, using PSW has brought our estimation much closer to the average engagement of the full population, as if all employees had participated in the survey. However, the accuracy of this adjustment depends on how well we can model the probability of participation using available variables and the extent to which participation probability is systematically related to engagement scores in ways that our model can adjust for. In a real-world scenario, the results may not be as precise as in this simulation, where we have full control over the conditions. Nonetheless, PSW typically reduces bias, bringing estimates closer to the true engagement level, provided key assumptions hold.

Have you tried similar methods in your employee survey analyses? What's your experience been like? Any caveats, lessons learned, or warnings you'd share?

## Figures

![](./psw-and-selection-bias-in-employee-surveys/unnamed-chunk-6-7.png)

<!-- RELATED:BEGIN -->
## Related notes
- [[rwa|RWA – A go-to tool for key drivers analysis of employee survey data?]]
- [[glassdoor|When flawed statistical & causal reasoning leads to a valid conclusion anyway]]
- [[bayesian-shrinkage|Using Bayesian shrinkage in reporting employee turnover]]
- [[latent-class-analysis|Latent Class Analysis of responses from employee surveys]]
- [[psychometric-network-analysis|Psychometric network analysis & employee survey data]]
<!-- RELATED:END -->

---
> 📄 Read the [original post with full outputs](https://blog-about-people-analytics.netlify.app/posts/2025-03-10-psw-and-selection-bias-in-employee-surveys/) on my blog.
