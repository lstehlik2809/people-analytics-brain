---
title: How should teams be designed to be creative and innovative?
description: A brief overview of the results of a meta-analysis on the relationship between team design and team creativity and innovation.
date: '2024-01-08'
tags:
- teams
- innovation
- leadership
- meta-analysis
original: https://blog-about-people-analytics.netlify.app/posts/2024-01-08-team-design-creativity-innovation/
---

If you are responsible for managing a team that is expected to be creative and come up with innovative solutions, you may be interested in the findings of [Byron et al.'s (2023)](https://onlinelibrary.wiley.com/doi/abs/10.1111/peps.12501) meta-analysis of team-design-related antecedents of team creativity and innovation. The meta-analysis aggregated results from 134 field studies (11,353 teams) and 35 student studies (2,485 teams) and revealed the following regularities, among others:

* Structuring teams to work interdependently (i.e. with greater interdependence of tasks and goals) is supportive of team creativity and innovation.
* Leaders providing autonomy to team members have teams that are more creative and innovative and this relationship is stronger when leaders emphasize team autonomy than when they emphasize the autonomy of individual team members.
* Related to the previous point, leaders who limit follower control also limit team creativity and innovation.
* Team size, demographic diversity, and job-related diversity show only a weak relationship with team creativity and innovation.
* Team task interdependence and supportive leadership are positively related to team creativity and innovation via processes of team collaboration (the extent to which team members work together to share information and knowledge) and team potency (the extent to which team members believe they can be effective).
* There is evidence for a curvilinear relationship between team tenure and team creativity and innovation. Specifically, when teams are relatively new (~1 yr), being together longer leads to a slight decrease in team creativity/innovation; when teams are of moderate tenure (~2.5 yrs), being together longer has no effect on team creativity/innovation; and, when teams are quite mature (~9 yrs), being together longer leads to an increase in team creativity/innovation.

```python
import pandas as pd
from plotnine import *

# uploading table with meta-analysis results
data = pd.read_excel("./metaanalysis_results.xlsx")
# extracting higher and lower borders of 95% CI
data[['l95ci', 'h95ci']] = data['95CI'].str.split(',', expand=True).astype(float)

# sorting the df for dataviz purposes
data['abs_P'] = data['P'].abs()
data_sorted = data.sort_values(by=['Category', 'abs_P'], ascending=[False, True])
categories_order = data_sorted['Variable'].unique()
data_sorted['Variable'] = pd.Categorical(data_sorted['Variable'], categories=categories_order, ordered=True)

```


```r
library(reticulate)
library(ggplot2)

colors = c(
  'Team composition'='#e15759',  
  'Task structure'='#f28e2b',  
  'Organizational support'='#4e79a7'
)

ggplot(py$data_sorted, aes(x=Variable, y=P, fill = Category, color = Category)) +
  geom_hline(yintercept=0, linetype="dashed", color="grey") +
  geom_point(size=3) +
  geom_errorbar(aes(ymin=l95ci, ymax=h95ci), width=0.3, size=1) +
  scale_color_manual(values=colors) +
  scale_fill_manual(values=colors) +
  coord_flip() +
  labs(
    x = "",
    y = "Optimally-weighted and corrected mean correlation (ρ) with 95% CI",
    title = "Meta-analytic results for team design and team creativity/innovation",
    fill = "",
    color = "",
    caption = "Data source: Byron et al. (2023)"
  ) +
  theme_bw() +
  ggplot2::theme(
    plot.title = element_text(color = '#2C2F46', face = "bold", size = 18, margin=margin(0,0,12,0)),
    plot.subtitle = element_text(color = '#2C2F46', face = "plain", size = 15, margin=margin(0,0,12,0)),
    plot.caption = element_text(color = '#2C2F46', face = "plain", size = 11, hjust = 0),
    axis.title.x.bottom = element_text(margin = margin(t = 15, r = 0, b = 0, l = 0), color = '#2C2F46', face = "plain", size = 13, hjust = 0),
    axis.text = element_text(color = '#2C2F46', face = "plain", size = 12),
    axis.line = element_line(colour = "#E0E1E6"),
    axis.ticks = element_line(color = "#E0E1E6"),
    strip.text.x = element_text(size = 11, face = "plain"),
    legend.position= "top",
    legend.key = element_rect(fill = "white"),
    legend.key.width = unit(1.6, "line"),
    legend.margin = margin(0,0,0,0, unit="cm"),
    legend.text = element_text(color = '#2C2F46', face = "plain", size = 12),
    panel.background = element_blank(),
    panel.grid.major.y = element_blank(),
    panel.grid.major.x = element_blank(),
    panel.grid.minor = element_blank(),
    plot.margin=unit(c(5,5,5,5),"mm"), 
    plot.title.position = "plot",
    plot.caption.position =  "plot"
  )

```

What might be the practical implications for managers?  

* Focus on selecting team members who are diverse in terms of job-related factors such as educational background.
* Ensure task and goal interdependence - design projects to require collaboration, provide team-level feedback, and create team accountability systems.
* When leading innovative teams, adopt an approach aimed at supporting and encouraging - not controlling - the team as a whole as opposed to the individuals within the team.
* Try to keep high-quality people in the team as team tenure is positively related to team creativity and innovation.

<!-- RELATED:BEGIN -->
## Related notes
- [[team-level-predictors-of-innovation|Team-level predictors of innovation at work]]
- [[tas-c-suit-teams|Insights from the Team Assessment Survey results of C-suite teams]]
- [[cognitive-diversity|Can there be too much cognitive diversity in teams?]]
- [[self-leadership|Self-Leadership: A New Superpower?]]
- [[corporate-culture-trade-offs|The hidden trade-offs in corporate culture?]]
<!-- RELATED:END -->

---
> 📄 Read the [original post with full outputs](https://blog-about-people-analytics.netlify.app/posts/2024-01-08-team-design-creativity-innovation/) on my blog.
