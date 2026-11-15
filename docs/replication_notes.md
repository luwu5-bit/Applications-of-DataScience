# Replication notes

Running log of where our numbers differ from the paper and what we checked.
Input for the "critical evaluation" part of the presentation and report.

## E1 (m = 5, N = 20, 100 groups, S = 10,000), 2026-11-14

nDCG@20, mean over 100 groups, ± = 95% CI half-width. Source: `results/E1.csv`.

| | Fairness RND | Fairness SIM | Group utility RND | Group utility SIM |
|---|---|---|---|---|
| AVG ours | 0.204 ± 0.026 | 0.305 ± 0.034 | 0.480 ± 0.022 | 0.576 ± 0.027 |
| AVG paper | 0.298 | 0.437 | 0.455 | 0.577 |
| LM ours | 0.093 ± 0.018 | 0.181 ± 0.028 | 0.327 ± 0.027 | 0.453 ± 0.031 |
| LM paper | 0.197 | 0.403 | 0.341 | 0.542 |
| NPO ours | 0.142 ± 0.021 | 0.234 ± 0.029 | 0.378 ± 0.026 | 0.488 ± 0.031 |
| NPO paper | 0.311 | 0.472 | 0.466 | 0.601 |
| XPO ours | 0.224 ± 0.024 | 0.320 ± 0.027 | 0.433 ± 0.027 | 0.545 ± 0.028 |
| XPO paper | 0.406 | 0.579 | 0.532 | 0.674 |

Mean pool size: NPO 88 (RND) / 73 (SIM) of 200 items, XPO 26 / 23.

### What matches
- XPO has the highest fairness and LM the lowest, for RND and SIM.
- SIM groups score higher than RND groups for every method.
- AVG group utility is close to the paper (0.480 vs 0.455, 0.576 vs 0.577).
- NPO is best or near-best on the first rank (P@1 fairness 0.71 vs AVG 0.54), as the paper says.

### What does not match
- **NPO is below AVG** on nDCG@20 fairness (paired difference -0.063 ± 0.013 RND, -0.071 ± 0.018 SIM). Paper: NPO slightly above AVG.
- **XPO's lead over AVG is small**: +0.020 ± 0.018 (RND), +0.015 ± 0.022 (SIM, not significant). Paper: +0.108 and +0.142.
- **AVG, not XPO, has the highest group utility.** Paper: XPO.
- Fairness levels are lower than the paper's for all methods.

### What we ruled out (m = 5, N = 20, same 100 groups, nDCG@20 fairness)

| Variant | AVG RND | NPO RND | XPO RND | AVG SIM | NPO SIM | XPO SIM |
|---|---|---|---|---|---|---|
| Current (real ratings kept, clipped, 50 factors) | 0.204 | 0.142 | 0.224 | 0.305 | 0.234 | 0.320 |
| MF predictions for all pairs, not clipped | 0.244 | 0.197 | 0.278 | 0.396 | 0.349 | 0.401 |
| MF predictions for all pairs, clipped | 0.245 | 0.199 | 0.281 | 0.392 | 0.350 | 0.402 |
| MF with 10 factors, predictions for all pairs | 0.204 | 0.146 | 0.235 | 0.368 | 0.315 | 0.378 |
| Current with S = 50,000 | 0.204 | 0.142 | 0.224 | 0.305 | 0.233 | 0.319 |

The ordering XPO >= AVG > NPO > LM is the same in every variant, so it is not
caused by S, by keeping the real ratings, by clipping, or by the MF size.
Keeping the real ratings lowers all levels (rated movies with integer scores
dominate each member's top-20 and differ between members). These variants were
diagnostics only; no setting was changed because of them.

### The paper's nDCG values do not fit its printed formula
The paper defines gain 2^rel with rel = N - p + 1 (up to 20). We use 2^rel - 1 so
that a movie outside the ground truth earns nothing (A11); at N = 20 both forms
give the same numbers to 3 decimals. Under either form nDCG@1 is about
2^(rel - 20): 1 only if the first group item is the member's own number 1, 0.5
if it is their number 2, and so on. nDCG@1 must therefore be far below P@1.
In the paper's Table 1 they are almost equal (AVG group utility: nDCG@1 0.694,
P@1 0.702; same pattern in every row). With five random users this is not
possible under the printed formula. Our values under the printed formula:
nDCG@1 0.280 vs P@1 0.876.

Same groups and lists, different gain (diagnostic, RND, nDCG@20 fairness):

| Gain | AVG | LM | NPO | XPO |
|---|---|---|---|---|
| 2^rel - 1 (our default; 2^rel as printed gives the same) | 0.204 | 0.093 | 0.142 | 0.224 |
| rel (linear) | 0.425 | 0.313 | 0.407 | 0.474 |
| 1 if in ground truth (binary) | 0.455 | 0.365 | 0.463 | 0.491 |

With a less top-heavy gain XPO's lead grows and NPO moves up to AVG, closer to
the paper's picture. We cannot tell which gain the paper really used.

## New issues found in the paper

- **Fairness P@1 column in Tables 1 and 2 is a copy of group-utility P@10.**
  Every row has identical values in both columns (AVG RND 0.490 / 0.490, XPO RND
  0.566 / 0.566, AVG SIM 0.633 / 0.633, ...). The fairness P@1 values are also
  implausibly high next to fairness P@5.
- **nDCG values are inconsistent with the printed DCG formula** (see above).
- **Ties in the Monte Carlo counts are not addressed.** When the XPO pool has
  exactly N items, every item has the same count and the order of the list is
  undefined. We break ties by mean rank (ASSUMPTIONS.md, A13).
- **BORDA is far below AVG for similar users** (SIM nDCG@20 fairness 0.203 vs
  0.437). For like-minded users mean rank and mean rating should give similar
  lists. This suggests the paper's ranks are not exact ranks over the 200
  candidates (possibly the top-N' approximation), which would also affect NPO/XPO.

## E2 / E3 group size (N = 20, 100 groups per setting), 2026-11-14

Source: `results/E2.csv` (m = 2..8) and `results/E3.csv` (m = 2..30). Groups are
keyed by (type, m, N, id), so settings shared by E1, E2 and E3 use the same groups
and give the same numbers.

Fairness, nDCG@20, RND:

| m | 2 | 3 | 5 | 8 | 10 | 15 | 20 | 30 |
|---|---|---|---|---|---|---|---|---|
| AVG | 0.532 | 0.339 | 0.204 | 0.110 | 0.110 | 0.054 | 0.048 | 0.029 |
| LM | 0.314 | 0.187 | 0.093 | 0.043 | 0.037 | 0.016 | 0.010 | 0.006 |
| NPO | 0.415 | 0.247 | 0.142 | 0.082 | 0.082 | 0.041 | 0.035 | 0.021 |
| XPO | 0.497 | 0.357 | 0.224 | 0.144 | 0.109 | 0.047 | 0.039 | 0.022 |

Fairness, nDCG@20, SIM:

| m | 2 | 3 | 5 | 8 | 10 | 15 | 20 | 30 |
|---|---|---|---|---|---|---|---|---|
| AVG | 0.623 | 0.420 | 0.305 | 0.209 | 0.185 | 0.124 | 0.097 | 0.064 |
| LM | 0.460 | 0.282 | 0.181 | 0.124 | 0.086 | 0.048 | 0.030 | 0.021 |
| NPO | 0.535 | 0.338 | 0.234 | 0.168 | 0.144 | 0.089 | 0.078 | 0.052 |
| XPO | 0.596 | 0.442 | 0.320 | 0.225 | 0.193 | 0.115 | 0.091 | 0.053 |

XPO minus AVG, paired over groups, RND (95% CI half-width):
m=2 -0.035 ± 0.022, m=3 +0.018 ± 0.023, m=5 +0.020 ± 0.018, m=8 +0.034 ± 0.016,
m=10 -0.001 ± 0.010, m=15 -0.008 ± 0.005, m=20 -0.009 ± 0.006, m=30 -0.007 ± 0.004.

Pool size (of 200 candidates) and XPO level x:

| m | 2 | 3 | 5 | 8 | 10 | 15 | 20 | 30 |
|---|---|---|---|---|---|---|---|---|
| NPO pool RND | 43 | 62 | 88 | 109 | 117 | 134 | 145 | 159 |
| XPO pool RND | 21 | 22 | 26 | 30 | 37 | 51 | 61 | 80 |
| XPO level x RND | 7.6 | 4.3 | 2.1 | 1.2 | 1.2 | 1.0 | 1.0 | 1.0 |
| NPO pool SIM | 39 | 52 | 73 | 93 | 102 | 114 | 127 | 142 |
| XPO pool SIM | 21 | 21 | 23 | 27 | 29 | 38 | 45 | 61 |
| XPO level x SIM | 9.2 | 5.7 | 2.8 | 1.8 | 1.4 | 1.1 | 1.0 | 1.0 |

Runtime per group: NPO 2 ms (m = 2) to 12 ms (m = 30), XPO 0.7 to 7.5 ms, AVG and LM below 0.1 ms.

### Findings
- Fairness falls quickly with group size for every method (as in the paper's Fig. 2/3), and SIM stays above RND.
- **XPO beats AVG only for mid-sized groups (m = 3 to 8)**, and only at m = 8 (RND) is the lead clearly significant. At m = 2 AVG is better; from m = 15 on AVG is slightly but significantly better.
- **Hypothesis "NPO pool approaches all items": partly confirmed.** The NPO pool grows from 22% to 79% of the candidates (RND), not to 100%.
- **Hypothesis "XPO stays selective": not confirmed for large groups.** From m = 15 on the level is x = 1 in almost every group, so XPO cannot shrink its pool any further: the plain Pareto-optimal set alone already has 51 to 80 items. XPO and NPO then give nearly the same fairness (0.022 vs 0.021 at m = 30).
- NPO is below AVG at every group size on nDCG@20. On P@20 and AP the three are close.
- AVG has the highest group utility at every group size.
- The tie case (XPO pool of exactly 20 items, A13) is frequent for small groups: 47% of RND groups at m = 2, 14% at m = 5, 0% from m = 15.

## E5 Monte Carlo sensitivity (RND, N = 20, 100 groups), 2026-11-14

Mean nDCG@20 fairness by number of weight samples S (`results/E5.csv`):

| | S = 1,000 | 5,000 | 10,000 | 50,000 |
|---|---|---|---|---|
| NPO, m = 5 | 0.1423 | 0.1404 | 0.1419 | 0.1422 |
| XPO, m = 5 | 0.2224 | 0.2237 | 0.2240 | 0.2240 |
| NPO, m = 20 | 0.0361 | 0.0350 | 0.0350 | 0.0352 |
| XPO, m = 20 | 0.0392 | 0.0390 | 0.0394 | 0.0392 |

Mean absolute change per group against S = 50,000 is at most 0.001 at S = 10,000
(0.003 at S = 1,000). S = 10,000 is enough, also for m = 20. The sampling noise
is far smaller than the differences between methods and the CI over groups.

## A5 check: how SIM groups are built (N = 20, 100 groups per setting), 2026-11-15

The paper builds SIM groups "by adding the most similar user to the group". We
add the users most similar **to the seed user** (A5). The other reading is to
add, at each step, the user with the highest mean similarity **to all members so
far**. Diagnostic run of that reading with the same seed users and the same 200
candidates per group; nothing in the main results was changed.

The group-based reading gives clearly different and tighter groups. At m = 5
only 2.7 of 5 members are the same on average, and the mean pairwise similarity
is 0.218 instead of 0.167 (m = 30: 0.176 vs 0.095).

Fairness, nDCG@20, SIM (seed = our main results, group = diagnostic):

| m | 2 | 3 | 5 | 8 | 10 | 15 | 20 | 30 |
|---|---|---|---|---|---|---|---|---|
| AVG seed | 0.623 | 0.420 | 0.305 | 0.209 | 0.185 | 0.124 | 0.097 | 0.064 |
| AVG group | 0.623 | 0.464 | 0.333 | 0.216 | 0.195 | 0.139 | 0.111 | 0.086 |
| LM seed | 0.460 | 0.282 | 0.181 | 0.124 | 0.086 | 0.048 | 0.030 | 0.021 |
| LM group | 0.460 | 0.320 | 0.215 | 0.118 | 0.100 | 0.057 | 0.044 | 0.042 |
| NPO seed | 0.535 | 0.338 | 0.234 | 0.168 | 0.144 | 0.089 | 0.078 | 0.052 |
| NPO group | 0.535 | 0.387 | 0.270 | 0.167 | 0.154 | 0.099 | 0.096 | 0.068 |
| XPO seed | 0.596 | 0.442 | 0.320 | 0.225 | 0.193 | 0.115 | 0.091 | 0.053 |
| XPO group | 0.596 | 0.467 | 0.359 | 0.239 | 0.215 | 0.136 | 0.114 | 0.080 |

XPO minus AVG, paired over groups (95% CI half-width):

| m | 2 | 3 | 5 | 8 | 10 | 15 | 20 | 30 |
|---|---|---|---|---|---|---|---|---|
| seed | -0.026 ± 0.017 | +0.022 ± 0.022 | +0.015 ± 0.022 | +0.015 ± 0.016 | +0.009 ± 0.016 | -0.009 ± 0.012 | -0.005 ± 0.011 | -0.011 ± 0.006 |
| group | -0.026 ± 0.017 | +0.002 ± 0.020 | +0.026 ± 0.020 | +0.023 ± 0.017 | +0.020 ± 0.017 | -0.003 ± 0.017 | +0.002 ± 0.008 | -0.006 ± 0.009 |

### Findings
- Fairness is higher for every method with group-based SIM groups, by 0.01 to
  0.04 (at m = 2 both readings give the same group). The gain is small next to
  the gap to the paper: XPO at m = 5 is 0.359 instead of 0.320, paper 0.579.
- The ordering does not change: XPO >= AVG > NPO > LM at m = 5, NPO below AVG
  at every size, AVG best on group utility at every size.
- XPO's lead over AVG becomes significant at m = 5, 8 and 10 (it was not
  significant at any size for SIM with seed-based groups), but stays at 0.02 to
  0.03. For m = 2 and m >= 15 XPO is still not better than AVG.
- Pools are a little smaller (NPO 131 vs 142, XPO 52 vs 61 at m = 30).
- Conclusion: A5 explains a small part of the lower SIM levels and none of the
  differences in ordering. We keep the seed-based choice and report this check.

