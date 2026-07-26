---
title: 'NetLogo: Don’t tell me, show me'
description: An example of how to get a better understanding of various complex phenomena through simulation in NetLogo, a free programmable multi-agent modelling environment.
date: '2024-04-28'
tags:
- simulation
- learning-and-development
original: https://blog-about-people-analytics.netlify.app/posts/2024-04-28-netlogo/
---

Recently, my 10-year-old son came across the concept of the [exploration vs. exploitation dilemma](https://en.wikipedia.org/wiki/Exploration-exploitation_dilemma) in one of his books and wanted me to help him understand it.

I got quite sweaty in explaining it before I remembered [NetLogo](https://ccl.northwestern.edu/netlogo/), which contains a series of pre-programmed simulations of various multi-agent systems and emergent phenomena. 

One of them shows how this particular dilemma is solved by a colony of ants foraging for food using a very simple but effective system of rules:  

1. **Random Exploration:** Ants explore randomly, ensuring the discovery of new resources.
2. **Pheromone Trails:** When an ant finds a piece of food, it carries the food back to the nest, dropping a chemical as it moves. When other ants "sniff" the chemical, they follow the chemical toward the food. As more ants carry food to the nest, they reinforce the chemical trail, focusing on exploitation.
3. **Pheromone Decay:** Trails weaken over time, prompting exploration when resources dwindle.

<div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden;">
  <video controls style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;">
    <source src="netlogo-ants-colony.mp4" type="video/mp4">
    Your browser does not support the video tag.
  </video>
</div>
<br>

After watching a few rounds of the simulation and a brief explanation, everything became much clearer to my son. If you are ever faced with similar types of questions, give NetLogo a chance. It's free to use, contains a number of pre-programmed simulations, and if you don't find what you're looking for there, it's not hard to learn how to program what you need in NetLogo.

Btw, I can't wait for my son to stumble upon the topic of how order can arise without some central controlling authority - there's a very effective bird flocking simulation in NetLog for that 😉

<!-- RELATED:BEGIN -->
## Related notes
- [[dunning-kruger-effect-simulation|Making abstract ideas digestible with knobs and sliders]]
- [[exploration-vs-exploitation-tradeoff|Exploration vs. Exploitation trade-off in our calendars]]
- [[kohonen-self-organizing-maps|Kohonen's Self-Organizing Maps]]
- [[bayesian-belief-updating|A visual introduction to Bayesian belief updating]]
- [[ai-powered-data-exploration-assistant|Testing my GenAI skepticism]]
<!-- RELATED:END -->

---
> 📄 Read the [original post with full outputs](https://blog-about-people-analytics.netlify.app/posts/2024-04-28-netlogo/) on my blog.
