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
