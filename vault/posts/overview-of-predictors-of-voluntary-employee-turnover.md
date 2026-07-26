---
title: Overview of predictors of voluntary employee turnover
description: An introduction of a simple R Shiny application to facilitate extraction and digestion of information from meta-analysis of predictors of voluntary employee turnover.
date: '2021-12-12'
tags:
- employee-turnover
- meta-analysis
- shiny-app
original: https://blog-about-people-analytics.netlify.app/posts/2021-12-12-overview-of-predictors-of-voluntary-employee-turnover/
---

```r
knitr::opts_chunk$set(echo = FALSE)
```

Although the 'Great Resignation' in some parts of the world may be due in no small part to factors specific to the COVID-19 pandemic, it is still useful in this context to draw on the extensive research on employee turnover carried out in the run-up to the pandemic. 

A useful overview of such findings is provided, for example, by a 2017 meta-analysis by Rubenstein et al. that summarizes the significance of 57 predictors of voluntary turnover from 9 different domains based on 316 studies from 1975 to 2016 involving more than 300,000 people. 
To make it easier to assimilate these findings, I extracted them from the original article and visualized them in a simple shiny app that helps one to quickly explore and grasp the estimated magnitude, direction, and reliability of the effect of each factor, along with information on the degree of their actionability. The last feature is based purely on my own judgement, so please take it with a grain of salt, or adjust it in your mind using your own judgement. Try it out and let me know if you find it useful.

➡️ https://peopleanalyticsblog.shinyapps.io/voluntary_turnover_predictors/

[![Overview of predictors of voluntary employee turnover](./overview-of-predictors-of-voluntary-employee-turnover/turnover_predictors_app.png)](https://peopleanalyticsblog.shinyapps.io/voluntary_turnover_predictors/)

And here is the original research paper on which the shiny app is based.

<object data="Rubenstein_et_al-2017-Personnel_Psychology.pdf" type="application/pdf" height="400px">
    <embed src="Rubenstein_et_al-2017-Personnel_Psychology.pdf">
        <p>This browser does not support PDFs. Please download the PDF to view it: <a href="Rubenstein_et_al-2017-Personnel_Psychology.pdf">Download PDF</a>.</p>
    </embed>
</object>

<!-- RELATED:BEGIN -->
## Related notes
- [[resources-on-retention-and-downsizing|Some resources on staff retention and downsizing]]
- [[predictors-of-stay-intentions-vs-actual-resignations|Talk vs. Walk: Predictors of staying intentions vs. actual quitting behavior]]
- [[survey-participation-and-attrition-prediction|People may signal their exit intentions not only by their actions but also by their inactions]]
- [[regression-to-the-mean|Employee commitment over time & regression to the mean]]
- [[bayesian-shrinkage|Using Bayesian shrinkage in reporting employee turnover]]
<!-- RELATED:END -->

---
> 📄 Read the [original post with full outputs](https://blog-about-people-analytics.netlify.app/posts/2021-12-12-overview-of-predictors-of-voluntary-employee-turnover/) on my blog.
