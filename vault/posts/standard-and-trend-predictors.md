---
title: Standard vs. trend predictors
description: When modeling a phenomenon, one usually can't get by with just raw data but must use one's domain knowledge to select and transform the most relevant variables from raw data to be able to successfully grasp regularities in the domain of one's interest. Let's look at one simple example of such feature engineering from the domain of collaboration analytics.
date: '2022-02-06'
tags:
- predictive-analytics
- machine-learning
- employee-experience
- employee-engagement
- employee-satisfaction
- employee-turnover
- collaboration
original: https://blog-about-people-analytics.netlify.app/posts/2022-02-06-standard-and-trend-predictors/
---

As predictive analytics practitioners know, **trend variables** can be more useful in many situations for predicting certain phenomena than **standard variables** that simply refer to the state of the world at a particular time point or period. 

For example, when trying to predict [employee attrition](https://www.aihr.com/blog/employee-attrition/), a downward trend in the use of a piece of company equipment, such as a printer/copier, over the 6 months prior to the resignation may be more predictive than the absolute number of pages printed/copied over the same period. 

This is also true for our domain we focus on at [Time is Ltd.](https://www.timeisltd.com/) where, among other things, we try to use collaboration data to infer some aspects of [employee experience](https://www.cultureamp.com/blog/what-is-employee-experience).

To illustrate, the attached chart shows the distribution of the typical daily amount of time people spend by collaboration for two groups of employees - one with above-average scores and the other with below-average scores on the employee satisfaction survey. As you can see, there is little difference between the two groups in terms of the average daily amount of time people spend by collaboration over the last six months (see the density plots), but there is a fairly clear difference in the trend of this metric over the same period, suggesting that less satisfied employees may be suffering from increasing collaboration overload (see the line charts with trend lines for individual employees and the estimated overall linear trend).  

<br> 

![](./standard-and-trend-predictors/collaborationActivityChart.png) 

<br> 

Do you have a similar experience with or just a strong hunch about other metrics in your area of expertise? Let me know in the comments.

<!-- RELATED:BEGIN -->
## Related notes
- [[regression-to-the-mean|Employee commitment over time & regression to the mean]]
- [[change-detection|How to quickly navigate dashboard users to what they need to know?]]
- [[probability-of-comments-in-a-survey|What makes people more likely to comment on a question in an employee survey?]]
- [[predictors-of-stay-intentions-vs-actual-resignations|Talk vs. Walk: Predictors of staying intentions vs. actual quitting behavior]]
- [[personality-and-non-linearities|Nonlinear relationships between personality traits and business outcomes seem to be the norm rather than the exception]]
<!-- RELATED:END -->

---
> 📄 Read the [original post with full outputs](https://blog-about-people-analytics.netlify.app/posts/2022-02-06-standard-and-trend-predictors/) on my blog.
