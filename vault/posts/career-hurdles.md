---
title: And what are your career hurdles?
description: Visualization of the results from a meta-analytic review of the hurdles to subjective career success.
date: '2025-02-05'
tags:
- career-development
- i-o-psychology
- meta-analysis
original: https://blog-about-people-analytics.netlify.app/posts/2025-02-05-career-hurdles/
---

I came across an interesting meta-analytic review by [Ng & Feldman (2014)](https://www.sciencedirect.com/science/article/pii/S0001879114000761) that might be useful for setting priors about the hurdles people face when it comes to their perception of subjective career success (SCS). The authors estimated the impact of 54 specific hurdles, grouped into six categories that can potentially lower people's SCS: 

1. Trait-related
2. Social-network-related
3. Skill-related
4. Organizational and job-related
5. Motivational
6. Background-related hurdles

On average, the strongest negative effects were found in the social and organizational hurdle groups, followed by trait-related and motivational hurdles. Interestingly, background-related and skill-related hurdles weren’t strongly associated with SCS. I’d say that’s good news, considering how non/malleable some of these types of hurdles can be 🤔

```r
# uploading libraries
library(tidyverse)
library(ggtext)
library(readxl)

# uploading the dataset with stats extracted from the research paper
data <- readxl::read_excel('career_hurdles_95CI.xlsx')

# defining colors for individual groups of career hurdles
category_colors <- c(
  "Background-related hurdles" = "#1B39A6", 
  "Motivational hurdles" = "#289ECC", 
  "Organizational and job hurdles" = "#B13AA0",
  "Skill-related hurdles" = "#73A239",
  "Social network hurdles" = "#895F22",
  "Trait-related hurdles" = "#D08311"
  
) 

# enriching the dataset for coloring the value labels
data <- data %>%
  dplyr::arrange(Category, desc(`95% CI Upper`)) %>%
  dplyr::mutate(
    Hurdle_ordered = factor(Hurdle, levels = unique(Hurdle)),
    Hurdle_colored = paste0("<span style='color:", category_colors[Category], "'>", Hurdle, "</span>")
  )

# dataviz
data %>% 
  ggplot2::ggplot(aes(x = Hurdle_ordered, y = rc, color = Category)) +
  ggplot2::geom_point(size = 3) +
  ggplot2::geom_errorbar(aes(ymin = `95% CI Lower`, ymax = `95% CI Upper`), width = 0.2, position = position_dodge(0.05), linewidth = 1) +
  ggplot2::geom_hline(yintercept = 0, linetype = "dashed", color = "grey") +
  ggplot2::scale_color_manual(values = category_colors) +
  ggplot2::coord_flip() +
  ggplot2::labs(
    x = "",
    y = "SAMPLE-SIZE WEIGHTED CORRECTED CORRELATION",
    title = "Relationships of career hurdles with subjective career success",
    caption = "\nThe bars around the point estimates represent the 2.5% lower and 97.5% upper limits of the 95% confidence interval.\nThe hurdles are listed by groups and in ascending order based on the upper bound of the 95% confidence interval for effect size.",
    color = ""
  ) +
  ggplot2::theme(
    plot.title = ggtext::element_markdown(face = "bold", size = 18, margin = margin(0, 0, 10, 0)),
    plot.subtitle = element_text(color = '#2C2F46', face = "plain", size = 16, margin = margin(0, 0, 20, 0)),
    plot.caption = element_text(color = '#2C2F46', face = "plain", size = 10, hjust = 0),
    axis.title.x.bottom = element_text(margin = margin(t = 15), color = '#2C2F46', face = "plain", size = 13),
    axis.title.y.left = element_text(margin = margin(r = 15), color = '#2C2F46', face = "plain", size = 13),
    axis.text.y = element_markdown(size = 12, lineheight = 1.2),  # Apply markdown here
    axis.line = element_line(colour = "#E0E1E6"),
    legend.position = "top", 
    legend.box = "horizontal",
    legend.justification = "right",
    legend.key = element_blank(),
    legend.text = element_text(size = 12),
    panel.background = element_blank(),
    panel.grid.major.y = element_blank(),
    panel.grid.major.x = element_blank(),
    panel.grid.minor = element_blank(),
    axis.ticks = element_line(color = "#E0E1E6"),
    plot.margin = unit(c(5, 5, 5, 5), "mm"), 
    plot.title.position = "plot",
    plot.caption.position = "plot"
  ) +
  ggplot2::scale_x_discrete(labels = function(x) data$Hurdle_colored[match(x, data$Hurdle_ordered)])  +
  ggplot2::guides(color = guide_legend(reverse = TRUE))

```

![](./career-hurdles/unnamed-chunk-1-1.png)
P.S. As is evident from the code snippet above, the attached chart isn't straight from the paper. I made it based on the results presented there, so any mistakes in the chart are on me!

<!-- RELATED:BEGIN -->
## Related notes
- [[selection-procedures-validity-update|Visualizing shifts in validity estimates for selection procedures]]
- [[vocational-interests|Vocational interests don't seem so uninteresting after all]]
- [[insights-discovery-and-skills|Do Insights Discovery ‘colors’ relate to self-reported skills?]]
- [[corporate-culture-trade-offs|The hidden trade-offs in corporate culture?]]
- [[collaboration-and-personality|Collaboration and personality]]
<!-- RELATED:END -->

---
> 📄 Read the [original post with full outputs](https://blog-about-people-analytics.netlify.app/posts/2025-02-05-career-hurdles/) on my blog.
