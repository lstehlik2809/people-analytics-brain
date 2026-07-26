---
title: Kohonen's Self-Organizing Maps
description: A brief demonstration of an awesome tool for exploring multidimensional data, using personality and work-life satisfaction data.
date: '2024-08-21'
tags:
- data-visualization
- data-science
- machine-learning
- personality
- big-five
- work-life-balance
original: https://blog-about-people-analytics.netlify.app/posts/2024-08-21-kohonen-self-organizing-maps/
---

Recently, I needed to explore the interactions of several variables in relation to a variable of interest, and I was wondering what tool could help me, until I remembered that in the distant past I had used [Kohonen's Self-Organizing Maps (SOMs)](https://en.wikipedia.org/wiki/Self-organizing_map) in such situations - an artificial neural network designed for unsupervised learning that relies on competitive learning mechanism to preserve topological properties of high-dimensional data and map them onto a lower-dimensional grid for visualization and clustering.

To illustrate, I applied it to a piece of data collected by [Clearer Thinking](https://www.clearerthinking.org/), which used it to compare the [predictive performance of different popular personality test frameworks in relation to various life outcomes](https://www.clearerthinking.org/post/how-accurate-are-popular-personality-test-frameworks-at-predicting-life-outcomes-a-detailed-investi). Specifically, I tried to explore the relationship between [Big Five traits](https://en.wikipedia.org/wiki/Big_Five_personality_traits) and work-life satisfaction. 

```r
# loading necessary libraries
library(tidyverse)
library(kohonen)
library(gridExtra)

# uploading data
data <- readr::read_csv('big5_mbti-stlye_astrologicalSigns_enneagramTypes_outcome_variables.csv')

# data preparation
mydata <- data %>% 
  dplyr::select(contains("Big5"), outcome_SatisfiedWithWorkLife ) %>% 
  tidyr::drop_na() %>% 
  dplyr::rename(
    Extraversion = Big5_E,
    Openness = Big5_O,
    Agreeableness = Big5_A,
    Conscientiousness = Big5_C,
    Neuroticism = Big5_N,
    "Work-Life Satisfaction" = outcome_SatisfiedWithWorkLife
  )

# normalize the data
data_scaled <- mydata %>%
  dplyr::mutate(across(everything(), ~scale(.)))

# creating a matrix for SOM function
data_matrix <- as.matrix(data_scaled)
data_matrix <- apply(data_matrix, 2, as.numeric)

# keeping the original names of the vars
colnames(data_matrix) <- colnames(data_scaled)

# creating a SOM grid with hexagonal topology 20x20
som_grid <- kohonen::somgrid(xdim = 20, ydim = 20, topo = "hexagonal")

# training the SOM 
set.seed(2024)
som_model <- kohonen::som(
  data_matrix, 
  grid = som_grid, 
  rlen = 5000, 
  alpha = c(0.05, 0.01), 
  keep.data = TRUE
)

# plotting the SOM using ggplot
# SOM with hexagonal cells using ggplot

# function to create hexagonal coordinates
hex_coords <- function(x, y) {
  r <- 1 / sqrt(3)  # the radius of a hexagon
  angles <- seq(0, 2*pi, length.out = 7)  # angles for hexagon vertices
  data.frame(
    x = x + r * cos(angles),
    y = y + r * sin(angles)
  )
}

# defining a blue-to-red color palette
blue_to_red_palette <- colorRampPalette(c("blue", "white", "red"))

# creating a list to store ggplot objects
plots <- list()

# generating the component planes for each variable and store them as ggplot objects
for(i in 1:ncol(data_matrix)){
  # extracting the component plane data
  plane_data <- data.frame(
    x = rep(1:som_grid$xdim, each = som_grid$ydim),
    y = rep(1:som_grid$ydim, som_grid$xdim),
    z = getCodes(som_model)[,i]
  )
  
  # creating hexagon coordinates for each tile
  hex_list <- lapply(1:nrow(plane_data), function(j) {
    hex_coords(plane_data$x[j], plane_data$y[j])
  })
  
  # combining all hexagons into one data frame
  hex_data <- do.call(rbind, hex_list)
  hex_data$z <- rep(plane_data$z, each = 7)
  hex_data$group <- rep(1:nrow(plane_data), each = 7)
  
  # creating a ggplot object with hexagons
  p <- ggplot2::ggplot(hex_data, aes(x = x, y = y, group = group, fill = z)) +
    ggplot2::geom_polygon() +
    ggplot2::scale_fill_gradientn(colors = blue_to_red_palette(100)) +
    ggplot2::coord_fixed() +
    ggplot2::labs(
      title = colnames(data_matrix)[i], 
      fill = "Value"
    ) +
    ggplot2::theme_minimal() +
    ggplot2::theme(
      axis.text = element_blank(),
      axis.title = element_blank(), 
      panel.grid = element_blank(),
      plot.title = element_text(hjust = 0.5)
    )
  
  plots[[i]] <- p
}

# arranging the plots in a 2x3 grid
gridExtra::grid.arrange(grobs = plots, nrow = 2, ncol = 3)



# an alternative and easier SOM visualization
# par(mfrow = c(2, 3))
# par(cex.main = 1.5) 
# for(i in 1:ncol(data_matrix)){
#   plot(som_model, type = "property", property = getCodes(som_model)[,i],
#        main = colnames(data_matrix)[i], shape = "straight", palette.name = blue_to_red_palette)
# }
# dev.off()
# # resetting the layout to default
# par(mfrow = c(1, 1), cex.main = 1)


```

The maps clearly show that satisfaction with work-life is strongly associated with Extraversion (positively), Neuroticism (negatively), and Conscientiousness (positively), and only weakly—if at all—with Openness and Agreeableness (both positively). More importantly, however, we can also check various “exceptions” to these bivariate patterns by looking at the same specific locations across all maps. For example, one can observe a group of individuals with higher Neuroticism (in the lower left corner) who nevertheless report greater work-life satisfaction—possibly due to higher levels of Extraversion, Conscientiousness, and, to some extent, Openness and Agreeableness. That's something that wouldn't be possible to find out from the pairwise plots that are usually used for similar data exploration. Check it out for yourself below.

```r
# exploring the data in the pairplot
library(GGally)

GGally::ggpairs(
  mydata,
  lower = list(continuous = GGally::wrap("smooth", alpha = 0.3)),
  diag = list(continuous = GGally::wrap("densityDiag", fill = "grey"))
) +
ggplot2::theme_minimal()


```

If you find yourself in a similar situation, definitely give it a try. Happy exploration(s) 🙂

<!-- RELATED:BEGIN -->
## Related notes
- [[dimensional-traits-vs-personality-types|Dimensional Traits vs. Personality Types]]
- [[personality-and-non-linearities|Nonlinear relationships between personality traits and business outcomes seem to be the norm rather than the exception]]
- [[personas-based-on-ml-local-interpretation-algos|Personas based on ML local interpretation algorithms]]
- [[team-maps|Experiencing and seeing team similarities and differences]]
- [[latent-class-analysis|Latent Class Analysis of responses from employee surveys]]
<!-- RELATED:END -->

---
> 📄 Read the [original post with full outputs](https://blog-about-people-analytics.netlify.app/posts/2024-08-21-kohonen-self-organizing-maps/) on my blog.
