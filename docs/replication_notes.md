# Replication notes

Where our numbers differ from the paper, what we checked, and what changed along
the way. Input for the "critical evaluation" part of the presentation and report.

All results below use the settings in force since 2026-11-15 (see
`ASSUMPTIONS.md`): nDCG gain 2^rel as printed (A11), SIM groups grown by
similarity to the whole group (A5), tied ranks for equally rated movies (A4).
The section "Changes on 2026-11-15" shows what each of these moved.
nDCG@20, 100 groups per setting, S = 10,000, ± = 95% CI half-width.

## E1 (m = 5, N = 20)

Source: `results/E1.csv`.

| | Fairness RND | Fairness SIM | Group utility RND | Group utility SIM |
|---|---|---|---|---|
| AVG ours | 0.204 ± 0.026 | 0.333 ± 0.035 | 0.480 ± 0.022 | 0.589 ± 0.027 |
| AVG paper | 0.298 | 0.437 | 0.455 | 0.577 |
| LM ours | 0.093 ± 0.018 | 0.215 ± 0.033 | 0.327 ± 0.027 | 0.470 ± 0.031 |
| LM paper | 0.197 | 0.403 | 0.341 | 0.542 |
| NPO ours | 0.142 ± 0.021 | 0.266 ± 0.035 | 0.375 ± 0.026 | 0.503 ± 0.032 |
| NPO paper | 0.311 | 0.472 | 0.466 | 0.601 |
| XPO ours | 0.202 ± 0.024 | 0.335 ± 0.034 | 0.420 ± 0.027 | 0.552 ± 0.029 |
| XPO paper | 0.406 | 0.579 | 0.532 | 0.674 |

Mean pool size: NPO 88 (RND) / 71 (SIM) of 200 items, XPO 26 / 23.

### What matches
- XPO is clearly fairer than NPO (+0.061 ± 0.014 RND, +0.069 ± 0.015 SIM), and LM is last.
- SIM groups score higher than RND groups for every method.
- AVG group utility is close to the paper (0.480 vs 0.455, 0.589 vs 0.577).
- NPO is best on the first rank (P@1 fairness 0.71 vs AVG 0.54 RND, 0.89 vs 0.70 SIM), as the paper says.

### What does not match
- **XPO is not fairer than AVG.** Paired difference -0.002 ± 0.015 (RND) and
  +0.003 ± 0.018 (SIM). Paper: +0.108 and +0.142.
- **NPO is below AVG** (-0.063 ± 0.013 RND, -0.067 ± 0.016 SIM). Paper: NPO slightly above AVG.
- **AVG, not XPO, has the highest group utility** (XPO - AVG: -0.061 ± 0.014 RND, -0.037 ± 0.012 SIM). Paper: XPO.
- Fairness levels are lower than the paper's for all methods.

So the ordering on fairness is XPO = AVG > NPO > LM, not the paper's
XPO > NPO > AVG > LM.

## Sensitivity checks at m = 5 and m = 8

Diagnostics only: same groups and candidates, one thing changed at a time.
No setting was chosen because of them. Scripts: `scripts/diagnostics/mf_seed.py`
(MF start, rating matrix) and `scripts/diagnostics/rating_matrix_and_gain.py`
(gain, clipping).

### Random start of the matrix factorization

The MF starts from random factors (A3). Six fits that differ only in that
start, real ratings kept as in the main results. Fairness, mean and range over
the six fits ("main" is the fit used everywhere else):

| | AVG | LM | NPO | XPO | XPO - AVG (range) | main fit |
|---|---|---|---|---|---|---|
| RND m = 5 | 0.195 | 0.088 | 0.133 | 0.201 | +0.006 (-0.005 to +0.022) | -0.002 |
| RND m = 8 | 0.112 | 0.047 | 0.081 | 0.130 | +0.017 (+0.013 to +0.026) | +0.026 |
| SIM m = 5 | 0.336 | 0.212 | 0.265 | 0.334 | -0.002 (-0.010 to +0.003) | +0.003 |
| SIM m = 8 | 0.221 | 0.116 | 0.166 | 0.221 | +0.000 (-0.007 to +0.005) | +0.004 |

- A single fit moves a method's fairness by up to 0.03 (AVG RND m = 5: 0.175 to
  0.204) and XPO - AVG by up to 0.03. This is as large as the 95% CI over groups
  and is not covered by it. Differences of 0.02 from one fit are not reliable.
- The conclusions hold in every fit: XPO and AVG are level at m = 5, XPO has a
  small lead (about 0.02) at m = 8 in RND groups only, NPO is below AVG, LM last.

### Rating matrix: keep real ratings (A9) or use MF predictions everywhere

Same six fits, but the MF prediction is used for every user-movie pair, also
where a real rating exists (not clipped). Mean and range over the fits:

| | AVG | LM | NPO | XPO | XPO - AVG (range) |
|---|---|---|---|---|---|
| RND m = 5 | 0.258 | 0.143 | 0.204 | 0.281 | +0.023 (+0.009 to +0.041) |
| RND m = 8 | 0.172 | 0.100 | 0.138 | 0.203 | +0.031 (+0.021 to +0.038) |
| SIM m = 5 | 0.428 | 0.306 | 0.372 | 0.431 | +0.003 (-0.003 to +0.012) |
| SIM m = 8 | 0.294 | 0.198 | 0.257 | 0.318 | +0.023 (+0.014 to +0.033) |

- All levels are higher than with real ratings kept, and AVG comes close to the
  paper (0.258 / 0.428 vs 0.298 / 0.437). Kept real ratings are integers that
  dominate each member's top 20 and differ between members.
- XPO's lead over AVG is larger here (0.02 to 0.03 in three of four settings)
  but still far from the paper's 0.11 to 0.14, and XPO's level (0.281 / 0.431)
  is far below the paper's (0.406 / 0.579). NPO stays below AVG.
- Clipping makes no difference here (checked on the main fit: at most 0.007).
- The paper says MF is used "to fill in the missing ratings", so we keep the
  real ratings (A9). This check shows the choice matters for the size of XPO's
  lead, not for the ordering.

### nDCG gain

Same groups and lists, different gain (main fit, m = 5, fairness):

| Gain | AVG RND | NPO RND | XPO RND | XPO - AVG RND | AVG SIM | NPO SIM | XPO SIM | XPO - AVG SIM |
|---|---|---|---|---|---|---|---|---|
| 2^rel (as printed, our setting) | 0.204 | 0.142 | 0.202 | -0.002 ± 0.015 | 0.333 | 0.266 | 0.335 | +0.003 ± 0.018 |
| rel (linear) | 0.425 | 0.406 | 0.462 | +0.037 ± 0.015 | 0.567 | 0.547 | 0.603 | +0.036 ± 0.012 |
| 1 if in ground truth (binary) | 0.455 | 0.463 | 0.487 | +0.033 ± 0.013 | 0.575 | 0.582 | 0.601 | +0.025 ± 0.011 |

The printed gain is extremely top-heavy: a member's number 1 is worth twice
their number 2 and about a million times their number 20. With a less top-heavy
gain XPO is significantly fairer than AVG and NPO moves up to AVG, which is
closer to the paper's picture. So XPO does put more of each member's top 20 into
the list; it does not get the very first positions right more often than AVG.
We cannot tell which gain the paper really used (next section).

### Number of weight samples

See E5 below: S = 10,000 is enough.

## The paper's nDCG values do not fit its printed formula

The paper defines gain 2^rel with rel = N - p + 1 (up to 20), and we use it as
printed (A11). Under this gain nDCG@1 is about 2^(rel - 20): 1 only if the first
group item is the member's own number 1, 0.5 if it is their number 2, and so
on. nDCG@1 must therefore be far below P@1. In the paper's Table 1 they are
almost equal (AVG group utility: nDCG@1 0.694, P@1 0.702; same pattern in every
row). With five random users this is not possible under the printed formula.
Our values: nDCG@1 0.280 vs P@1 0.876.

## Issues found in the paper

- **Fairness P@1 column in Tables 1 and 2 is a copy of group-utility P@10.**
  Every row has identical values in both columns (AVG RND 0.490 / 0.490, XPO RND
  0.566 / 0.566, AVG SIM 0.633 / 0.633, ...). The fairness P@1 values are also
  implausibly high next to fairness P@5.
- **nDCG values are inconsistent with the printed DCG formula** (see above).
- **Ties in ranks are allowed but not specified.** The paper says "we assume that
  ties in ranks are possible" but not how tied ranks are assigned, nor which of
  two equally rated movies enters a member's top-N. Our results depend on this
  (see "Changes on 2026-11-15").
- **Ties in the Monte Carlo counts are not addressed.** When the XPO pool has
  exactly N items, every item has the same count and the order of the list is
  undefined. We break ties by mean rank (A13).
- **BORDA is far below AVG for similar users** (SIM nDCG@20 fairness 0.203 vs
  0.437). For like-minded users mean rank and mean rating should give similar
  lists. This suggests the paper's ranks are not exact ranks over the 200
  candidates (possibly the top-N' approximation), which would also affect NPO/XPO.
- Toy example: the stated tie point (3/7, 4/7) does not follow from the printed
  ranks; it should be (2/5, 3/5).
- Not reported: S, weight distribution, MF settings, runtime, significance tests.

## E2 / E3 group size (N = 20)

Source: `results/E2.csv` (m = 2..8) and `results/E3.csv` (m = 2..30). Groups are
keyed by (type, m, N, id), so settings shared by E1, E2 and E3 use the same groups
and give the same numbers.

Fairness, RND:

| m | 2 | 3 | 5 | 8 | 10 | 15 | 20 | 30 |
|---|---|---|---|---|---|---|---|---|
| AVG | 0.532 | 0.339 | 0.204 | 0.110 | 0.110 | 0.054 | 0.048 | 0.029 |
| LM | 0.314 | 0.187 | 0.093 | 0.043 | 0.037 | 0.016 | 0.010 | 0.006 |
| NPO | 0.414 | 0.248 | 0.142 | 0.082 | 0.080 | 0.041 | 0.035 | 0.020 |
| XPO | 0.487 | 0.336 | 0.202 | 0.135 | 0.103 | 0.047 | 0.040 | 0.022 |

Fairness, SIM:

| m | 2 | 3 | 5 | 8 | 10 | 15 | 20 | 30 |
|---|---|---|---|---|---|---|---|---|
| AVG | 0.623 | 0.464 | 0.333 | 0.216 | 0.195 | 0.139 | 0.112 | 0.086 |
| LM | 0.460 | 0.320 | 0.215 | 0.118 | 0.100 | 0.057 | 0.044 | 0.042 |
| NPO | 0.532 | 0.385 | 0.266 | 0.157 | 0.152 | 0.096 | 0.090 | 0.066 |
| XPO | 0.591 | 0.453 | 0.335 | 0.220 | 0.197 | 0.121 | 0.106 | 0.072 |

XPO minus AVG, paired over groups:

| m | 2 | 3 | 5 | 8 | 10 | 15 | 20 | 30 |
|---|---|---|---|---|---|---|---|---|
| RND | -0.044 ± 0.023 | -0.003 ± 0.023 | -0.002 ± 0.015 | +0.026 ± 0.015 | -0.007 ± 0.010 | -0.008 ± 0.005 | -0.008 ± 0.006 | -0.007 ± 0.004 |
| SIM | -0.031 ± 0.017 | -0.012 ± 0.018 | +0.003 ± 0.018 | +0.004 ± 0.017 | +0.002 ± 0.015 | -0.018 ± 0.015 | -0.006 ± 0.008 | -0.014 ± 0.009 |

Group utility: AVG is highest at every size for RND and SIM (RND m = 5: AVG
0.480, XPO 0.420, NPO 0.375, LM 0.327; m = 30: 0.404, 0.336, 0.335, 0.222).

Pool size (of 200 candidates) and XPO level x:

| m | 2 | 3 | 5 | 8 | 10 | 15 | 20 | 30 |
|---|---|---|---|---|---|---|---|---|
| NPO pool RND | 43 | 62 | 88 | 108 | 116 | 134 | 145 | 159 |
| XPO pool RND | 21 | 22 | 26 | 29 | 36 | 50 | 59 | 79 |
| XPO level x RND | 7.8 | 4.5 | 2.2 | 1.3 | 1.2 | 1.0 | 1.0 | 1.0 |
| NPO pool SIM | 38 | 51 | 71 | 91 | 97 | 109 | 118 | 130 |
| XPO pool SIM | 21 | 21 | 23 | 25 | 29 | 33 | 39 | 50 |
| XPO level x SIM | 9.3 | 6.0 | 3.2 | 1.9 | 1.7 | 1.2 | 1.1 | 1.1 |

Runtime per group: NPO 2 ms (m = 2) to 13 ms (m = 30), XPO 0.7 to 8.5 ms, AVG and LM below 0.1 ms.

### Findings
- Fairness falls quickly with group size for every method (as in the paper's Fig. 2/3), and SIM stays above RND.
- **XPO is never clearly fairer than AVG, except at m = 8 in RND groups**
  (+0.026 ± 0.015; +0.013 to +0.026 across six MF fits). At m = 2 AVG is
  significantly fairer (RND and SIM). From m = 15 on AVG is slightly but
  significantly fairer in RND groups, and at m = 15 and 30 in SIM groups.
- **XPO is fairer than NPO at every size**, clearly so up to m = 10. From m = 15 on the gap is below 0.01 in RND groups and 0.01 to 0.03 in SIM groups.
- NPO is below AVG at every group size. On P@20 and AP the three are close.
- AVG has the highest group utility at every group size.
- **Hypothesis "NPO pool approaches all items": partly confirmed.** The NPO pool
  grows from 22% to 79% of the candidates (RND; SIM 19% to 65%), not to 100%.
- **Hypothesis "XPO stays selective": not confirmed for large groups.** From
  m = 15 on the level is x = 1 in almost every RND group, so XPO cannot shrink
  its pool any further: the plain Pareto-optimal set alone already has 50 to 79
  items. XPO and NPO then give nearly the same fairness (0.022 vs 0.020 at m = 30).
- The tie case of A13 (XPO pool of exactly 20 items) is frequent for small
  groups: 42% of RND groups at m = 2, 9% at m = 5, 0% from m = 15 (SIM: 37%, 23%, 3%).

## E5 Monte Carlo sensitivity (RND, N = 20)

Mean fairness by number of weight samples S (`results/E5.csv`):

| | S = 1,000 | 5,000 | 10,000 | 50,000 |
|---|---|---|---|---|
| NPO, m = 5 | 0.1429 | 0.1403 | 0.1418 | 0.1407 |
| XPO, m = 5 | 0.2016 | 0.2011 | 0.2024 | 0.2010 |
| NPO, m = 20 | 0.0356 | 0.0340 | 0.0350 | 0.0349 |
| XPO, m = 20 | 0.0394 | 0.0400 | 0.0400 | 0.0397 |

Mean absolute change per group against S = 50,000 is at most 0.002 at S = 10,000
(at most 0.004 for smaller S; the change does not shrink steadily with S at m = 5,
and it is larger than with the old strict ranks, where it was 0.001). S = 10,000 is enough, also for m = 20: the sampling noise
is far smaller than the CI over groups (about 0.02) and the MF-start effect.

## Changes on 2026-11-15: back to the paper for A11, A5 and A4

A check of `ASSUMPTIONS.md` against the paper text showed three places where we
departed from it. All three were switched back and E1, E2, E3 and E5 rerun.

### A11, nDCG gain: 2^rel - 1 -> 2^rel (as printed)

Largest change in any group's fairness or group utility: 4e-6. No reported
number moved.

### A5, SIM groups: similarity to the seed user -> to the whole group

The paper builds SIM groups "by adding the most similar user to the group".
Each step now adds the user with the highest mean similarity to all members so
far. Seed users and candidates are the same as before, so the comparison is
paired. At m = 5 only 2.7 of 5 members are the same on average, and the mean
pairwise similarity is 0.218 instead of 0.167 (m = 30: 0.176 vs 0.095).

Fairness, SIM, current settings otherwise (`scripts/diagnostics/sim_groups.py`):

| m | 2 | 3 | 5 | 8 | 10 | 15 | 20 | 30 |
|---|---|---|---|---|---|---|---|---|
| AVG seed | 0.623 | 0.420 | 0.305 | 0.209 | 0.185 | 0.124 | 0.097 | 0.064 |
| AVG group (now) | 0.623 | 0.464 | 0.333 | 0.216 | 0.195 | 0.139 | 0.112 | 0.086 |
| XPO seed | 0.591 | 0.422 | 0.309 | 0.213 | 0.182 | 0.109 | 0.089 | 0.053 |
| XPO group (now) | 0.591 | 0.453 | 0.335 | 0.220 | 0.197 | 0.121 | 0.106 | 0.072 |

Fairness rises for every method by 0.01 to 0.04 (LM and NPO likewise). Small
next to the gap to the paper, and the ordering of the methods did not change:
XPO minus AVG at m = 5 is +0.004 ± 0.021 with seed-based groups and +0.003 ± 0.018 now.

### A4, ranks: ties broken by movie id -> tied ranks

The paper says "we assume that ties in ranks are possible". Until 2026-11-15
every member had strict ranks: two movies with the same rating were ordered by
movie id. Ties are not rare, because real ratings are integers and predictions
are clipped at 5 (A9): 3% (RND) to 6% (SIM) of a member's 200 candidate ratings
repeat another value, mostly at the top of the list. Now equally rated movies
share the average of the ranks they span. A member's ground-truth top 20 still
needs a strict order and keeps the movie-id order; AVG and LM work on ratings
and are not affected.

XPO fairness under three ways of handling ties (same groups, candidates and
ground truth; `scripts/diagnostics/tie_order.py`):

| m | 2 | 3 | 5 | 8 | 10 | 15 | 20 | 30 |
|---|---|---|---|---|---|---|---|---|
| RND strict, by movie id (old) | 0.497 | 0.357 | 0.224 | 0.144 | 0.109 | 0.047 | 0.039 | 0.022 |
| RND strict, random order | 0.486 | 0.351 | 0.214 | 0.135 | 0.110 | 0.046 | 0.039 | 0.022 |
| RND tied ranks (now) | 0.487 | 0.336 | 0.202 | 0.135 | 0.103 | 0.047 | 0.040 | 0.022 |
| SIM strict, by movie id (old) | 0.596 | 0.467 | 0.359 | 0.239 | 0.215 | 0.136 | 0.114 | 0.080 |
| SIM strict, random order | 0.587 | 0.464 | 0.342 | 0.227 | 0.199 | 0.123 | 0.104 | 0.075 |
| SIM tied ranks (now) | 0.591 | 0.453 | 0.335 | 0.220 | 0.197 | 0.121 | 0.106 | 0.072 |

XPO minus AVG, paired over groups:

| m | 2 | 3 | 5 | 8 | 10 | 15 | 20 | 30 |
|---|---|---|---|---|---|---|---|---|
| RND strict, by movie id (old) | -0.035 ± 0.022 | +0.018 ± 0.023 | +0.020 ± 0.018 | +0.034 ± 0.016 | -0.001 ± 0.010 | -0.008 ± 0.005 | -0.009 ± 0.006 | -0.007 ± 0.004 |
| RND strict, random order | -0.045 ± 0.022 | +0.012 ± 0.023 | +0.010 ± 0.017 | +0.025 ± 0.014 | +0.001 ± 0.012 | -0.008 ± 0.005 | -0.010 ± 0.006 | -0.007 ± 0.004 |
| RND tied ranks (now) | -0.044 ± 0.023 | -0.003 ± 0.023 | -0.002 ± 0.015 | +0.026 ± 0.015 | -0.007 ± 0.010 | -0.008 ± 0.005 | -0.008 ± 0.006 | -0.007 ± 0.004 |
| SIM strict, by movie id (old) | -0.026 ± 0.017 | +0.002 ± 0.020 | +0.026 ± 0.020 | +0.023 ± 0.017 | +0.020 ± 0.017 | -0.003 ± 0.017 | +0.002 ± 0.008 | -0.006 ± 0.009 |
| SIM strict, random order | -0.036 ± 0.018 | +0.000 ± 0.020 | +0.009 ± 0.019 | +0.010 ± 0.016 | +0.004 ± 0.014 | -0.015 ± 0.015 | -0.007 ± 0.009 | -0.011 ± 0.009 |
| SIM tied ranks (now) | -0.031 ± 0.017 | -0.012 ± 0.018 | +0.003 ± 0.018 | +0.004 ± 0.017 | +0.002 ± 0.015 | -0.018 ± 0.015 | -0.006 ± 0.008 | -0.014 ± 0.009 |

- **XPO loses about 0.02 fairness at m = 3 to 10 with tied ranks**, which was
  its whole lead over AVG at m = 5 (and at m = 5 to 10 in SIM groups).
- **Why:** with movie-id tie-breaking the same arbitrary order decided both the
  ranks XPO saw and where equally rated movies sit in a member's ground truth.
  XPO could "see" how the evaluation breaks ties; AVG, which only sees ratings,
  could not. Breaking ties in a random order instead (unrelated to the ground
  truth) removes about half of the advantage in RND groups and most of it in
  SIM groups. The rest comes from strict ranks as such.
- NPO barely changes (at most 0.01). Pools and the XPO level hardly move.
- Assigning both tied movies the better rank instead of the average gives the
  same dominance and nearly the same results (XPO m = 5: 0.204 vs 0.202 RND,
  0.338 vs 0.335 SIM).
- With the old tie-breaking the main result was "XPO is the fairest at m = 5,
  by 0.02". That lead was an artefact of the tie-breaking.
