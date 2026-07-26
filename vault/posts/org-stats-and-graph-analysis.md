---
title: 'A graph approach to reporting structures: stop wrestling recursion'
description: About a cleaner, faster way to compute some org metrics.
date: '2025-10-31'
tags:
- people-analytics
- network-analysis
- python
original: https://blog-about-people-analytics.netlify.app/posts/2025-10-31-org-stats-and-graph-analysis/
---

From time to time, I need to compute organizational stats related to manager-report relationships.

I used to do this with nested loops or a recursive walk through the org chart plus memoization (i.e., caching results to avoid recomputation). It works - but it’s verbose and easy to get wrong (recursion limits, cycle guards, cache invalidation).

Recently I came upon a much more elegant and clear solution: rely on graph libraries like `NetworkX`, whose built-in functions let me easily traverse manager-report relationships and compute the metrics I need.

Some quick wins with this approach:️

* **Span of control**: direct reports (number of outgoing links from a manager) vs. total reports (number of unique people reachable by following those links through all levels).️
* **Org depth / layers**: shortest-path lengths from a chosen root to its descendants.️
* **Dotted-line structures**: multiple managers are fine; compute totals via unique descendants (no double-counting).️
* **Data quality checks**: detect cycles (impossible loops) and find disconnected sub-orgs.️
* **Fewer footguns**: no hand-rolled recursion, cycle guards, or bespoke caches.️
* **Extensibility**: once it’s a graph, adding metrics (e.g., centralities, bridges) is just another function call.️
* **Clarity & auditability**: easier to review than nested recursion with custom memoization.

So if you’re computing org stats and your code is full of nested loops, `NetworkX` and other similar libraries can make it shorter, safer, and more expressive. I only wish I’d discovered this earlier - I could have saved myself a lot of headaches 🫣

P.S. Below is a minimal working example of Python code that builds edges from `manager_id` → `employee_id`, followed by a simple loop to compute direct, indirect, and total reports for every manager.

```
import pandas as pd
import networkx as nx

# mydata: columns ['manager_id', 'employee_id']
df = (mydata.dropna(subset=['manager_id','employee_id'])  
              .drop_duplicates(['manager_id','employee_id']))
df = df[df['manager_id'] != df['employee_id']]  # drop self-loops just in case

G = nx.DiGraph()
G.add_edges_from(df[['manager_id','employee_id']].itertuples(index=False, name=None))

# Managers = anyone who manages at least one person
managers = set(df['manager_id'])

rows = []
for m in managers:
    total = len(nx.descendants(G, m))    # all reports at any depth (unique people)
    direct = G.out_degree(m)             # direct reports
    rows.append((m, direct, total - direct, total))

out = (pd.DataFrame(rows, columns=['manager_id','direct','indirect','total'])
         .sort_values(['total','direct'], ascending=False))

```

<!-- RELATED:BEGIN -->
## Related notes
- [[span-of-control-and-managerial-behavior|Can flatter orgs undermine people management?]]
- [[induced-centrality|Induced centralities]]
- [[multilevel-modeling|Multilevel modeling in people analytics]]
- [[corporate-culture-trade-offs|The hidden trade-offs in corporate culture?]]
- [[org-chart-and-collaboration|Org chart and collaboration]]
<!-- RELATED:END -->

---
> 📄 Read the [original post with full outputs](https://blog-about-people-analytics.netlify.app/posts/2025-10-31-org-stats-and-graph-analysis/) on my blog.
