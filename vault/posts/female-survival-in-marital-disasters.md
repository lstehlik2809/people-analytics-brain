---
title: Women, men, and sixteen sinking ships
description: A reproducible reanalysis of Elinder & Erixson (2012).
date: '2026-08-06'
tags:
- statistics
- causal-inference
- research-methods
- multilevel-modeling
- regression-analysis
- critical-thinking
- r
- replication
- open-science
original: https://blog-about-people-analytics.netlify.app/posts/2026-08-06-female-survival-in-marital-disasters/
---

```r
knitr::opts_chunk$set(
  echo = TRUE, message = FALSE, warning = FALSE,
  fig.width = 8, fig.height = 5, dpi = 120
)
suppressWarnings(suppressPackageStartupMessages({
  library(readxl); library(dplyr); library(tidyr); library(purrr)
  library(stringr); library(fixest); library(ggplot2)
  library(fwildclusterboot); library(knitr); library(kableExtra)
}))
setFixest_notes(FALSE)
options(knitr.kable.NA = "")
# Cluster-robust t-tests are referred to a t distribution with G - 1 degrees of
# freedom (G = number of ships), not the large-sample normal. This is fixest's
# default and the appropriate choice with 7-16 clusters; it is used for every
# clustered model in this document.
cluster_ssc <- ssc(t.df = "min")
navy <- "#17365D"; blue <- "#2B6CB0"; rust <- "#B55432"; sand <- "#D9C7A3"
theme_ship <- theme_minimal(base_size = 12) +
  theme(panel.grid.minor = element_blank(), plot.title.position = "plot",
        plot.title = element_text(face = "bold", size = 14),
        plot.subtitle = element_text(color = "#4B5563"),
        axis.title = element_text(color = "#374151"),
        legend.position = "bottom", strip.text = element_text(face = "bold"))
theme_set(theme_ship)
fmt_p <- function(x) ifelse(x < .001, "< 0.001", sprintf("%.3f", x))
# Two-sided 95% critical value on the reference distribution the model itself
# uses: n - K for robust fits, G - 1 for ship-clustered ones.
crit95 <- function(model) qt(.975, degrees_freedom(model, type = "t"))
model_row <- function(model, term, label, inference) {
  b <- unname(coef(model)[term]); s <- unname(se(model)[term])
  pv <- unname(pvalue(model)[term])
  tibble(term = label, estimate = b, se = s, p = pv, inference = inference,
         crit = crit95(model))
}
ci_text <- function(model, term, digits = 3) {
  b <- unname(coef(model)[term]); s <- unname(se(model)[term]); tc <- crit95(model)
  sprintf(paste0("[%+.", digits, "f, %+.", digits, "f]"), b - tc * s, b + tc * s)
}
term_labels <- c(
  female = "Female", crew = "Crew",
  `female:wcf` = "Female × recorded WCF order",
  `female:quick` = "Female × quick sinking",
  `female:smallshare` = "Female × small female share",
  `female:voyage1` = "Female × voyage over one day",
  `female:post_wwi` = "Female × post-WWI",
  `female:british` = "Female × British-registered ship"
)
joint_term_label <- function(term) {
  label <- unname(term_labels[term])
  ifelse(term %in% c("female", "crew"), paste0(label, " (joint)"), label)
}
```

# The Titanic prior

For many people in my network the word *Titanic* brings to mind not James Cameron’s film, but the passenger manifest they encountered as one of their first datasets while trying to break into the field. Kaggle’s famous [“Titanic: Machine Learning from Disaster”](https://www.kaggle.com/competitions/titanic) has served as a beginner competition for more than a decade, while versions of the dataset appear in introductory courses built around R, Python, and Stata.

<div style="text-align:center">

![](./female-survival-in-marital-disasters/become-data-scientist.png)

</div>

The standard modelling exercise is familiar: fit a logistic regression using variables such as sex, passenger class, and age. One coefficient tends to dwarf the others. Women survived; men, for the most part, did not.

The model merely quantified a story already firmly lodged in the public imagination: officers lowering women and children into lifeboats while men stoically stood back. But that is just one ship. This post begins with a simple question: what happens when someone adds seventeen more?

That is exactly what Mikael Elinder and Oscar Erixson did in a 2012 [PNAS paper](https://doi.org/10.1073/pnas.1207156109). They compiled an unusually large individual-level dataset covering 18 maritime disasters between 1852 and 2011: more than 15,000 people, each linked, where possible, to their sex, passenger or crew status, and survival outcome.

The results overturned the Titanic-shaped prior. Across the other disasters, the authors report, women survived at roughly half the rate of men. Crew members fared better than passengers. Elinder and Erixson summarised the pattern with deliberate bluntness: “every man for himself.” I take that “roughly half” at face value for now, and come back at the end to where the figure behind it comes from, because it is a slipperier number than it looks.

While reading the paper, two broader thoughts and questions came to mind:

1. The explanations proposed by the authors vary by ship, but the outcomes are recorded person by person. Anyone who has run a geo experiment, a market rollout, or a team-level intervention will recognise the problem. I was therefore curious to see which claims would survive once uncertainty was measured at the ship level - and how robust those claims might be given the small number of ships. 
2. The authors’ summary seems to turn the Titanic’s story of chivalry on its head. But what does the observed female survival gap actually mean when sex appears to bundle together social treatment and physical capacity? 

Fortunately, the authors made their `r xfun::embed_file("data/sd01.xlsx", text = "data publicly available")`, so I did not have to stop at asking these questions - I could try to answer them. But before getting to that, let’s reproduce the paper’s original numbers and make sure we are playing on the same field.

# Reproducing the paper's numbers

```r
path <- file.path("data", "sd01.xlsx")
ship_sheets <- excel_sheets(path)[3:20]

read_ship <- function(sheet) {
  x <- read_excel(path, sheet = sheet, na = ".", col_types = "text")
  names(x) <- trimws(names(x))
  names(x)[str_detect(names(x), "^Id_\\d+$")] <- "id"
  numeric_cols <- c(
    "Ship Id", "Year", "Women and children first", "Quick",
    "No. of passengers", "No. of women passengers",
    "Women passengers/passengers", "Ship size", "Length of voyage",
    "Gender", "Age", "Child", "Crew", "Survival"
  )
  x %>% mutate(across(any_of(numeric_cols), ~ suppressWarnings(as.numeric(.x))),
               ship = sheet)
}

raw <- map_dfr(ship_sheets, read_ship)
d <- raw %>% mutate(
  female = Gender, crew = Crew, surv = Survival,
  wcf = `Women and children first`, quick = Quick,
  british = as.integer(str_to_upper(str_trim(`Nationality of the Ship`)) %in%
                         c("U.K", "UK", "BRITISH")),
  post_wwi = as.integer(Year > 1915),
  smallshare = as.integer(`Women passengers/passengers` < .368),
  voyage1 = as.integer(`Length of voyage` > 1)
)

ms_h1 <- d %>% filter(!ship %in% c("RMS Titanic", "RMS Lusitania"),
                      !is.na(surv), !is.na(female))
ms <- d %>% filter(!ship %in% c("RMS Titanic", "RMS Lusitania"),
                   !is.na(surv), !is.na(female), !is.na(crew)) %>%
  group_by(ship) %>% mutate(w = 1 / n()) %>% ungroup()

titanic <- d %>% filter(ship == "RMS Titanic", !is.na(surv))
stopifnot(nrow(titanic) > 0,
          !anyNA(titanic[c("surv", "female")]),
          setequal(unique(titanic$female), c(0, 1)),
          sum(titanic$female == 1) == 486,
          all(is.na(titanic$Child)))
titanic_rates <- titanic %>%
  summarise(women = mean(surv[female == 1]),
            men = mean(surv[female == 0]))
```


The workbook has 21 sheets: 18 ships plus the dictionary, sources, and captain outcomes. A period means missing. Column names carry stray spaces, each ship uses a different `Id_` suffix, Britain is coded `U.K`, and the wreck the paper's Table 1 styles *RMS Atlantic* sails here under the sheet name *SS Atlantic*. Any of those details can quietly spoil a replication.

The paper's main sample excludes the *Titanic* and *Lusitania* because those wrecks helped generate the hypotheses being tested. I follow that choice. In the full workbook, `r sum(is.na(d$surv))` rows have no survival outcome, and `r sum(!d$ship %in% c('RMS Titanic', 'RMS Lusitania') & !is.na(d$surv) & is.na(d$female))` main-sample records have an outcome but no recorded sex. Both drop out when survival is regressed on sex, leaving `r format(nrow(ms_h1), big.mark = ',')` people on `r n_distinct(ms_h1$ship)` ships. The joint model has `r format(nrow(ms), big.mark = ',')` rows because two more records lack crew status.

The paper did more than compare women with men: it asked whether ship-level conditions changed the female–male survival gap. Two of those conditions matter repeatedly below. A women-and-children-first (WCF) order means that the historical record says the captain explicitly gave that order; the authors expected it to enforce priority for women and make their survival gap relative to men more favorable. A British ship means a vessel registered in Britain. Drawing on the idea that chivalry at sea was particularly associated with British culture, the authors expected women to fare relatively better on those ships. The model tests both ideas through interactions with sex: a positive coefficient means that the female–male gap shifts toward women under that condition; a negative coefficient means that it shifts further toward men. These are changes in the sex gap, not effects on everyone aboard.

```r
h1_robust <- feols(surv ~ female | ship, data = ms_h1, vcov = "hetero")
h2_robust <- feols(surv ~ female + crew | ship, data = ms, vcov = "hetero")
joint_fml <- surv ~ female + crew + female:wcf + female:quick +
  female:smallshare + female:voyage1 + female:post_wwi +
  female:british | ship
joint_robust <- feols(joint_fml, data = ms, weights = ~w, vcov = "hetero")

targets <- c(female = -.1794, `female:wcf` = .0963,
             `female:quick` = .0326, `female:smallshare` = -.0501,
             `female:voyage1` = .0266, `female:post_wwi` = .0730,
             `female:british` = -.1013, crew = .1609)
stopifnot(abs(coef(h1_robust)["female"] - (-.1670)) < .001,
          abs(se(h1_robust)["female"] - .0083) < .001,
          abs(coef(h2_robust)["crew"] - .1868) < .001,
          all(abs(coef(joint_robust)[names(targets)] - targets) < .001))
replication <- bind_rows(
  model_row(h1_robust, "female", "Female", "Robust"),
  model_row(h2_robust, "crew", "Crew", "Robust"),
  map_dfr(names(targets), ~ model_row(joint_robust, .x,
                                      joint_term_label(.x),
                                      "Joint, robust"))
) %>% rename(Model = inference) %>% select(Model, term, estimate, se, p) %>%
  mutate(estimate = sprintf("%.3f", estimate),
         se = sprintf("%.4f", se), p = fmt_p(p))
kable(replication, col.names = c("Model", "Term", "Estimate", "SE", "p"),
      align = c("l", "l", "r", "r", "r")) %>%
  kable_styling(full_width = FALSE, bootstrap_options = "striped")
```

```r
# A ship-fixed-effects logit is estimable here, so the LPM is not a fallback:
# no wreck is all-survivors or all-dead, and with one pooled sex coefficient the
# Atlantic's all-dead women do not separate the likelihood.
fe_logit <- glm(surv ~ female + factor(ship), data = ms_h1, family = binomial)
ship_rates <- tapply(ms_h1$surv, ms_h1$ship, mean)
stopifnot(fe_logit$converged, nobs(fe_logit) == nrow(ms_h1),
          all(is.finite(coef(fe_logit))), max(abs(coef(fe_logit))) < 5,
          max(sqrt(diag(vcov(fe_logit)))) < 1,
          !any(ship_rates %in% c(0, 1)),
          nobs(feglm(surv ~ female | ship, data = ms_h1,
                     family = binomial)) == nrow(ms_h1))
```

These are linear probability models with ship fixed effects, following the paper. It is worth being clear about why, because the obvious justification is wrong: a ship-fixed-effects logit is perfectly estimable on this sample. No wreck is all-survivors or all-dead, and with a single pooled sex coefficient the *Atlantic*'s 235 women, none of whom lived, do not separate the likelihood - that model converges with every record retained and every coefficient bounded. I use the LPM because it reproduces the paper and because the rest of this post needs differences in survival probability rather than log-odds. (A wreck-specific sex effect would separate: in a `female × ship` model the *Atlantic*'s term is unbounded. Nothing below asks for one.)

Every checkpoint lands within one-thousandth of the published number. The female coefficient is `r sprintf('%.3f', coef(h1_robust)['female'])`: within the same wreck, female survival was 16.7 percentage points lower. The crew coefficient is `r sprintf('%.3f', coef(h2_robust)['crew'])`, or 18.7 percentage points higher after accounting for sex and ship. In the joint specification, a recorded WCF order shifts the female–male gap by `r sprintf('%+.3f', coef(joint_robust)['female:wcf'])`, in the direction predicted by the captain-enforcement hypothesis. The British-ship interaction is `r sprintf('%+.3f', coef(joint_robust)['female:british'])`: women fare relatively worse, not better, on British-registered ships - the opposite of the paper's British-chivalry hypothesis. On the paper's standard errors, both have p below 0.050.

The thin fields need care. Age is recorded on `r n_distinct(d$ship[!is.na(d$Age)])` ships overall; `r n_distinct(ms$ship[!is.na(ms$Age)])` of them belong to the sixteen-ship main sample, because the other two are the excluded *Titanic* and *Lusitania*. If you cross-check against the paper, its Figure 1 counts nine main-sample wrecks with children's data, and the ledger reconciles: the *Golden Gate* and the *Vestris* flag who is a child without recording an age, so they join the paper's count but sit out any analysis that needs age itself. Passenger nationality exists on `r n_distinct(d$ship[!is.na(d[['Nationality of Passenger']])])` ships and companionship on `r n_distinct(d$ship[!is.na(d$Companionship)])`. Four ships can't identify a nationality pattern; three can't identify a companionship pattern. Neither is used below. Age is thin too, but it comes back later for one specific job.

```r
age_ships_all <- unique(d$ship[!is.na(d$Age)])
age_ships_main <- unique(ms$ship[!is.na(ms$Age)])
stopifnot(length(age_ships_all) == 9, length(age_ships_main) == 7,
          setequal(setdiff(age_ships_all, age_ships_main),
                   c("RMS Titanic", "RMS Lusitania")),
          all(is.na(d$Age[d$ship %in% c("SS Golden Gate", "SS Vestris")])),
          all(c("SS Golden Gate", "SS Vestris") %in%
                unique(ms$ship[!is.na(ms$Child)])),
          n_distinct(ms$ship[!is.na(ms$Age) | !is.na(ms$Child)]) == 9)
```

```r
missing_sex <- d %>% group_by(ship) %>% summarise(
  unknown_sex = sum(is.na(female)),
  unknown_survival = mean(surv[is.na(female)], na.rm = TRUE),
  recorded_survival = mean(surv[!is.na(female)], na.rm = TRUE), .groups = "drop"
) %>% filter(unknown_sex > 0) %>% mutate(
  unknown_survival = if_else(is.nan(unknown_survival), NA_real_, unknown_survival)
)
stopifnot(missing_sex$unknown_sex[missing_sex$ship == "SS Arctic"] == 78,
          missing_sex$unknown_sex[missing_sex$ship == "SS Princess Alice"] == 61)
```

Historical records add a stranger data-quality problem. The workbook contains `r sum(is.na(d$female))` people without recorded sex, but the pattern matters more than the count. On the *Arctic*, `r missing_sex$unknown_sex[missing_sex$ship == 'SS Arctic']` people are unrecorded and `r scales::percent(missing_sex$unknown_survival[missing_sex$ship == 'SS Arctic'], accuracy = .1)` survived, against `r scales::percent(missing_sex$recorded_survival[missing_sex$ship == 'SS Arctic'], accuracy = .1)` among the recorded. Those are mostly the dead, reconstructed from an uncertain passenger list. On the *Princess Alice*, the unrecorded are mostly the living: `r scales::percent(missing_sex$unknown_survival[missing_sex$ship == 'SS Princess Alice'], accuracy = .1)` survived, against `r scales::percent(missing_sex$recorded_survival[missing_sex$ship == 'SS Princess Alice'], accuracy = .1)` among the recorded, because newspaper survivor lists named people the drowned records missed. Same missing-data label, opposite selection, both produced by how the archive was made.

```r
mm_bound <- d %>% filter(!ship %in% c("RMS Titanic", "RMS Lusitania"), !is.na(surv))
miss_idx <- which(is.na(mm_bound$female))
sid <- match(mm_bound$ship, unique(mm_bound$ship))
ns <- tabulate(sid); ysum <- rowsum(mm_bound$surv, sid)[, 1]
fe_coef <- function(f) {
  fm <- rowsum(f, sid)[, 1] / ns
  (sum(f * mm_bound$surv) - sum(fm * ysum)) / (sum(f) - sum(ns * fm^2))
}
assign_coef <- function(fill) { f <- mm_bound$female; f[miss_idx] <- fill; fe_coef(f) }
bounds <- tibble(
  Assignment = c("All unknown male", "All unknown female",
                 "Unknown deaths female, survivors male",
                 "Unknown deaths male, survivors female"),
  estimate = c(assign_coef(0), assign_coef(1),
               assign_coef(as.integer(mm_bound$surv[miss_idx] == 0)),
               assign_coef(as.integer(mm_bound$surv[miss_idx] == 1)))
)

# The within-ship coefficient is a ratio of sums that depend on the assignment
# only through each ship's counts of unknown survivors (a) and unknown deaths (b)
# labeled female. That collapses 2^301 assignments onto small per-ship grids, so
# the extremes can be found exactly with a Dinkelbach iteration on the ratio.
bound_stats <- mm_bound %>% group_by(ship) %>% summarise(
  n = n(), Y = sum(surv), F1y = sum(female * surv, na.rm = TRUE),
  F1 = sum(female, na.rm = TRUE),
  A = sum(is.na(female) & surv == 1), B = sum(is.na(female) & surv == 0),
  .groups = "drop")
bound_grids <- pmap(bound_stats %>% select(n, Y, F1y, F1, A, B),
                    function(n, Y, F1y, F1, A, B) {
  g <- expand.grid(a = 0:A, b = 0:B); Fm <- F1 + g$a + g$b
  data.frame(a = g$a, b = g$b,
             num = F1y + g$a - Fm * Y / n, den = Fm - Fm^2 / n)
})
select_bound_grid <- function(sense, t) {
  map2_dfr(bound_grids, bound_stats$ship, function(g, ship) {
    objective <- g$num - t * g$den
    idx <- if (sense < 0) which.min(objective) else which.max(objective)
    data.frame(ship, g[idx, c("a", "b", "num", "den")], row.names = NULL)
  })
}
dinkelbach <- function(sense, t0, tol = 1e-13) {
  t <- t0
  for (iter in 1:100) {
    chosen <- select_bound_grid(sense, t)
    denominator <- sum(chosen$den)
    if (!is.finite(denominator) || denominator <= 0) {
      stop("Non-positive denominator in Dinkelbach iteration")
    }
    t_new <- sum(chosen$num) / denominator
    if (abs(t_new - t) < tol) {
      final <- select_bound_grid(sense, t_new)
      final_denominator <- sum(final$den)
      if (!is.finite(final_denominator) || final_denominator <= 0) {
        stop("Non-positive denominator in Dinkelbach certificate")
      }
      residual <- sum(final$num - t_new * final$den)
      if (abs(residual) < tol) {
        return(list(
          value = t_new,
          assignments = final %>% select(ship, a, b),
          residual = residual,
          denominator = final_denominator,
          iterations = iter,
          start = t0
        ))
      }
    }
    t <- t_new
  }
  stop("Dinkelbach iteration failed to converge")
}
bound_starts <- c(-.5, -.2, 0, .2, .5)
lo_runs <- map(bound_starts, ~ dinkelbach(-1, .x))
hi_runs <- map(bound_starts, ~ dinkelbach(1, .x))
global_lo_result <- lo_runs[[1]]
global_hi_result <- hi_runs[[1]]
global_lo <- global_lo_result$value
global_hi <- global_hi_result$value

bound_assignment_table <- bound_stats %>% select(ship, A, B) %>%
  left_join(global_lo_result$assignments %>% rename(lo_a = a, lo_b = b), by = "ship") %>%
  left_join(global_hi_result$assignments %>% rename(hi_a = a, hi_b = b), by = "ship")
```

```r
check_uniform <- feols(
  surv ~ female_bound | ship,
  data = mutate(mm_bound, female_bound = if_else(is.na(female), 0, female)),
  vcov = ~ship, ssc = cluster_ssc
)
# The bound above is on the point estimate. Refitting at the two optimizing
# corners with ship-clustered errors does NOT bound the interval, because the
# completion that extremizes the coefficient need not extremize a confidence
# limit - the clustered standard error moves with the assignment too. Both are
# computed below: the corner pair for reference, then a direct search on the
# endpoints themselves.
corner_fit <- function(rule) feols(
  surv ~ fb | ship,
  data = mutate(mm_bound, fb = if_else(is.na(female), as.integer(rule), female)),
  vcov = ~ship, ssc = cluster_ssc
)
lo_corner_fit <- corner_fit(mm_bound$surv == 0)
hi_corner_fit <- corner_fit(mm_bound$surv == 1)
corner_union <- c(confint(lo_corner_fit)["fb", 1], confint(hi_corner_fit)["fb", 2])
all_runs <- c(lo_runs, hi_runs)
stopifnot(length(miss_idx) == 301,
          sum(mm_bound$surv[miss_idx] == 1) == 99,
          abs(coef(check_uniform)["female_bound"] - bounds$estimate[1]) < 1e-10,
          abs(bounds$estimate[1] - (-.170)) < .001,
          abs(bounds$estimate[2] - (-.157)) < .001,
          abs(global_lo - bounds$estimate[3]) < 1e-12,
          abs(global_hi - bounds$estimate[4]) < 1e-12,
          abs(global_lo_result$residual) < 1e-12,
          abs(global_hi_result$residual) < 1e-12,
          all(map_dbl(all_runs, "denominator") > 0),
          max(abs(map_dbl(lo_runs, "value") - global_lo)) < 1e-12,
          max(abs(map_dbl(hi_runs, "value") - global_hi)) < 1e-12,
          all(global_lo_result$assignments$a == 0),
          all(global_lo_result$assignments$b == bound_stats$B),
          all(global_hi_result$assignments$a == bound_stats$A),
          all(global_hi_result$assignments$b == 0),
          abs(global_lo - (-.18598)) < 1e-4,
          abs(global_hi - (-.13949)) < 1e-4,
          abs(coef(lo_corner_fit)["fb"] - global_lo) < 1e-10,
          abs(coef(hi_corner_fit)["fb"] - global_hi) < 1e-10,
          degrees_freedom(lo_corner_fit, type = "t") == 15,
          corner_union[1] > -.30, corner_union[2] < -.06)

bound_certificate <- tibble(
  Extreme = c("Minimum", "Maximum"),
  Estimate = c(global_lo, global_hi),
  `Corner estimate` = bounds$estimate[c(3, 4)],
  `Optimality residual` = c(global_lo_result$residual, global_hi_result$residual),
  Denominator = c(global_lo_result$denominator, global_hi_result$denominator),
  Iterations = c(global_lo_result$iterations, global_hi_result$iterations)
) %>% mutate(
  across(c(Estimate, `Corner estimate`), ~ sprintf("%.3f", .x)),
  `Optimality residual` = sprintf("%.2e", `Optimality residual`),
  Denominator = sprintf("%.6f", Denominator)
)
kable(bound_certificate, align = c("l", "r", "r", "r", "r", "r"),
      caption = paste("Exact missing-sex optimization certificate;",
                      length(bound_starts), "starting values checked for each extreme.")) %>%
  kable_styling(full_width = FALSE, bootstrap_options = "striped")
```

```r
# The clustered variance depends on the assignment only through each ship's
# (num, den) pair, exactly as the point estimate does, so the same per-ship grids
# support a direct search on the interval endpoints. The CR1 scaling is read off
# one fixest fit and the winning completion is re-fitted to confirm it.
G_bound <- nrow(bound_stats); t_bound <- qt(.975, G_bound - 1)
bound_stat <- function(sel, scale) {
  nu <- map_dbl(seq_len(G_bound), ~ bound_grids[[.x]]$num[sel[.x]])
  de <- map_dbl(seq_len(G_bound), ~ bound_grids[[.x]]$den[sel[.x]])
  b <- sum(nu) / sum(de)
  c(est = b, se = sqrt(scale * sum((nu - b * de)^2) / sum(de)^2))
}
sel_for <- function(a, b) map_int(seq_len(G_bound), function(i)
  which(bound_grids[[i]]$a == a[i] & bound_grids[[i]]$b == b[i]))
hi_sel <- sel_for(bound_stats$A, rep(0L, G_bound))
lo_sel <- sel_for(rep(0L, G_bound), bound_stats$B)
cr1_scale <- unname(se(hi_corner_fit)["fb"]^2 / bound_stat(hi_sel, 1)[["se"]]^2)
bound_ci <- function(sel) {
  s <- bound_stat(sel, cr1_scale)
  c(lo = s[["est"]] - t_bound * s[["se"]], hi = s[["est"]] + t_bound * s[["se"]])
}
# Both endpoints depend on the assignment only through five additive sums, since
# sum((num - b*den)^2) = Q1 - 2*b*Q2 + b^2*Q3. That makes a whole ship's grid
# evaluable in one vectorized pass: hold the other fifteen ships' contributions
# fixed and sweep every (a, b) this ship allows at once.
sums_of <- function(sel) {
  nu <- map_dbl(seq_len(G_bound), ~ bound_grids[[.x]]$num[sel[.x]])
  de <- map_dbl(seq_len(G_bound), ~ bound_grids[[.x]]$den[sel[.x]])
  c(S1 = sum(nu), S2 = sum(de), Q1 = sum(nu^2), Q2 = sum(nu * de), Q3 = sum(de^2))
}
ship_sums <- function(i, sel) {
  nu <- bound_grids[[i]]$num[sel[i]]; de <- bound_grids[[i]]$den[sel[i]]
  c(S1 = nu, S2 = de, Q1 = nu^2, Q2 = nu * de, Q3 = de^2)
}
sweep_ship <- function(i, rest, end) {
  g <- bound_grids[[i]]
  S1 <- rest[["S1"]] + g$num; S2 <- rest[["S2"]] + g$den
  Q1 <- rest[["Q1"]] + g$num^2; Q2 <- rest[["Q2"]] + g$num * g$den
  Q3 <- rest[["Q3"]] + g$den^2
  b <- S1 / S2
  s <- sqrt(cr1_scale * (Q1 - 2 * b * Q2 + b^2 * Q3)) / S2
  if (end == "lo") b - t_bound * s else b + t_bound * s
}
# Coordinate ascent is a heuristic on a non-separable objective, so this
# establishes only that the union is AT LEAST this wide - which is what the
# argument needs, since one feasible completion outside the corner pair already
# shows the corner pair is not a coverage statement. Unlike the point-estimate
# bound above, no global optimality certificate is claimed for the endpoints.
endpoint_search <- function(sel, end, sense) {
  best <- bound_ci(sel)[[end]]
  repeat {
    moved <- FALSE
    for (i in seq_len(G_bound)) {
      if (nrow(bound_grids[[i]]) == 1) next
      cand <- sweep_ship(i, sums_of(sel) - ship_sums(i, sel), end)
      j <- if (sense > 0) which.max(cand) else which.min(cand)
      if (sense * cand[j] > sense * best + 1e-13) {
        sel[i] <- j; best <- cand[j]; moved <- TRUE
      }
    }
    if (!moved) break
  }
  list(sel = sel, value = best)
}
set.seed(101)
search_starts <- c(
  list(hi_sel, lo_sel, sel_for(bound_stats$A, bound_stats$B),
       sel_for(rep(0L, G_bound), rep(0L, G_bound))),
  map(1:400, ~ map_int(bound_grids, function(g) sample.int(nrow(g), 1)))
)
hi_search <- map(search_starts, endpoint_search, end = "hi", sense = 1)
lo_search <- map(search_starts, endpoint_search, end = "lo", sense = -1)
hi_restart_agree <- mean(map_dbl(hi_search, "value") >
                           max(map_dbl(hi_search, "value")) - 1e-9)
hi_best <- hi_search[[which.max(map_dbl(hi_search, "value"))]]
lo_best <- lo_search[[which.min(map_dbl(lo_search, "value"))]]
searched_union <- c(lo_best$value, hi_best$value)

# Re-fit the widening completion with fixest to confirm the analytic endpoint.
completion_fit <- function(sel) {
  a <- map_dbl(seq_len(G_bound), ~ bound_grids[[.x]]$a[sel[.x]])
  b <- map_dbl(seq_len(G_bound), ~ bound_grids[[.x]]$b[sel[.x]])
  f <- if_else(is.na(mm_bound$female), 0L, as.integer(mm_bound$female))
  for (i in seq_len(G_bound)) {
    s <- which(mm_bound$ship == bound_stats$ship[i] & is.na(mm_bound$female) &
                 mm_bound$surv == 1)
    dd <- which(mm_bound$ship == bound_stats$ship[i] & is.na(mm_bound$female) &
                  mm_bound$surv == 0)
    if (a[i] > 0) f[s[seq_len(a[i])]] <- 1L
    if (b[i] > 0) f[dd[seq_len(b[i])]] <- 1L
  }
  feols(surv ~ fb | ship, data = mutate(mm_bound, fb = f),
        vcov = ~ship, ssc = cluster_ssc)
}
hi_best_fit <- completion_fit(hi_best$sel)
hi_best_where <- bound_stats %>% select(ship, A, B) %>%
  mutate(a = map_dbl(seq_len(G_bound), ~ bound_grids[[.x]]$a[hi_best$sel[.x]]),
         b = map_dbl(seq_len(G_bound), ~ bound_grids[[.x]]$b[hi_best$sel[.x]])) %>%
  filter(A + B > 0, a != A | b != 0)
stopifnot(abs(cr1_scale - G_bound / (G_bound - 1)) < .001,
          abs(bound_ci(hi_sel)[["hi"]] - corner_union[2]) < 1e-9,
          abs(bound_ci(lo_sel)[["lo"]] - corner_union[1]) < 1e-9,
          length(search_starts) == 404, hi_restart_agree > .9,
          abs(confint(hi_best_fit)["fb", 2] - searched_union[2]) < 1e-9,
          searched_union[2] > corner_union[2] + .007,
          searched_union[1] <= corner_union[1] + 1e-9,
          searched_union[2] < -.05, searched_union[1] > -.30,
          nrow(hi_best_where) == 1, hi_best_where$ship == "SS Atlantic",
          hi_best_where$a == 0, hi_best_where$b == hi_best_where$B)
```

<details>
<summary>Per-ship optimizing assignments</summary>

```r
kable(bound_assignment_table %>% transmute(
  Ship = ship,
  `Unknown survivors` = A, `Unknown deaths` = B,
  `Minimum: survivors female` = lo_a, `Minimum: deaths female` = lo_b,
  `Maximum: survivors female` = hi_a, `Maximum: deaths female` = hi_b
), align = c("l", "r", "r", "r", "r", "r", "r")) %>%
  kable_styling(full_width = FALSE, bootstrap_options = "striped")
```

</details>

How much could those `r length(miss_idx)` unlabeled records move the headline? Two uniform fills - every unknown record assigned male, then female - shift the female coefficient only between `r sprintf('%.3f', bounds$estimate[1])` and `r sprintf('%.3f', bounds$estimate[2])`. But uniform assignment is not a worst case, because `r sum(mm_bound$surv[miss_idx] == 0)` of the unknowns died and `r sum(mm_bound$surv[miss_idx] == 1)` survived, and an adversary can exploit that. The coefficient depends on the assignment only through per-ship counts, which makes the discrete optimization solvable exactly: the Dinkelbach iteration above searches every logically possible assignment and finds the global extremes at the outcome-based corner fills - every unknown death labeled a woman and every unknown survivor a man, and the reverse. Those extremes are `r sprintf('[%.3f, %.3f]', global_lo, global_hi)`. No assignment of the `r length(miss_idx)` records, however coordinated, can push the coefficient outside that interval.

That is a statement about point estimates, so sampling error still has to be added rather than left in a separate ledger - and this is where an appealing shortcut fails. Refitting at the two optimizing corners with ship-clustered errors gives `r sprintf('[%.3f, %.3f]', corner_union[1], corner_union[2])`, but that pair does not cover the two uncertainties together. The completion that extremizes the coefficient need not extremize a confidence limit, because the clustered standard error moves with the assignment too. Searching the endpoints directly finds a completion that proves it: label every one of the *Atlantic*'s `r bound_stats$B[bound_stats$ship == 'SS Atlantic']` unknown deaths female and its `r bound_stats$A[bound_stats$ship == 'SS Atlantic']` unknown survivors male, hold the other wrecks at the maximizing corner, and the point estimate falls back to `r sprintf('%.3f', coef(hi_best_fit)['fb'])` while the interval's upper limit *rises* to `r sprintf('%.3f', searched_union[2])` - outside the corner pair. The union over completions is therefore at least `r sprintf('[%.3f, %.3f]', searched_union[1], searched_union[2])`. That is a lower bound on its width, not the width: coordinate ascent on a non-separable objective is a heuristic, and unlike the point-estimate bound above - which carries a global optimality certificate - the endpoints do not. `r sum(map_dbl(hi_search, 'value') > max(map_dbl(hi_search, 'value')) - 1e-9)` of `r length(search_starts)` restarts land on the same maximum, which is suggestive and is not a proof. It is also a union of intervals, conservative by construction rather than a calibrated partial-identification interval. So the claim this section can actually make is the narrower one: the largest upper endpoint the search found still puts the coefficient well below zero, and none of the `r length(search_starts)` restarts found an upper endpoint above `r sprintf('%.3f', searched_union[2])`. (Largest upper endpoint, not widest interval - the two ends of the union come from different completions, and no single assignment produces both.) Two limits on the claim: it bounds sex missingness only - `r sum(!d$ship %in% c('RMS Titanic', 'RMS Lusitania') & is.na(d$surv))` main-sample records have no survival outcome and are simply dropped, too few to matter but not bounded - and nothing here addresses who made it onto a passenger list in the first place.

# Sixteen dots

An average deserves a look at what it averages. For every main-sample wreck, the next figure subtracts the male survival rate from the female rate. Positive means women did better.

```r
ship_gaps <- ms_h1 %>% group_by(ship) %>% summarise(
  year = first(Year), wcf = first(wcf),
  female_rate = mean(surv[female == 1]), male_rate = mean(surv[female == 0]),
  gap = female_rate - male_rate, overall = mean(surv), .groups = "drop"
) %>% arrange(year, ship) %>% mutate(ship_year = factor(
  paste0(ship, " (", year, ")"), levels = rev(paste0(ship, " (", year, ")"))))

birkenhead_records <- d %>% filter(ship == "HMS Birkenhead")
atlantic_records <- d %>% filter(ship == "SS Atlantic")
stopifnot(nrow(birkenhead_records) == 556,
          sum(birkenhead_records$female == 1, na.rm = TRUE) == 7,
          sum(birkenhead_records$surv[birkenhead_records$female == 1], na.rm = TRUE) == 7,
          sum(birkenhead_records$female == 0, na.rm = TRUE) == 549,
          abs(mean(birkenhead_records$surv[birkenhead_records$female == 0], na.rm = TRUE) - .3352) < .0001,
          nrow(atlantic_records) == 951,
          sum(atlantic_records$female == 1, na.rm = TRUE) == 235,
          sum(atlantic_records$surv[atlantic_records$female == 1], na.rm = TRUE) == 0,
          sum(atlantic_records$female == 0, na.rm = TRUE) == 636,
          abs(mean(atlantic_records$surv[atlantic_records$female == 0], na.rm = TRUE) - .5213) < .0001,
          # the Birkenhead is the only wreck on the female-advantage side
          nrow(ship_gaps) == 16, sum(ship_gaps$gap < 0) == 15,
          ship_gaps$ship[ship_gaps$gap > 0] == "HMS Birkenhead")

ggplot(ship_gaps, aes(gap, ship_year, color = factor(wcf), shape = factor(wcf))) +
  geom_vline(xintercept = 0, color = "#6B7280", linewidth = .5) +
  geom_segment(aes(x = 0, xend = gap, yend = ship_year),
               color = "#D1D5DB", linewidth = .6) +
  geom_point(size = 3) +
  scale_color_manual(values = c(`0` = blue, `1` = rust),
                     labels = c("No recorded order", "Captain ordered WCF"), name = NULL) +
  scale_shape_manual(values = c(`0` = 16, `1` = 17),
                     labels = c("No recorded order", "Captain ordered WCF"), name = NULL) +
  scale_x_continuous(labels = scales::label_percent(accuracy = 1)) +
  labs(title = "The average is made from radically different wrecks",
       subtitle = "Sex gap in survival, ordered by year",
       x = "Female survival minus male survival", y = NULL)
```

![Female minus male survival in each main-sample wreck. Rust triangles mark a recorded women-and-children-first order.](./female-survival-in-marital-disasters/generated-figure-01.png)

The range is not subtle. The *Birkenhead* sits at `r sprintf('%+.3f', ship_gaps$gap[ship_gaps$ship == 'HMS Birkenhead'])` because seven women were recorded aboard and all seven survived, alongside 549 men of whom `r scales::percent(mean(birkenhead_records$surv[birkenhead_records$female == 0], na.rm = TRUE), accuracy = .1)` lived. The most famous instance of women-and-children-first in the sample is a rate computed from seven people. I checked that denominator twice. The *Atlantic* sits at `r sprintf('%+.3f', ship_gaps$gap[ship_gaps$ship == 'SS Atlantic'])`; none of its recorded women survived. The *Mafalda* and *Morro Castle* sit close to zero, but on the same side as the rest: the *Birkenhead* is the only one of the sixteen where women did better, and the other `r sum(ship_gaps$gap < 0)` all fall the same way. That count is the simplest evidence in the post and the least dependent on any modelling choice.

```r
# Which average is -0.167? A ship-fixed-effects coefficient on a binary regressor
# is exactly the wreck-level gaps reweighted by n * p * (1 - p): ship size times
# sex balance. Equal-ship weights (the paper's moderator specification) drop the
# size factor but keep the balance factor, so they do not weight wrecks equally
# either - only their totals.
ms_h1_w <- ms_h1 %>% group_by(ship) %>% mutate(w = 1 / n()) %>% ungroup()
h1_eqship <- feols(surv ~ female | ship, data = ms_h1_w, weights = ~w,
                   vcov = ~ship, ssc = cluster_ssc)

gap_w <- ship_gaps %>%
  left_join(ms_h1 %>% group_by(ship) %>%
              summarise(n_s = n(), p_s = mean(female == 1), .groups = "drop"),
            by = "ship") %>%
  mutate(fe_w = n_s * p_s * (1 - p_s), eq_w = p_s * (1 - p_s))

birk_fe_share <- gap_w$fe_w[gap_w$ship == "HMS Birkenhead"] / sum(gap_w$fe_w)

estimands <- tibble(
  Estimand = c("Plain average of the sixteen wreck gaps",
               "Median wreck gap",
               "Ship fixed effects (the headline)",
               "Ship fixed effects, paper-style equal-ship weights"),
  `Wreck weight` = c("1 / 16 each", "—", "n x p x (1 - p)", "p x (1 - p)"),
  Estimate = c(mean(gap_w$gap), median(gap_w$gap),
               unname(coef(h1_robust)["female"]),
               unname(coef(h1_eqship)["female"]))
)

stopifnot(
  nrow(gap_w) == 16, sum(gap_w$gap < 0) == 15,
  gap_w$ship[gap_w$gap > 0] == "HMS Birkenhead",
  # the identities the paragraph below asserts, to machine precision
  abs(weighted.mean(gap_w$gap, gap_w$fe_w) - coef(h1_robust)["female"]) < 1e-12,
  abs(weighted.mean(gap_w$gap, gap_w$eq_w) - coef(h1_eqship)["female"]) < 1e-12,
  abs(mean(gap_w$gap) - (-.147)) < .001,
  abs(median(gap_w$gap) - (-.179)) < .001,
  abs(coef(h1_eqship)["female"] - (-.187)) < .001,
  # every version is negative, and none is close to zero
  all(estimands$Estimate < -.14), all(estimands$Estimate > -.19),
  degrees_freedom(h1_eqship, type = "t") == n_distinct(ms_h1$ship) - 1,
  # fixed effects give the seven-woman wreck a twentieth of the weight an
  # equal-wreck average would
  birk_fe_share < 1 / 16 / 15)

kable(estimands %>% mutate(Estimate = sprintf("%+.3f", Estimate)),
      align = c("l", "l", "r"),
      caption = "The same sixteen wrecks, four ways of averaging them.") %>%
  kable_styling(full_width = FALSE, bootstrap_options = "striped")
```

That spread answers a question the headline number quietly begs: which average is `r sprintf('%.3f', coef(h1_robust)['female'])`? It is not the average of those sixteen dots. A ship-fixed-effects coefficient on a binary regressor weights each wreck by its size *and* its sex balance - `n x p x (1 - p)` - so a large, evenly split wreck counts for far more than a small or lopsided one. The identity is exact rather than approximate: reweight the sixteen gaps that way and `r sprintf('%.3f', coef(h1_robust)['female'])` comes back to fifteen decimal places. Weight the wrecks the paper's way instead, equal totals per ship, and the gap is `r sprintf('%.3f', coef(h1_eqship)['female'])`; take the plain average of the sixteen dots and it is `r sprintf('%.3f', mean(gap_w$gap))`; take the median and it is `r sprintf('%.3f', median(gap_w$gap))`.

Nothing in the story turns on that choice - every version is negative and none is near zero - but it is worth naming rather than inheriting from a software default, especially since the moderator models later in the post switch to the equal-ship weights while the headline does not. It also cuts against the intuition that the plain average is the more honest one. An equal-wreck average hands the *Birkenhead*'s seven-woman denominator `r scales::percent(1/16, accuracy = .1)` of the estimate; fixed effects give it `r scales::percent(birk_fe_share, accuracy = .1)`. The estimator that looks least democratic is the one that leans least on the thinnest cell in the sample.

So the average is real, but the thing being averaged isn't one tidy phenomenon. A captain ordering women first on a troopship in 1852 and a listing car ferry in the Baltic in 1994 share a dependent variable. They don't necessarily share a data-generating process.

# Eleven thousand people, sixteen ships

The paper's first two claims concern people: female or male, crew or passenger. There are thousands of observations for those comparisons. Its six moderators concern ships. A recorded WCF order and a ship's registry each provide only one label per wreck. A wreck is quick or slow once. A flag doesn't change from deck to deck.

If we want to know whether captains' orders matter, we have sixteen captains, not eleven thousand independent data points. Counting people as separate evidence about an order is like polling one household a thousand times and reporting the margin of error for a thousand households.

That mismatch is easiest to see by counting ship-level conditions as ships, not people:

```r
treatment_counts <- ms %>% distinct(ship, wcf, quick, post_wwi, british,
                                    smallshare, voyage1) %>%
  summarise(`Recorded WCF order` = sum(wcf), `Quick sinking` = sum(quick),
            `Post-WWI` = sum(post_wwi), `British-registered` = sum(british),
            `Small share of women` = sum(smallshare),
            `Voyage over one day` = sum(voyage1)) %>%
  pivot_longer(everything(), names_to = "Ship-level condition", values_to = "Ships = 1")
kable(treatment_counts, align = c("l", "r")) %>%
  kable_styling(full_width = FALSE, bootstrap_options = "striped")
```

Three ships carry the captain's-order result. The richest split is eight against eight, still a small experiment if the ships had been randomized. They weren't.

Clustered standard errors treat people on the same ship as related evidence. Coefficients don't change; uncertainty does. Two choices come with that. The first is the standard error itself. The second is the reference distribution the resulting t-statistic is compared against, which is easy to leave on a default and which matters far more with sixteen clusters than with sixteen thousand: referring to the normal implicitly claims the cluster count is large, which is the very assumption under audit here. Every clustered test below is therefore referred to a t distribution with `r n_distinct(ms$ship) - 1` degrees of freedom - ships minus one - and every clustered interval uses that distribution's critical value rather than 1.96. The wild bootstrap in the next section adds a second small-cluster sensitivity check resting on different assumptions - not a stronger one.

```r
h1_cluster <- update(h1_robust, vcov = ~ship, ssc = cluster_ssc)
h2_cluster <- update(h2_robust, vcov = ~ship, ssc = cluster_ssc)
joint_cluster <- update(joint_robust, vcov = ~ship, ssc = cluster_ssc)

terms <- tibble(
  source = c("h1", "h2", rep("joint", 6)),
  term = c("female", "crew", "female:wcf", "female:british", "female:post_wwi",
           "female:smallshare", "female:voyage1", "female:quick")
) %>% mutate(label = unname(term_labels[term]))
pick_model <- function(source, clustered) {
  get(paste0(source, if (clustered) "_cluster" else "_robust"))
}
inference <- pmap_dfr(terms, function(source, term, label) {
  bind_rows(model_row(pick_model(source, FALSE), term, label, "Robust"),
            model_row(pick_model(source, TRUE), term, label, "Clustered by ship"))
}) %>% mutate(lo = estimate - crit * se, hi = estimate + crit * se)
stopifnot(all(inference$crit[inference$inference == "Clustered by ship"] ==
                qt(.975, n_distinct(ms$ship) - 1)),
          all(inference$crit[inference$inference == "Robust"] < 1.97))

ggplot(inference, aes(estimate, factor(term, levels = rev(unique(terms$label))),
                      color = inference)) +
  geom_vline(xintercept = 0, color = "#6B7280", linewidth = .5) +
  geom_errorbar(aes(xmin = lo, xmax = hi), width = .18, orientation = "y",
                position = position_dodge(width = .45)) +
  geom_point(position = position_dodge(width = .45), size = 2.4) +
  scale_color_manual(values = c("Robust" = rust, "Clustered by ship" = navy)) +
  scale_x_continuous(labels = scales::label_number(accuracy = .001)) +
  labs(title = "Once ships are the evidence, the explanations become uncertain",
       x = "Estimated change in survival probability", y = NULL, color = NULL)
```

![Coefficients from three models - Female from the sex-only model, Crew from the sex-and-crew model, the six interactions from the paper's joint weighted specification - each with heteroskedasticity-robust and ship-clustered 95% intervals. Robust intervals use n - K degrees of freedom, clustered intervals G - 1 = 15.](./female-survival-in-marital-disasters/generated-figure-02.png)

The robust SE on `female` is `r sprintf('%.4f', se(h1_robust)['female'])`; ship clustering raises it to `r sprintf('%.4f', se(h1_cluster)['female'])`, roughly five times larger. The conclusion is unchanged either way - p = `r fmt_p(pvalue(h1_cluster)['female'])` on fifteen degrees of freedom - and the crew claim survives too, at p `r fmt_p(pvalue(h2_cluster)['crew'])`. The moderator claims are where the original precision does not survive ship-level inference. The captain-order interaction moves from p `r fmt_p(pvalue(joint_robust)['female:wcf'])` to `r fmt_p(pvalue(joint_cluster)['female:wcf'])`; British ships move from `r fmt_p(pvalue(joint_robust)['female:british'])` to `r fmt_p(pvalue(joint_cluster)['female:british'])`; the post-WWI interaction lands at `r fmt_p(pvalue(joint_cluster)['female:post_wwi'])`. Standard errors for the moderators are roughly two to three and a half times larger.

The female and crew coefficients remain clearly distinguishable from zero under clustering. The moderator intervals contain zero as well as effects in either direction large enough to matter historically. Their width reflects the limited number of ships and the weak support for ship-level explanations.

The t correction is a patch, not a fix. The cluster-robust variance estimator is itself biased downward when a handful of clusters carry most of the leverage, and no choice of degrees of freedom repairs that. As a genuine small-cluster check, I use `fwildclusterboot::boottest()`: it imposes the null, applies Rademacher weights at the ship level, and reports two-sided p-values and 95% confidence intervals. I use 9,999 draws for the sixteen-ship models; the package automatically enumerates the full reference set when only seven ships are available later in the post. It is a second sensitivity analysis rather than an arbiter: its own validity rests on conditions - clusters large, and their covariate distributions similar enough across ships - that these wrecks satisfy no better than they satisfy the conditions behind the clustered t-test. Where the two answers differ I report both and say so, rather than picking a winner.

```r
wild_boot <- function(model, term, seed, B = 9999) {
  set.seed(seed)
  dqrng::dqset.seed(seed)
  fit <- boottest(model, param = term, B = B, clustid = "ship",
                  bootcluster = "ship", type = "rademacher",
                  impose_null = TRUE, conf_int = TRUE)
  tibble(term, estimate = unname(fit$point_estimate), p = fit$p_val,
         lo = fit$conf_int[1], hi = fit$conf_int[2], B = fit$boot_iter)
}
```

```r
h1_boot_model <- lm(surv ~ female + factor(ship), data = ms_h1)
h2_boot_model <- lm(surv ~ female + crew + factor(ship), data = ms)
joint_boot_model <- lm(
  surv ~ female + crew + female:wcf + female:quick + female:smallshare +
    female:voyage1 + female:post_wwi + female:british + factor(ship),
  data = ms, weights = w
)
wild_results <- bind_rows(
  wild_boot(h1_boot_model, "female", 11),
  wild_boot(h2_boot_model, "crew", 12),
  wild_boot(joint_boot_model, "female:wcf", 13),
  wild_boot(joint_boot_model, "female:british", 14),
  wild_boot(joint_boot_model, "female:post_wwi", 15)
) %>% mutate(label = unname(term_labels[term]))
expected_boot <- c(
  female = unname(coef(h1_robust)["female"]),
  crew = unname(coef(h2_robust)["crew"]),
  `female:wcf` = unname(coef(joint_robust)["female:wcf"]),
  `female:british` = unname(coef(joint_robust)["female:british"]),
  `female:post_wwi` = unname(coef(joint_robust)["female:post_wwi"])
)
stopifnot(max(abs(setNames(wild_results$estimate, wild_results$term)[names(expected_boot)] -
                    expected_boot)) < 1e-8)

kable(wild_results %>% transmute(Term = label, Estimate = sprintf("%.3f", estimate),
                                 `Bootstrap p` = fmt_p(p),
                                 `95% interval` = sprintf("[%.3f, %.3f]", lo, hi)),
      align = c("l", "r", "r", "r")) %>%
  kable_styling(full_width = FALSE, bootstrap_options = "striped")
```

The wild bootstrap agrees with the clustered comparison. The overall female disadvantage has p `r fmt_p(wild_results$p[wild_results$term == 'female'])`; the crew advantage has p = `r fmt_p(wild_results$p[wild_results$term == 'crew'])`. None of the three moderator interactions is distinguishable from zero, and each bootstrap interval spans meaningful effects of both signs. Captain's orders, the result most central to the paper's leadership story, have p = `r fmt_p(wild_results$p[wild_results$term == 'female:wcf'])`.

Randomization inference gives the same idea without residuals. There are only `r choose(16, 3)` ways to place three WCF orders among sixteen ships. I assign the three labels to every possible trio, refit the joint model, and compare those placebo coefficients with the observed one.

```r
ship_names <- sort(unique(ms$ship)); assignments <- combn(ship_names, 3, simplify = FALSE)
ri_null <- map_dbl(assignments, function(treated) {
  z <- ms %>% mutate(wcf_ri = as.integer(ship %in% treated))
  m <- feols(surv ~ female + crew + female:wcf_ri + female:quick +
               female:smallshare + female:voyage1 + female:post_wwi +
               female:british | ship, data = z, weights = ~w)
  coef(m)["female:wcf_ri"]
})
ri_observed <- coef(joint_robust)["female:wcf"]
ri_p <- mean(abs(ri_null) >= abs(ri_observed))

ggplot(tibble(estimate = ri_null), aes(estimate)) +
  geom_histogram(bins = 28, fill = sand, color = "white") +
  geom_vline(xintercept = ri_observed, color = rust, linewidth = 1.1) +
  annotate("text", x = ri_observed, y = Inf, vjust = 1.5, hjust = -.08,
           label = paste0("Observed = ", sprintf("%.3f", ri_observed)), color = rust) +
  scale_x_continuous(labels = scales::label_number(accuracy = .001)) +
  labs(title = "Three order labels can make many apparent effects",
       subtitle = paste0("Two-sided permutation p = ", sprintf("%.3f", ri_p),
                         " over all 560 placements"),
       x = "Placebo coefficient on female × recorded WCF order", y = "Assignments")
```

![Enumerated permutation distribution from all 560 placements of three WCF labels. The line is the observed joint-model estimate.](./female-survival-in-marital-disasters/generated-figure-03.png)

The p-value is `r sprintf('%.3f', ri_p)`. It is exhaustive rather than exact: the reference set is enumerated completely, with no simulation error anywhere in it, but "exact" in the randomization-test sense would require the three labels to have been assigned by a design that made all 560 placements equally likely, and no such design ever existed. Read it as a conditional permutation diagnostic and the point is plain enough: the observed estimate isn't unusual among arbitrary placements of three labels.

# Take one wreck away

While the bootstrap and permutation test ask whether chance could produce the estimate, the leave-one-out asks whether one particular wreck is carrying it.

A result based on sixteen ships should show what happens when one disappears. I use paper-style equal-ship weights in one-hypothesis models, cluster by ship, and refit each model sixteen times. The weights make each wreck contribute the same total weight, as in the paper's moderator specifications.

```r
loo_specs <- tribble(
  ~label, ~variable,
  "Recorded WCF order", "wcf", "Post-WWI", "post_wwi",
  "British-registered ship", "british")
fit_one <- function(data, variable) {
  f <- as.formula(paste0("surv ~ female + crew + female:", variable, " | ship"))
  feols(f, data = data, weights = ~w, vcov = ~ship, ssc = cluster_ssc)
}
full_loo <- map2_dfr(loo_specs$label, loo_specs$variable, function(label, variable) {
  m <- fit_one(ms, variable); term <- paste0("female:", variable)
  tibble(label, variable, estimate = coef(m)[term], p = pvalue(m)[term])
})
full_value <- function(variable, column) full_loo[full_loo$variable == variable, column, drop = TRUE]
```

One bookkeeping note, because it explains two different British numbers in this post. The paper tests each moderator twice: alone, in its own model, and jointly with the other five. Its Table 1 reports both, and they differ - `r sprintf('%.3f', full_value('british', 'estimate'))` alone (column 8) against `r sprintf('%.3f', coef(joint_robust)['female:british'])` in the joint test (column 9). The bootstrap section above used the joint specification, because that is the one the paper calls its most reliable. This section uses the single-moderator models, because leaving a wreck out of a six-moderator model on sixteen ships changes several comparisons at once and the resulting movement can't be attributed to anything. So the `r sprintf('%.3f', full_value('british', 'estimate'))` here and the `r sprintf('%.3f', coef(joint_robust)['female:british'])` earlier are two specifications, not two estimates of the same thing, and neither is precise once ships are the unit.

```r
loo <- map_dfr(unique(ms$ship), function(omitted) {
  map2_dfr(loo_specs$label, loo_specs$variable, function(label, variable) {
    m <- fit_one(filter(ms, ship != omitted), variable); term <- paste0("female:", variable)
    tibble(omitted, label, variable, estimate = coef(m)[term], p = pvalue(m)[term])
  })
}) %>% left_join(ship_gaps %>% select(ship, year), by = c("omitted" = "ship")) %>%
  mutate(omit_label = paste0(omitted, " (", year, ")"),
         highlight = omitted == "SS Atlantic" & label == "British ship")
omit_levels <- loo %>% distinct(omit_label, year) %>% arrange(desc(year)) %>% pull(omit_label)
loo$omit_label <- factor(loo$omit_label, levels = omit_levels)
loo_summary <- loo %>% group_by(label, variable) %>% summarise(
  lo = min(estimate), hi = max(estimate), best_p = min(p), worst_p = max(p),
  .groups = "drop"
)
loo_value <- function(variable, omitted, column) {
  loo[loo$variable == variable & loo$omitted == omitted, column, drop = TRUE]
}
british_sig <- sum(loo$p[loo$variable == "british"] < .05)
stopifnot(all(map_dbl(unique(ms$ship), ~ degrees_freedom(
            fit_one(filter(ms, ship != .x), "british"), type = "t")) == 14),
          degrees_freedom(fit_one(ms, "british"), type = "t") == 15,
          abs(full_value("wcf", "estimate") - .0189) < .0001,
          abs(full_value("wcf", "p") - .782) < .001,
          abs(full_value("post_wwi", "estimate") - .0850) < .0001,
          abs(full_value("post_wwi", "p") - .270) < .001,
          abs(full_value("british", "estimate") - (-.1530)) < .0001,
          abs(full_value("british", "p") - .060) < .001,
          abs(loo_value("british", "SS Atlantic", "estimate") - (-.0954)) < .0001,
          abs(loo_value("british", "SS Atlantic", "p") - .116) < .001,
          abs(loo_value("british", "SS Princess Alice", "estimate") - (-.2009)) < .0001,
          abs(loo_value("british", "SS Princess Alice", "p") - .014) < .001,
          abs(loo_value("british", "MV Bulgaria", "estimate") - (-.1818)) < .0001,
          abs(loo_value("british", "MV Bulgaria", "p") - .025) < .001,
          british_sig == 3,
          round(loo_summary$lo[loo_summary$variable == "wcf"], 3) == -.012,
          round(loo_summary$hi[loo_summary$variable == "wcf"], 3) == .090,
          abs(loo_summary$best_p[loo_summary$variable == "wcf"] - .342) < .001,
          round(loo_summary$lo[loo_summary$variable == "post_wwi"], 3) == .032,
          round(loo_summary$hi[loo_summary$variable == "post_wwi"], 3) == .117,
          abs(loo_summary$best_p[loo_summary$variable == "post_wwi"] - .126) < .001,
          round(loo_summary$lo[loo_summary$variable == "british"], 3) == -.201,
          round(loo_summary$hi[loo_summary$variable == "british"], 3) == -.095,
          round(loo_summary$best_p[loo_summary$variable == "british"], 3) == .014,
          round(loo_summary$worst_p[loo_summary$variable == "british"], 3) == .116,
          round(loo_summary$worst_p[loo_summary$variable == "wcf"], 3) == .990,
          round(loo_summary$worst_p[loo_summary$variable == "post_wwi"], 3) == .579)

loo_table <- loo_specs %>%
  left_join(full_loo %>% select(label, variable, estimate, p), by = c("label", "variable")) %>%
  left_join(loo_summary, by = c("label", "variable")) %>%
  transmute(
    Moderator = label,
    `Full sample` = sprintf("%+.3f (p = %.3f)", estimate, p),
    `LOO estimate range` = sprintf("[%+.3f, %+.3f]", lo, hi),
    `LOO p range` = sprintf("[%.3f, %.3f]", best_p, worst_p)
  )

ggplot(loo, aes(estimate, omit_label)) +
  geom_vline(data = full_loo, aes(xintercept = estimate),
             color = "#6B7280", linetype = 2) +
  geom_point(aes(color = highlight), size = 2.2) +
  facet_wrap(~label, ncol = 1, scales = "free_x") +
  scale_color_manual(values = c(`FALSE` = blue, `TRUE` = rust), guide = "none") +
  scale_x_continuous(labels = scales::label_number(accuracy = .001)) +
  labs(title = "The British result is the leave-one-out exception",
       x = "Female × ship-condition coefficient", y = "Wreck omitted")
```

![Each point is the interaction estimate after omitting the named wreck. Dashed lines show the full-sample estimate from the same one-hypothesis model.](./female-survival-in-marital-disasters/generated-figure-04.png)

```r
kable(loo_table, align = c("l", "r", "r", "r"),
      caption = "Weighted single-hypothesis models with ship-clustered inference.") %>%
  kable_styling(full_width = FALSE, bootstrap_options = "striped")
```

For captain's orders and the postwar shift, no omission changes the picture. The captain's-order estimate ranges from `r sprintf('%+.3f', loo_summary$lo[loo_summary$variable == 'wcf'])` to `r sprintf('%+.3f', loo_summary$hi[loo_summary$variable == 'wcf'])` with p never below `r fmt_p(loo_summary$best_p[loo_summary$variable == 'wcf'])`; the postwar estimate from `r sprintf('%+.3f', loo_summary$lo[loo_summary$variable == 'post_wwi'])` to `r sprintf('%+.3f', loo_summary$hi[loo_summary$variable == 'post_wwi'])` with p never below `r fmt_p(loo_summary$best_p[loo_summary$variable == 'post_wwi'])`. In every subsample both are compatible with zero and with effects of real size in either direction.

The British interaction deserves separate attention because its sign runs opposite to the paper's starting hypothesis: women fare relatively worse, not better, on British-registered ships. Three questions need to be kept apart, because they get different answers. *Is the point estimate stable?* Yes. It is negative in all sixteen omissions, ranging from `r sprintf('%+.3f', loo_summary$lo[loo_summary$variable == 'british'])` to `r sprintf('%+.3f', loo_summary$hi[loo_summary$variable == 'british'])`. *Is conventional significance stable?* No, and it does not reach the threshold to begin with: on the full sample the single-moderator estimate is `r sprintf('%+.3f', full_value('british', 'estimate'))` with p = `r fmt_p(full_value('british', 'p'))`, and only `r british_sig` of the sixteen omissions fall below 0.050. The *Atlantic* is the reason the number moves most. It contains 951 records: 235 women, none of whom survived, and 636 men, of whom `r scales::percent(mean(atlantic_records$surv[atlantic_records$female == 0], na.rm = TRUE), accuracy = .1)` lived - a brutal row in otherwise tidy data, British-registered, and the most extreme female disadvantage in the sample. Remove it and p moves from `r fmt_p(full_value('british', 'p'))` to `r fmt_p(loo_value('british', 'SS Atlantic', 'p'))`; remove the *Princess Alice* instead and it tightens to `r fmt_p(loo_value('british', 'SS Princess Alice', 'p'))`. A p-value ranging over `r fmt_p(loo_summary$best_p[loo_summary$variable == 'british'])` to `r fmt_p(loo_summary$worst_p[loo_summary$variable == 'british'])` as single wrecks come and go is a property of a reference distribution with fourteen degrees of freedom, not a discontinuity in the evidence - which is the reason to read the estimate range rather than the threshold crossings. *Is the estimate causally interpretable?* This is where the claim actually founders. British registry is not a treatment: within these sixteen wrecks it travels with period, route, vessel type, passenger mix, evacuation practice, and the quality of the surviving records. The interaction is directionally more consistent than its p-values suggest - and still cannot be read as an effect of Britishness, because sixteen non-randomized ships cannot separate a flag from everything that sails with it.

One caution covers this whole battery of checks. Clustered errors, the wild bootstrap, label permutation, and leave-one-out are different diagnostics, not independent replications: all four reuse the same sixteen ships. Each guards against a specific way inference can fail; none creates new historical units, and none addresses confounding, how these wrecks entered the sample, or how far they generalize.

| Diagnostic | Guards against | Does not address |
|---|---|---|
| Ship-clustered SEs | treating shipmates as independent evidence | few-cluster reliability, confounding |
| Wild cluster bootstrap | over-reliance on one few-cluster reference distribution | whether its own small-*G* assumptions hold here, causal identification |
| Label permutation | chance placement of ship labels | plausibility of exchangeability |
| Leave-one-out | dependence on a single wreck | sample selection, confounding |

So where does the audit land? The female disadvantage and the crew advantage are robust descriptive associations in this dataset. The ship-level moderator effects are too imprecisely estimated to support the original explanatory claims, which leaves them unestablished, not refuted. Why the robust associations arose is a separate question, and the rest of this post turns to it.

# Little girls, little boys

“Female” is not a manipulable treatment. It bundles how other people respond with physical differences that mattered aboard a sinking ship. Rope ladders, steeply listing stairs, swimming, and heavy wet clothing reward strength and mobility. A female disadvantage isn't, by itself, an estimate of failed chivalry. We would need to know the gap with no chivalry at all.

Children offer a comparison, though a blunter probe than it first appears. Before puberty, girls and boys are closer in size and strength than adult women and men, so if the adult gap were purely a matter of bodies, it should shrink among children. The reverse reading is weaker, and it belongs here rather than after the result: a small gap among children would not show that treatment drives the adult gap. "Women and children first" groups girls and boys together by design; small children often lived or died with whichever adult carried them; and where a family stood when the ship went down varied by age more than by sex. Any of these could equalize child outcomes whatever the role of bodies. This is a mechanism probe with limited discriminatory power, not a decisive test between bodies and treatment.

With that limit on record, the comparison itself should at least be built symmetrically. Age is available on seven main-sample ships, and I restrict both age groups to passengers so children and adults are defined on the same footing (this drops `r sum(!is.na(ms$Age) & ms$Age < 16 & ms$crew == 1)` under-sixteen crew records; it changes nothing material). That leaves `r format(sum(!is.na(ms$Age) & ms$crew == 0), big.mark = ',')` passengers with recorded age, sex, and outcome: `r sum(!is.na(ms$Age) & ms$Age < 16 & ms$crew == 0 & ms$female == 1)` girls and `r sum(!is.na(ms$Age) & ms$Age < 16 & ms$crew == 0 & ms$female == 0)` boys below sixteen, and `r format(sum(!is.na(ms$Age) & ms$Age >= 16 & ms$crew == 0), big.mark = ',')` adults. Rather than comparing two separately estimated subgroup coefficients - where one significant and one non-significant estimate proves nothing about their difference - the model estimates the child–adult difference in the sex gap directly: `surv ~ female * child | ship`, with ship-clustered errors and, for the primary cutoff, the same wild-bootstrap check used earlier, here enumerating all 128 sign patterns that seven ships allow.

```r
age_ships <- ms %>% filter(!is.na(Age)) %>% distinct(ship) %>% pull(ship)
pax_age <- ms %>% filter(ship %in% age_ships, !is.na(Age), crew == 0)
z16 <- pax_age %>% mutate(child = as.integer(Age < 16))
child_counts <- z16 %>% filter(child == 1) %>% count(ship, sort = TRUE)
child_top2_share <- sum(child_counts$n[1:2]) / sum(child_counts$n)
adult_only_7 <- feols(surv ~ female | ship, data = filter(pax_age, Age >= 16),
                      vcov = ~ship, ssc = cluster_ssc)
```

```r
age_missing <- ms %>% filter(ship %in% age_ships) %>% group_by(ship) %>%
  summarise(missing = mean(is.na(Age)),
            surv_missing = mean(surv[is.na(Age)]),
            surv_recorded = mean(surv[!is.na(Age)]), .groups = "drop") %>%
  filter(missing > 0) %>% arrange(desc(missing))
am <- function(s, column) age_missing[[column]][age_missing$ship == s]
# The paper's combined child definition: Age < 16 where an age exists, the Child
# flag where it does not. That restores the two flag-only wrecks and every record
# an age cutoff drops, at the cost of a coarser definition of childhood.
combined <- ms %>%
  mutate(child = coalesce(as.integer(Age < 16), as.integer(Child == 1))) %>%
  filter(!is.na(child))
combined_pax <- combined %>% filter(crew == 0)
combined_crew <- combined %>% filter(crew == 1)
comb_pax <- feols(surv ~ female * child | ship, data = combined_pax,
                  vcov = ~ship, ssc = cluster_ssc)
# Restoring crew adds mostly adults, so that model has to adjust for crew status
# rather than pool it; and as in the crew section, the within-ship, within-group
# comparison wants ship x child baselines rather than a pooled child effect.
comb_all <- feols(surv ~ female * child + crew | ship, data = combined,
                  vcov = ~ship, ssc = cluster_ssc)
comb_all_sat <- feols(surv ~ female * child + crew | ship^child, data = combined,
                      vcov = ~ship, ssc = cluster_ssc)
comb_pax_sat <- feols(surv ~ female * child | ship^child, data = combined_pax,
                      vcov = ~ship, ssc = cluster_ssc)
stopifnot(nrow(combined) == 4349, n_distinct(combined$ship) == 9,
          nrow(combined_pax) == 3687, n_distinct(combined_pax$ship) == 9,
          nrow(combined_crew) == 662, sum(combined_crew$child) == 3,
          degrees_freedom(comb_all, type = "t") == 8,
          abs(coef(comb_all)["female:child"] - .1410) < .001,
          abs(pvalue(comb_all)["female:child"] - .044) < .001,
          abs(coef(comb_pax)["female:child"] - .1364) < .001,
          abs(pvalue(comb_pax)["female:child"] - .076) < .001,
          abs(coef(comb_pax_sat)["female:child"] - .1476) < .001,
          abs(pvalue(comb_pax_sat)["female:child"] - .053) < .001,
          degrees_freedom(comb_pax_sat, type = "t") == 8,
          abs(coef(comb_all_sat)["female:child"] - .1534) < .001,
          abs(pvalue(comb_all_sat)["female:child"] - .026) < .001,
          age_missing$ship[1] == "SS Principessa Mafalda",
          abs(am("SS Principessa Mafalda", "missing") - .680) < .001,
          abs(am("SS Principessa Mafalda", "surv_missing") - .912) < .001,
          abs(am("SS Principessa Mafalda", "surv_recorded") - .372) < .001,
          abs(am("SS Princess Alice", "surv_missing") - .429) < .001,
          abs(am("SS Princess Alice", "surv_recorded") - .050) < .001)
```

Three facts about this subsample belong before the result. In its favour, as far as it goes: restricted to adult passengers on those seven ships alone, the female coefficient is `r sprintf('%+.3f', coef(adult_only_7)['female'])`, close to the `r sprintf('%+.3f', coef(h1_robust)['female'])` of the full sixteen-ship sample. That is one moment of one distribution agreeing, which is weak evidence of representativeness rather than a demonstration of it - but it would have been a warning sign had it come out differently, and it doesn't. Against it: the children are concentrated. Of the `r sum(child_counts$n)` under-sixteens, `r sum(child_counts$n[1:2])` - `r scales::percent(child_top2_share, accuracy = .1)` - are on the *Norge* and the *Princess Alice*, and the *Princess Victoria* records five boys and no girls, so it contributes nothing to the contrast at all. This is the same concentration problem the crew section runs into later, and it deserves the same treatment: a leave-one-out.

Against it more seriously, and the reason the first fact is weaker than it looks: within these seven ships, age is often not recorded, and whether it was recorded is bound up with who lived. On the *Mafalda*, `r scales::percent(am('SS Principessa Mafalda', 'missing'), accuracy = .1)` of records carry no age, and `r scales::percent(am('SS Principessa Mafalda', 'surv_missing'), accuracy = .1)` of those people survived against `r scales::percent(am('SS Principessa Mafalda', 'surv_recorded'), accuracy = .1)` of the age-recorded; the *Princess Alice* shows the same direction even more sharply, `r scales::percent(am('SS Princess Alice', 'surv_missing'), accuracy = .1)` against `r scales::percent(am('SS Princess Alice', 'surv_recorded'), accuracy = .1)`. On the two wrecks that dominate the child counts, in other words, an age is far likelier to be missing for someone who lived. The `r format(nrow(pax_age), big.mark = ',')` complete-age passengers are a selected slice of their own wrecks, not merely a selected set of wrecks - and the adult check just quoted cannot detect that, because it is computed on the same slice.

The paper sidesteps part of this by falling back on the workbook's `Child` flag wherever an exact age is missing. Refit on that combined definition, across all `r n_distinct(combined$ship)` wrecks carrying either field, the passenger interaction is `r sprintf('%+.3f', coef(comb_pax)['female:child'])` (p = `r fmt_p(pvalue(comb_pax)['female:child'])`), or `r sprintf('%+.3f', coef(comb_pax_sat)['female:child'])` (p = `r fmt_p(pvalue(comb_pax_sat)['female:child'])`) once each wreck carries its own child and adult baselines. Restoring the `r format(nrow(combined_crew), big.mark = ',')` crew records adds almost only adults - `r sum(combined_crew$child)` of them are children - so that model has to adjust for crew status rather than pool it; done that way the interaction is `r sprintf('%+.3f', coef(comb_all)['female:child'])` (p = `r fmt_p(pvalue(comb_all)['female:child'])`, on `r degrees_freedom(comb_all, type = 't')` degrees of freedom), or `r sprintf('%+.3f', coef(comb_all_sat)['female:child'])` (p = `r fmt_p(pvalue(comb_all_sat)['female:child'])`) with per-wreck child and adult baselines as well. All four sit within a hair of the age-sixteen estimate below, which is reassuring about magnitude and settles nothing about the selection itself.

```r
child_results <- map_dfr(c(10, 12, 14, 16), function(cutoff) {
  z <- pax_age %>% mutate(child = as.integer(Age < cutoff))
  m <- feols(surv ~ female * child | ship, data = z, vcov = ~ship, ssc = cluster_ssc)
  b <- coef(m); V <- vcov(m)
  tibble(cutoff,
         girls = sum(z$female == 1 & z$child == 1),
         boys = sum(z$female == 0 & z$child == 1),
         adult_gap = b["female"],
         child_gap = b["female"] + b["female:child"],
         child_se = sqrt(V["female", "female"] + V["female:child", "female:child"] +
                           2 * V["female", "female:child"]),
         diff = b["female:child"], diff_se = se(m)["female:child"],
         diff_p = pvalue(m)["female:child"], crit = crit95(m))
}) %>% mutate(child_lo = child_gap - crit * child_se,
              child_hi = child_gap + crit * child_se,
              diff_lo = diff - crit * diff_se, diff_hi = diff + crit * diff_se)
adult_gap_16 <- child_results$adult_gap[child_results$cutoff == 16]

ggplot(child_results, aes(cutoff, child_gap)) +
  geom_hline(yintercept = 0, color = "#6B7280", linewidth = .5) +
  geom_hline(yintercept = adult_gap_16, color = rust, linetype = 2) +
  geom_ribbon(aes(ymin = child_lo, ymax = child_hi), fill = sand, alpha = .65) +
  geom_line(color = navy, linewidth = .8) + geom_point(color = navy, size = 2.6) +
  annotate("text", x = 15.8, y = adult_gap_16, hjust = 1, vjust = 1.4,
           label = "Adult passengers", color = rust) +
  scale_x_continuous(breaks = c(10, 12, 14, 16)) +
  scale_y_continuous(labels = scales::label_percent(accuracy = 1)) +
  labs(title = "Among child passengers, the estimated sex gap is near zero",
       x = "Age below cutoff", y = "Female survival gap")
```

![Female-minus-male survival gap among child passengers below each age cutoff, from surv ~ female × child | ship on the seven age-recording ships (delta-method bands, ship-clustered, t with six degrees of freedom). The dashed line is the same model's adult-passenger gap at the age-16 cutoff.](./female-survival-in-marital-disasters/generated-figure-05.png)

```r
child_boot_model <- lm(surv ~ female * child + factor(ship), data = z16)
wb_child <- wild_boot(child_boot_model, "female:child", 16)
# The crew section's restriction applies here too: `| ship` holds the child-adult
# survival difference constant across wrecks. Saturating on ship x child is the
# model that compares within-ship, within-age-group sex gaps.
child_sat <- feols(surv ~ female * child | ship^child, data = z16,
                   vcov = ~ship, ssc = cluster_ssc)
child_sat_cuts <- map_dfr(c(10, 12, 14, 16), function(cutoff) {
  m <- feols(surv ~ female * child | ship^child,
             data = mutate(pax_age, child = as.integer(Age < cutoff)),
             vcov = ~ship, ssc = cluster_ssc)
  tibble(cutoff, diff = unname(coef(m)["female:child"]),
         p = unname(pvalue(m)["female:child"]))
})
crew_adj <- feols(
  surv ~ female * child + crew | ship,
  data = ms %>% filter(ship %in% age_ships, !is.na(Age)) %>%
    mutate(child = as.integer(Age < 16)),
  vcov = ~ship, ssc = cluster_ssc
)
ships_with_both <- z16 %>% filter(child == 1) %>% group_by(ship) %>%
  summarise(both = all(c(0, 1) %in% female), .groups = "drop")
# Enumerated Rademacher reference set: 2^7 sign patterns, 2^6 distinct up to
# sign symmetry, so the smallest attainable two-sided p is 2/128.
child_boot_floor <- 2 / wb_child$B
stopifnot(sum(!is.na(ms$Age) & ms$Age < 16 & ms$crew == 1) == 3,
          nrow(pax_age) == 3009,
          child_results$girls[child_results$cutoff == 16] == 313,
          child_results$boys[child_results$cutoff == 16] == 268,
          nrow(ships_with_both) == 7, sum(ships_with_both$both) == 6,
          nrow(child_counts) == 7, sum(child_counts$n) == 581,
          child_counts$ship[1:2] == c("SS Norge", "SS Princess Alice"),
          abs(child_top2_share - .702) < .001,
          all(child_results$crit == qt(.975, 6)),
          abs(child_results$diff[child_results$cutoff == 16] - .1447) < .001,
          abs(child_results$diff[child_results$cutoff == 10] - .1622) < .001,
          abs(child_results$diff_p[child_results$cutoff == 16] - .0738) < .001,
          child_results$diff_lo[child_results$cutoff == 16] < 0,
          child_results$diff_lo[child_results$cutoff == 10] > 0,
          abs(wb_child$estimate -
                child_results$diff[child_results$cutoff == 16]) < 1e-8,
          wb_child$B == 128, abs(child_boot_floor - .015625) < 1e-12,
          wb_child$lo > 0, wb_child$hi > wb_child$lo,
          abs(coef(adult_only_7)["female"] - (-.1538)) < .001,
          abs(coef(crew_adj)["female:child"] - .1496) < .001,
          abs(pvalue(crew_adj)["female:child"] - .042) < .001,
          abs(coef(child_sat)["female:child"] - .1459) < .001,
          abs(pvalue(child_sat)["female:child"] - .070) < .001,
          degrees_freedom(child_sat, type = "t") == 6,
          all(child_sat_cuts$diff > .13), all(child_sat_cuts$diff < .17),
          sum(child_sat_cuts$p < .05) == 1,
          child_sat_cuts$cutoff[which.min(child_sat_cuts$p)] == 10)
```

```r
child_loo <- map_dfr(sort(unique(z16$ship)), function(omitted) {
  zz <- filter(z16, ship != omitted)
  m <- feols(surv ~ female * child | ship, data = zz, vcov = ~ship, ssc = cluster_ssc)
  wb <- wild_boot(lm(surv ~ female * child + factor(ship), data = zz),
                  "female:child", 31)
  tibble(omitted, estimate = unname(coef(m)["female:child"]),
         p = unname(pvalue(m)["female:child"]),
         boot_p = wb$p, boot_lo = wb$lo, boot_hi = wb$hi, B = wb$B)
})
child_loo_excl <- sum(child_loo$boot_lo > 0)
stopifnot(nrow(child_loo) == 7, all(child_loo$B == 64),
          all(child_loo$estimate > 0),
          abs(min(child_loo$estimate) - .0802) < .001,
          abs(max(child_loo$estimate) - .1912) < .001,
          child_loo$omitted[which.min(child_loo$estimate)] == "SS Norge",
          child_loo_excl == 4,
          max(abs(child_loo$estimate -
                    child_results$diff[child_results$cutoff == 16])) < .07)

ggplot(child_loo, aes(estimate, factor(omitted, levels = rev(sort(omitted))))) +
  geom_vline(xintercept = 0, color = "#6B7280", linewidth = .5) +
  geom_vline(xintercept = child_results$diff[child_results$cutoff == 16],
             color = "#6B7280", linetype = 2) +
  geom_errorbar(aes(xmin = boot_lo, xmax = boot_hi), width = .18, orientation = "y",
                color = navy) +
  geom_point(color = navy, size = 2.4) +
  scale_x_continuous(labels = scales::label_number(accuracy = .01)) +
  labs(title = "The child-adult contrast holds its sign but not its significance",
       x = "Female × child interaction", y = "Wreck omitted")
```

![Female × child interaction after omitting each age-recording wreck, with enumerated wild-bootstrap 95% intervals (64 distinct sign patterns per fit). The dashed line is the full seven-ship estimate.](./female-survival-in-marital-disasters/generated-figure-06.png)

At the sixteen-year cutoff, the adult female gap on these seven ships is `r sprintf('%+.3f', child_results$adult_gap[child_results$cutoff == 16])` and the gap among children is `r sprintf('%+.3f', child_results$child_gap[child_results$cutoff == 16])`. The quantity this section actually needs is the difference between those gaps, and the interaction estimates it directly: `r sprintf('%+.3f', child_results$diff[child_results$cutoff == 16])`, ship-clustered 95% CI `r sprintf('[%+.3f, %+.3f]', child_results$diff_lo[child_results$cutoff == 16], child_results$diff_hi[child_results$cutoff == 16])`, p = `r fmt_p(child_results$diff_p[child_results$cutoff == 16])`. On six degrees of freedom that interval includes zero. The enumerated wild bootstrap disagrees: `fwildclusterboot` runs all `r wb_child$B` sign patterns and returns `r sprintf('[%+.3f, %+.3f]', wb_child$lo, wb_child$hi)`, which excludes zero. Its p-value needs a word about convention. `boottest()` returns `r sprintf('%.0f', wb_child$p)` here, because it compares bootstrap statistics against the observed one strictly and no pattern exceeds it. But two patterns *equal* it: the `r wb_child$B` sign patterns collapse to `r wb_child$B / 2` distinct statistics under sign symmetry, and the identity pattern and its mirror reproduce the observed statistic by construction. Counting those ties inclusively - the conservative convention, and the one I use throughout - gives `r sprintf('2/%d = %.4f', wb_child$B, child_boot_floor)`, which is also the smallest value this reference set can produce. So the reported figure is a reporting choice on top of the package's output, not a number it printed.

Two caveats on that disagreement, and then the reading. The bootstrap interval is obtained by inverting the same coarse reference set, so its endpoints are step functions of the null value being tested, not smooth 95% limits; and with cells this small the enumerated test has very little power. Enumeration is also worth not over-reading: running all 128 patterns removes simulation error, not the procedure's assumptions. Sign-flip validity rests on cluster-level symmetry and on clusters being large, and it is asymptotic in cluster size rather than exact in finite samples. There is a result that fits this regime - [Canay, Santos and Shaikh (2021)](https://ivancanay.com/papers/wild-bootstrap-clusters-2021.pdf) justify the wild bootstrap with the cluster count held fixed and cluster sizes growing, which is exactly the corner seven ships put us in - but it comes with homogeneity-like restrictions on how similar the clusters are, and for a studentized statistic of this kind it bounds overrejection rather than delivering validity outright. Seven wrecks ranging from 70 to 796 passengers, with sex and age compositions as different as the *Princess Victoria*'s five boys and no girls against the *Norge*'s 131 girls and 127 boys, are not the homogeneous case. So I do not treat the bootstrap as the arbiter here. Two procedures disagree, neither has a strong claim on this sample, and the reading has to survive that: the child–adult difference is consistently positive and close to `r sprintf('%+.2f', child_results$diff[child_results$cutoff == 16])` across every specification below, and imprecise in all of them. Across cutoffs the estimate barely moves, from `r sprintf('%+.3f', min(child_results$diff))` to `r sprintf('%+.3f', max(child_results$diff))`, though only the age-ten cutoff produces a clustered interval that clears zero; and the interaction is `r sprintf('%+.3f', coef(crew_adj)['female:child'])` (p = `r fmt_p(pvalue(crew_adj)['female:child'])`) in the sensitivity check that restores the under-sixteen crew records and adjusts for crew status.

The crew section's specification point applies here as well, and it is worth settling rather than leaving implicit. `surv ~ female * child | ship` holds the child–adult survival difference constant across the seven wrecks, which is no more defensible for age than it was for crew status. Letting each wreck carry its own child and adult baselines, `| ship^child`, moves the interaction to `r sprintf('%+.3f', coef(child_sat)['female:child'])` (p = `r fmt_p(pvalue(child_sat)['female:child'])`) - and across the four cutoffs it stays between `r sprintf('%+.3f', min(child_sat_cuts$diff))` and `r sprintf('%+.3f', max(child_sat_cuts$diff))`, with the same single cutoff clearing 0.05 as before. On the nine-ship combined definition the saturated estimate is `r sprintf('%+.3f', coef(comb_pax_sat)['female:child'])` (p = `r fmt_p(pvalue(comb_pax_sat)['female:child'])`). Nothing in this section turns on which of the two specifications is used, which is the useful thing to know about it.

The leave-one-out gives the same three answers the British result gave. *Is the estimate stable?* Yes: positive in all seven omissions, from `r sprintf('%+.3f', min(child_loo$estimate))` (dropping the *Norge*, which alone supplies `r scales::percent(child_counts$n[1] / sum(child_counts$n), accuracy = .1)` of the children) to `r sprintf('%+.3f', max(child_loo$estimate))`. *Is significance stable?* No: the bootstrap interval excludes zero in `r child_loo_excl` of the seven subsamples and includes it in the other `r 7 - child_loo_excl`. *Is it causally interpretable?* No, for the reasons that opened this section - and now also because six contributing wrecks cannot carry an interaction this size with any precision. What the refits establish is the narrow claim: the contrast is not driven by any one age-recording wreck. That is weaker than calling it a real feature of these records, and deliberately so, because all seven refits run on the same age-recorded slice - the slice whose missingness this section already showed to be outcome-related, at `r scales::percent(am('SS Principessa Mafalda', 'missing'), accuracy = 1)` on the *Mafalda* with survival running `r scales::percent(am('SS Principessa Mafalda', 'surv_missing'), accuracy = 1)` among the age-missing against `r scales::percent(am('SS Principessa Mafalda', 'surv_recorded'), accuracy = 1)` among the age-recorded. Leave-one-out can rule out one ship. It cannot rule out the selection that chose which people got an age at all. It is not a finding I would defend at a threshold.

```r
kable(child_results %>% transmute(
  Cutoff = cutoff, Girls = girls, Boys = boys,
  `Adult gap` = sprintf("%+.3f", adult_gap),
  `Child gap` = sprintf("%+.3f", child_gap),
  `Difference (95% CI)` = sprintf("%+.3f [%+.3f, %+.3f]", diff, diff_lo, diff_hi),
  p = fmt_p(diff_p)
), align = c("r", "r", "r", "r", "r", "r", "r"),
caption = "Passenger-only interaction models, surv ~ female × child | ship, on the seven age-recording ships with ship-clustered SEs on six degrees of freedom. Adult and child gaps are the model's female coefficients for each group; the difference is the female × child interaction.") %>%
  kable_styling(full_width = FALSE, bootstrap_options = "striped")
```

Within these seven ships, the estimated girl–boy survival gap among passengers is near zero; the woman–man gap is not. What that supports is bounded by the caveats that opened this section. A near-zero child gap alongside a large adult one is consistent with a physical-capacity contribution to the adult gap - and equally consistent with rescue norms that sheltered children of both sexes, and with survival mediated by whichever adult held the child. Six of the seven ships record children of both sexes, two of them supply seven children in ten, and seven ships are few. The comparison narrows the story; it does not identify a mechanism, and no share of the adult gap can be attributed to bodies on this evidence.

# Comparing crew and passengers

I expected the crew comparison to make the gap smaller. Crew share training, ship knowledge, drills, and early information, so a gap driven mostly by access and information should shrink among them. The point estimate moves the other way.

```r
crew_int <- feols(surv ~ female * crew | ship, data = ms,
                  vcov = ~ship, ssc = cluster_ssc)
crew_boot_model <- lm(surv ~ female * crew + factor(ship), data = ms)
wb_crew <- wild_boot(crew_boot_model, "female:crew", 21)
crew_counts <- ms %>% filter(crew == 1) %>% group_by(ship) %>%
  summarise(f = sum(female == 1), m = sum(female == 0), .groups = "drop")
crew_gap_pax <- unname(coef(crew_int)["female"])
crew_gap_crew <- unname(coef(crew_int)["female"] + coef(crew_int)["female:crew"])
crew_diff <- unname(coef(crew_int)["female:crew"])
crew_diff_se <- unname(se(crew_int)["female:crew"])
# `| ship` holds the crew-passenger survival difference constant across wrecks.
# Letting every ship have its own crew and passenger baseline is the model that
# actually compares within-ship, within-status sex gaps.
crew_sat <- feols(surv ~ female * crew | ship^crew, data = ms,
                  vcov = ~ship, ssc = cluster_ssc)
crew_sat_diff <- unname(coef(crew_sat)["female:crew"])
crew_sat_gap_crew <- unname(coef(crew_sat)["female"] + coef(crew_sat)["female:crew"])
stopifnot(abs(crew_sat_diff - (-.0631)) < .001,
          abs(pvalue(crew_sat)["female:crew"] - .114) < .001,
          degrees_freedom(crew_sat, type = "t") == 15,
          crew_sat_diff < 0, crew_sat_diff > crew_diff,
          abs(crew_diff - (-.0993)) < .001,
          abs(wb_crew$estimate - crew_diff) < 1e-8,
          degrees_freedom(crew_int, type = "t") == 15,
          abs(pvalue(crew_int)["female:crew"] - .062) < .001,
          crew_diff + crit95(crew_int) * crew_diff_se > 0,
          wb_crew$lo < crew_diff - crit95(crew_int) * crew_diff_se,
          wb_crew$hi > crew_diff + crit95(crew_int) * crew_diff_se,
          sum(crew_counts$f) == 278, sum(crew_counts$f > 0) == 14,
          sum(crew_counts$f[crew_counts$ship %in%
                              c("MS Estonia", "SS Admiral Nakhimov")]) == 218)
crew_ship_gaps <- ms %>% group_by(ship, crew) %>% summarise(
  gap = if (all(c(0, 1) %in% female)) mean(surv[female == 1]) - mean(surv[female == 0]) else NA_real_,
  .groups = "drop") %>% mutate(group = ifelse(crew == 1, "Crew", "Passengers")) %>%
  left_join(ship_gaps %>% select(ship, year), by = "ship") %>%
  mutate(ship_year = factor(paste0(ship, " (", year, ")"), levels = levels(ship_gaps$ship_year)))

crew_ship_plot <- crew_ship_gaps %>%
  select(ship, ship_year, group, gap) %>%
  pivot_wider(names_from = group, values_from = gap) %>%
  rename(crew_gap = Crew, passenger_gap = Passengers)

ggplot(crew_ship_plot, aes(y = ship_year)) +
  geom_vline(xintercept = 0, color = "#6B7280", linewidth = .5) +
  geom_segment(aes(x = passenger_gap, xend = crew_gap, yend = ship_year),
               color = "#AAB2BD", linewidth = .8, na.rm = TRUE) +
  geom_point(aes(x = passenger_gap, color = "Passengers"), size = 2.6,
             na.rm = TRUE) +
  geom_point(aes(x = crew_gap, color = "Crew"), size = 2.6,
             na.rm = TRUE) +
  scale_color_manual(values = c(Crew = rust, Passengers = blue)) +
  scale_x_continuous(labels = scales::label_percent(accuracy = 1)) +
  labs(title = "Sex gaps within crew and within passengers, wreck by wreck",
       x = "Female survival minus male survival", y = NULL, color = NULL)
```

![Raw female-minus-male survival gaps within crew and passenger groups. Lines connect estimates from the same wreck; a single endpoint means the other group has recorded members of only one sex.](./female-survival-in-marital-disasters/generated-figure-07.png)

The direct test is a single interaction model, `surv ~ female * crew | ship` - unweighted, like the descriptive crew model earlier, so the estimand is the person-level within-ship contrast. It puts the female gap at `r sprintf('%+.3f', crew_gap_pax)` among passengers and `r sprintf('%+.3f', crew_gap_crew)` among crew. Whether those two gaps differ is the `female × crew` term: `r sprintf('%+.3f', crew_diff)`, ship-clustered 95% CI `r ci_text(crew_int, 'female:crew')`, p = `r fmt_p(pvalue(crew_int)['female:crew'])`. The wild cluster bootstrap widens that interval further, to `r sprintf('[%+.3f, %+.3f]', wb_crew$lo, wb_crew$hi)` with p = `r fmt_p(wb_crew$p)`. Both procedures agree here, which the child section could not say.

That specification does impose something, though, and it is worth relaxing before reading a size off it. With `| ship` alone, the crew–passenger survival difference is a single pooled coefficient, held constant across sixteen very different wrecks - a real restriction when four in five female crew records come from two of them. Letting each ship carry its own crew and passenger baseline, `surv ~ female * crew | ship^crew`, moves the interaction to `r sprintf('%+.3f', crew_sat_diff)` (p = `r fmt_p(pvalue(crew_sat)['female:crew'])`) and the crew gap to `r sprintf('%+.3f', crew_sat_gap_crew)`. So the sign is stable and the magnitude is not: the female disadvantage among crew runs somewhere between about half again and twice the passenger gap depending on which baselines the model is allowed to vary. Under either specification the crew–passenger difference remains too imprecisely estimated to state as a finding.

Composition is part of the reason. Female crew appear on `r sum(crew_counts$f > 0)` of the sixteen ships, but `r sum(crew_counts$f[crew_counts$ship %in% c('MS Estonia', 'SS Admiral Nakhimov')])` of the `r sum(crew_counts$f)` female crew records - nearly four in five - come from two late wrecks. On the *Estonia*, `r scales::percent(mean(ms$surv[ms$ship == 'MS Estonia' & ms$crew == 1 & ms$female == 1]), accuracy = 1)` of female crew survived against `r scales::percent(mean(ms$surv[ms$ship == 'MS Estonia' & ms$crew == 1 & ms$female == 0]), accuracy = 1)` of male crew; on the *Admiral Nakhimov*, `r scales::percent(mean(ms$surv[ms$ship == 'SS Admiral Nakhimov' & ms$crew == 1 & ms$female == 1]), accuracy = 1)` against `r scales::percent(mean(ms$surv[ms$ship == 'SS Admiral Nakhimov' & ms$crew == 1 & ms$female == 0]), accuracy = 1)`. Those two disasters dominate the within-crew comparison; they illustrate the pattern rather than independently confirm it.

Occupational geography is a likely reconciliation. Stewardesses and catering staff often worked and slept inside or below decks; deck and engine crews were more often male and nearer boats. The spreadsheet has no crew-role field, so this remains a hypothesis. Public manifests for the *Titanic*, *Lusitania*, *Empress of Ireland*, and *Estonia* could test it.

# What survives

```r
raw_ratio <- mean(ms_h1$surv[ms_h1$female == 1]) /
  mean(ms_h1$surv[ms_h1$female == 0])
# 17.9 and 34.6 are the fitted values for whichever wreck the ship dummies omit,
# not adjusted averages. Standardizing over the sample instead of over a single
# reference wreck is what makes the number comparable to the raw rates.
ref_fit <- lm(surv ~ female + factor(ship), data = ms_h1)
ref_male <- unname(coef(ref_fit)[1])
ref_female <- ref_male + unname(coef(ref_fit)["female"])
std_male <- mean(predict(ref_fit, mutate(ms_h1, female = 0)))
std_female <- mean(predict(ref_fit, mutate(ms_h1, female = 1)))
std_ratio <- std_female / std_male
ref_ratios <- map_dbl(sort(unique(ms_h1$ship)), function(s) {
  cf <- coef(lm(surv ~ female + shipf,
                data = mutate(ms_h1, shipf = relevel(factor(ship), ref = s))))
  (cf[[1]] + cf[["female"]]) / cf[[1]]
})
stopifnot(abs(raw_ratio - .602) < .001,
          levels(factor(ms_h1$ship))[1] == "HMS Birkenhead",
          abs(ref_male - .346) < .001, abs(ref_female - .179) < .001,
          abs(ref_female - ref_male - coef(h1_robust)["female"]) < 1e-12,
          abs(ref_female / ref_male - .517) < .001,
          abs(std_ratio - .620) < .001,
          min(ref_ratios) < -.2, max(ref_ratios) > .79)
```

Women really did fare worse. In the main sample their raw survival rate is `r scales::percent(mean(ms_h1$surv[ms_h1$female == 1]), accuracy = .1)`, versus `r scales::percent(mean(ms_h1$surv[ms_h1$female == 0]), accuracy = .1)` for men - a raw ratio of `r sprintf('%.2f', raw_ratio)`. This is the “roughly half” claim flagged at the beginning: the broad description is defensible, but the particular numbers behind it are more slippery than they first appear. The paper’s “about half” (17.9% versus 34.6%) is a different quantity than it appears to be, and it is worth separating from the coefficient it accompanies. Those two numbers are the ship-dummy regression's constant and constant-plus-female-coefficient - but a regression constant belongs to whichever wreck the software happened to omit, here the *Birkenhead*, whose men survived at about a third. Omit a different wreck and the identical fitted model reports ratios anywhere from `r sprintf('%.2f', min(ref_ratios))` to `r sprintf('%.2f', max(ref_ratios))`, all while the `r sprintf('%.3f', coef(h1_robust)['female'])` coefficient never moves. Standardize over the whole sample instead and the adjusted ratio is `r sprintf('%.2f', std_ratio)` - essentially where the raw rates already sat. So adjustment does not sharpen the ratio. What is reference-category dependent is the quoted pair, not the broader framing it was used to support: 17.9 versus 34.6 belongs to whichever wreck the model omits, while the raw and standardized ratios - `r sprintf('%.2f', raw_ratio)` and `r sprintf('%.2f', std_ratio)` - do not move at all, and are close enough to "about half" to leave the phrase itself standing. It is the pair that should not be quoted. The durable quantity is the `r sprintf('%.1f', abs(coef(h1_robust)['female']) * 100)`-percentage-point difference rather than any ratio built from a constant. Even that difference is one average among several, as the sixteen dots showed: `r sprintf('%.1f', abs(mean(gap_w$gap)) * 100)` points averaging the wrecks plainly, `r sprintf('%.1f', abs(coef(h1_robust)['female']) * 100)` under ship fixed effects, `r sprintf('%.1f', abs(coef(h1_eqship)['female']) * 100)` under the paper's equal-ship weights. The range is the honest statement of it, and every point in that range is a large female disadvantage. The robustness checks are narrower than that range, and worth attributing precisely: the headline fixed-effects difference is what survives clustered inference, the wild bootstrap, and the adversarial reassignment of every unknown-sex record, and the adult-only estimates are what stay negative across every age definition. Crew really did survive more than passengers. Those are the durable descriptive findings.

The data do not estimate the proposed explanations precisely enough to support them. Captain's orders rest on three treated ships; Britishness and the postwar change are comparisons across sixteen wrecks that no one randomized. With uncertainty measured at the ship level, the captain's-order and postwar intervals contain zero and effects large enough to matter in either direction; the design cannot adjudicate them. The British comparison is the closest call: its estimate stays negative in every leave-one-out subsample (`r sprintf('%+.3f', loo_summary$lo[loo_summary$variable == 'british'])` to `r sprintf('%+.3f', loo_summary$hi[loo_summary$variable == 'british'])`), while its p-value never reaches 0.050 on the full sample and swings from `r fmt_p(loo_summary$best_p[loo_summary$variable == 'british'])` to `r fmt_p(loo_summary$worst_p[loo_summary$variable == 'british'])` as single wrecks come and go, and "British" remains a bundle of period, route, vessel, and record-keeping that sixteen ships cannot unbundle. "Every man for himself" is a memorable interpretation of the average, not a mechanism these data identify. The average it interprets spans wrecks from `r sprintf('%+.3f', max(ship_gaps$gap))` to `r sprintf('%+.3f', min(ship_gaps$gap))`.

The child comparison shifts the moral reading without settling it: the estimated sex gap is near zero among child passengers and large among adults, and the difference between the two is estimated directly rather than inferred from two subgroup tests. But that difference sits exactly where the two inference procedures part company - the clustered interval on six degrees of freedom includes zero, the enumerated bootstrap interval does not - and with seven unequal wrecks neither procedure has a strong enough claim on this sample to break the tie. The point estimate is the steadier part: close to `r sprintf('%+.2f', child_results$diff[child_results$cutoff == 16])` whether the model saturates ship × child or not, and whether the sample is the seven age-recording wrecks or the nine the paper's combined definition allows. Leave-one-out is looser than that - positive in all seven omissions, but running from `r sprintf('%+.3f', min(child_loo$estimate))` to `r sprintf('%+.3f', max(child_loo$estimate))` - so the sign is stable and the size only broadly so. Imprecise in every one of them. Rescue norms or adult-mediated survival could produce the same pattern as physical differences in any case. The crew comparison blocks a tidy ending from the other side: crew status does not visibly close the gap. Crew status is only a proxy for training, information, and access - the workbook records no occupation and no location aboard - so what fails to close the gap is the proxy, and unmeasured job location remains a live alternative to any reading of that; the crew–passenger difference is imprecise in its own right besides. The records support a sturdy descriptive claim. They cannot apportion it among strength, clothing, access, occupational segregation, and men's refusal to help - those remain hypotheses.

So, where did we end up? The Titanic can definitely keep its place in the data-science classroom. That one ship taught many of us logistic regression, but the others teach the harder lesson: a sturdy coefficient is not the same thing as a tidy explanation 😉

P.S. Kudos to Elinder and Erixson for making the data public and letting the rest of us take it for another spin 🤓

```r
sessionInfo()
```

<!-- RELATED:BEGIN -->
## Related notes
- [[did-with-repeated-cross-sectional-data|What a European cigarette tax study taught me about employee listening]]
- [[segmentedregression|Modeling impact of the COVID-19 pandemic on people’s interest in work-life balance and well-being]]
- [[dag-and-double-ml|A plausible model of data-generating process eats ML algorithms for breakfast]]
- [[impact-of-pets-on-life-satisfaction|Before you believe the £70,000 cat]]
- [[car-accidents-near-home|Before you blame the driver, check the denominator]]
<!-- RELATED:END -->

---
> 📄 Read the [original post with full outputs](https://blog-about-people-analytics.netlify.app/posts/2026-08-06-female-survival-in-marital-disasters/) on my blog.
