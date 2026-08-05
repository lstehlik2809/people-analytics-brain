---
title: An interactive demo of Computerized Adaptive Testing
description: Sharing a byproduct of my recent efforts to learn Streamlit—an interactive demo that might be useful for anyone teaching psychometrics or simply curious about how modern psychometrics (relatively speaking 😉) works.
date: '2025-06-02'
tags:
- psychometrics
- bayesian-statistics
- python
original: https://blog-about-people-analytics.netlify.app/posts/2025-06-02-cat-and-irt-demo/
---

Specifically, I decided to reimplement in [Streamlit](https://streamlit.io/) a [Computerized Adaptive Testing (CAT)](https://en.wikipedia.org/wiki/Computerized_adaptive_testing) and [Item Response Theory (IRT)](https://en.wikipedia.org/wiki/Item_response_theory) demo I originally built years ago in good old Excel. 

The app illustrates the estimation of a psychological trait of [learning agility](https://psycnet.apa.org/buy/2022-19273-004) and showcases several key ideas behind CAT and IRT-based testing:

* **Item-level modeling** – how individuals respond to questions is modeled based on both the characteristics of each item (e.g. difficulty, discrimination) and the test-taker’s underlying trait or ability.
* **Continuous ability estimation** – the app updates the trait estimate in a Bayesian way after each response, rather than only at the end of the test.
* **Adaptive item selection** – items are chosen based on how informative they are given the test-taker’s current estimated trait level.
* **Efficiency and precision** – fewer items are needed to reach a reliable estimate compared to traditional fixed-form tests.

<div style="text-align:center">

![](./cat-and-irt-demo/cat_irt_demo_app_screenshot.png)

</div>

Here’s the [link](https://cat-irt-demo.streamlit.app/) to the app (given that the app is hosted on Streamlit Community Cloud, it doesn’t stay awake all the time regardless of traffic—so if it hasn’t been used recently, you might need to wake it up and wait a few minutes). If you’re interested, you can copy the full code from [GitHub](https://github.com/lstehlik2809/Computerized-Adaptive-Testing-Demo.git) and customize the app to better suit your needs.

⚠️ Caveat: The app isn't intended as a valid and reliable measure of learning agility - it's purely for illustration purposes!

<!-- RELATED:BEGIN -->
## Related notes
- [[dimensional-traits-vs-personality-types|Dimensional Traits vs. Personality Types]]
- [[agentic-ai-for-visual-data-exploration|Agentic AI for visual data exploration]]
- [[detecting-personality-in-the-face|Can a simple algorithm read your personality from your face?]]
- [[dunning-kruger-effect-simulation|Making abstract ideas digestible with knobs and sliders]]
- [[evidence-based-hrm-knowledge-test|Evidence-based HRM knowledge test]]
<!-- RELATED:END -->

---
> 📄 Read the [original post with full outputs](https://blog-about-people-analytics.netlify.app/posts/2025-06-02-cat-and-irt-demo/) on my blog.
