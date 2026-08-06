---
title: SIOP 2026 Recommender
description: A practical AI assistant for finding the most relevant SIOP 2026 sessions and building a conflict-free personal schedule.
date: '2026-04-18'
tags:
- siop
- machine-learning
original: https://blog-about-people-analytics.netlify.app/posts/2026-04-18-siop-2026-recommender/
---

Attending SIOP for the first time this year confronted me with something that more seasoned attendees are probably already used to and may even have a few tricks for handling.

I’m talking about the need to sift through a huge number of interesting sessions packed into 3–4 days of the conference and choose the ones that best match my interests and needs.

I’ll admit it freely: I was somewhat paralyzed by the sheer volume of options. The filtering options on the website did not help much either. Scrolling through everything was still endless and pretty mentally exhausting.

I needed help narrowing things down. As you can probably guess, AI came to the rescue 🤖 During our last Friday afternoon dedicated to exploration and experimentation, and over part of the weekend, I managed to build and deploy an app designed to help with exactly that.

What does it do?️

* In the Profile section, you describe what you want from the conference: your goals, keywords, what to avoid, and optionally your CV. You can also include skills you want to develop or acquire.️
* You can adjust how strongly each of these inputs influences the search.️
* You get a ranked list of sessions, with schedule conflicts clearly marked.️
* You get an optimized personal agenda that avoids overlapping sessions.️
* As a bonus, you can explore an interactive SNA-style map of session similarity, with your top recommendations highlighted.

Give it a try and let me know whether it makes your SIOP planning at least a little bit easier. In my case, it helped a lot 🤓 You can access it [here](https://siop-recommender-48217563872.europe-west1.run.app/), or for now, just check the screenshots below (double-click any slide to zoom in).

⚠️ As is often the case with AI, treat its recommendations more as inspiration than as definitive guidance, and verify them against a reliable source such as the official SIOP schedule. The app works only with session titles, not abstracts; errors may have occurred during information extraction; and the embedding model used does not capture every semantic nuance. So there is plenty of room for mistakes.

**Update**: Now that SIOP 2026 has wrapped, the Recommender can officially retire. RIP, SIOP 2026 Recommender. You served us well 🫡 Thanks to everyone who tried it - it was fun building this.

```r
library(pdftools)
library(swipeR)
library(htmltools)

pdf_file <- "siop_2026_recommender_screenshots.pdf"
img_dir <- "slides_img"

if (!dir.exists(img_dir)) dir.create(img_dir)

n <- pdf_info(pdf_file)$pages
files <- pdf_convert(
  pdf_file,
  format = "png",
  dpi = 150,
  filenames = sprintf("%s/page-%02d.png", img_dir, seq_len(n)),
  verbose = FALSE
)

wrapper <- do.call(
  swipeRwrapper,
  lapply(files, function(x) {
    htmltools::tags$div(
      class = "swiper-zoom-container",
      htmltools::tags$img(
        src = x,
        style = "width:100%; height:auto; display:block; margin:0 auto;"
      )
    )
  })
)

htmltools::div(
  style = "max-width: 700px; margin: 0 auto;",
  swipeR(
    wrapper = wrapper,
    width = "100%",
    height = "800px",
    zoom = TRUE,
    navigationColor = "black",
    paginationColor = "black"
  )
)

```

<!-- RELATED:BEGIN -->
## Related notes
- [[siop-2026-reflection|SIOP through the wisdom of crowds: What I may have missed]]
- [[siop-2025-conference-events|What topics might you encounter at the SIOP 2025 conference?]]
- [[siop-2026-causal-inference-workshop|No Experiment, No Problem? Causal Inference in Applied Quasi-Experimental Settings (Session ID 830)]]
- [[cv-job-match-career-site|Improving a company career site with tools from OpenAI]]
- [[searching-and-querying-aihr-blog-posts|Searching & querying AIHR blog posts on People Analytics topics]]
<!-- RELATED:END -->

---
> 📄 Read the [original post with full outputs](https://blog-about-people-analytics.netlify.app/posts/2026-04-18-siop-2026-recommender/) on my blog.
