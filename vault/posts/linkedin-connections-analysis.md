---
title: R Shiny app for LinkedIn connections analysis
description: An introduction of a simple R Shiny application for analysing LinkedIn connections.
date: '2021-12-16'
tags:
- linkedin
- collaboration
- network-analysis
- shiny-app
original: https://blog-about-people-analytics.netlify.app/posts/2021-12-16-linkedin-connections-analysis/
---

If you like to use the end of the year as an opportunity for deeper self-reflection, you might enjoy [this simple app](https://peopleanalyticsblog.shinyapps.io/linkedIn_connections_analysis/) I have put together over the past weekend. 

Once you upload your LinkedIn connections data to the app (you can easily download the data by following the instructions in the app or in [this video](https://www.youtube.com/watch?v=FLWSmiBxQQY)), it automatically generates basic descriptive statistics about your LinkedIn connections:

* Cumulative number of connections over time  
* Number of established connections by years, months, and days of the week 
* Top N companies by the number of established connections
* Top N positions by their frequency among your connections (based on whole position titles, bigrams and single words)
* Proportion of connections by their gender (based on your connections' first name)

<div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden;">

  <video controls style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;">
    <source src="video_tour.mp4" type="video/mp4">
    Your browser does not support the video tag.
  </video>

</div>
<br>

Unfortunately, since there is no information about your connections' connections in the data, the app cannot perform more advanced SNA-type of analyses on it. Still, I think you may find some of the statistics useful, or at least interesting and entertaining.

You can take it as a kind of Christmas gift for my fellow LinkedIn users. Enjoy exploring your connections! And if you'd like to explore and better manage also your company's internal collaboration networks, then check out what we do at [Time is Ltd.](https://www.timeisltd.com/) 

P.S. The data you upload is not permanently stored anywhere. The app runs on the [shinyapps.io server](https://www.shinyapps.io/). If you don’t want to upload your own data, but would still like to see what the analysis output looks like, you can download and then upload ready-made sample data from the app.

P.P.S. Big thanks to [Sebastian Vorac](https://www.linkedin.com/in/sebastian-vor%C3%A1%C4%8D-93361526/) for bringing me to this idea and for UX review. Any remaining errors are, of course, mine alone.

<!-- RELATED:BEGIN -->
## Related notes
- [[linkedin-contacts-job-positions|Analyzing LinkedIn connections' jobs using LLMs and the BERTopic package]]
- [[david-green-hr-people-sna-network|Mapping the People Analytics universe]]
- [[job-comparator|A bet on a new job]]
- [[network-graph-employee-comments|Using network graph modeling to capture overarching thematic clusters in employee comments]]
- [[overview-of-predictors-of-voluntary-employee-turnover|Overview of predictors of voluntary employee turnover]]
<!-- RELATED:END -->

---
> 📄 Read the [original post with full outputs](https://blog-about-people-analytics.netlify.app/posts/2021-12-16-linkedin-connections-analysis/) on my blog.
