# Replication notes

Where our numbers differ from the paper, what we checked, and what changed along
the way. Input for the "critical evaluation" part of the presentation and report.

**Since 2026-11-18 the reported results are averages over 20 MF fits** (A15)
and include the paper's other baselines (MUL, MAX, BORDA, MED; A19), Average
without Misery (AWM; A16, A17) and two rating-based metrics (A18). They are in
the first part below ("Results over 20 MF fits"). The sections after it are
the earlier single-fit analysis (fit 0, the presentation numbers), kept
because the sensitivity checks and the paper issues are still valid.

Settings in force since 2026-11-15 (see `ASSUMPTIONS.md`): nDCG gain 2^rel as
printed (A11), SIM groups grown by similarity to the whole group (A5), tied
ranks for equally rated movies (A4). 100 groups per setting, S = 10,000,
± = 95% CI half-width over groups.

# Results over 20 MF fits (2026-11-18)

Sources: `results/summary/*.csv` from `scripts/summarize.py`; per-row data in
`results/E1.csv`, `E2.csv`, `E3.csv`, `E5.csv` (column `mf_fit`). For each group
a method's value is averaged over the 20 fits, then over the 100 groups; the CI
is over the 100 per-group averages. In the difference tables "[a/b]" counts in
how many of the 20 fits the difference is significant on that fit alone, in
favour of the first / second method.

## Are 20 fits enough?

- Running mean over fits (`convergence.csv`): going from 15 to 20 fits moves no
  setting mean (any method, m, group type; nDCG@20, P@20, AP) by more than
  0.002; from 10 to 20 by at most 0.0035. A single fit is up to 0.016 away
  from the 20-fit mean.
- Spread between fits of a setting mean (`fairness_fit_sd`, nDCG@20, E3):
  median 0.005, max 0.012, so the standard error of a 20-fit mean is at most
  about 0.003, well below the CI over groups (0.003 to 0.03).
- Fit 0 reproduces the earlier single-fit results exactly (checked row by row).

## E1 (m = 5, N = 20), all methods

Fairness (95% CI) and group utility. Paper values in `results/summary/e1_vs_paper.csv`
and `figures/e1_vs_paper*.png`.

| nDCG@20 | Fair. RND | Fair. SIM | GU RND | GU SIM | paper fair. RND / SIM |
|---|---|---|---|---|---|
| AVG | 0.196 ± 0.023 | 0.331 ± 0.032 | 0.473 | 0.585 | 0.298 / 0.437 |
| LM | 0.092 ± 0.016 | 0.211 ± 0.031 | 0.324 | 0.466 | 0.197 / 0.403 |
| MUL | 0.183 ± 0.022 | 0.320 ± 0.033 | 0.460 | 0.577 | 0.290 / 0.438 |
| MAX | 0.260 ± 0.024 | 0.362 ± 0.026 | 0.540 | 0.613 | 0.208 / 0.329 |
| BORDA | 0.135 ± 0.019 | 0.271 ± 0.033 | 0.379 | 0.519 | 0.210 / 0.203 |
| MED | 0.149 ± 0.019 | 0.293 ± 0.032 | 0.438 | 0.567 | 0.211 / 0.154 |
| NPO | 0.134 ± 0.018 | 0.266 ± 0.032 | 0.365 | 0.506 | 0.311 / 0.472 |
| XPO | 0.203 ± 0.020 | 0.332 ± 0.031 | 0.421 | 0.554 | 0.406 / 0.579 |
| AWM (ours) | 0.184 ± 0.023 | 0.321 ± 0.033 | 0.457 | 0.576 | n/a |

| P@20 | Fair. RND | Fair. SIM | GU RND | GU SIM | paper fair. RND / SIM |
|---|---|---|---|---|---|
| AVG | 0.395 ± 0.019 | 0.512 ± 0.018 | 0.553 | 0.636 | 0.267 / 0.367 |
| LM | 0.309 ± 0.018 | 0.419 ± 0.019 | 0.454 | 0.555 | 0.165 / 0.327 |
| MUL | 0.393 ± 0.019 | 0.509 ± 0.018 | 0.548 | 0.633 | 0.260 / 0.366 |
| MAX | 0.316 ± 0.018 | 0.405 ± 0.018 | 0.475 | 0.557 | 0.223 / 0.332 |
| BORDA | 0.385 ± 0.018 | 0.496 ± 0.019 | 0.531 | 0.619 | 0.217 / 0.235 |
| MED | 0.397 ± 0.020 | 0.511 ± 0.019 | 0.560 | 0.645 | 0.237 / 0.185 |
| NPO | 0.392 ± 0.018 | 0.504 ± 0.019 | 0.543 | 0.629 | 0.281 / 0.377 |
| XPO | 0.414 ± 0.016 | 0.516 ± 0.015 | 0.537 | 0.622 | 0.376 / 0.508 |
| AWM (ours) | 0.389 ± 0.019 | 0.505 ± 0.018 | 0.543 | 0.629 | n/a |

AP fairness, RND / SIM: AVG 0.252 / 0.388, LM 0.185 / 0.290, MUL 0.252 / 0.387,
MAX 0.141 / 0.218, BORDA 0.259 / 0.390, MED 0.253 / 0.376, NPO 0.258 / 0.390,
XPO 0.279 / 0.407, AWM 0.249 / 0.382 (paper: AVG 0.126 / 0.239, XPO 0.205 / 0.377).

Paired fairness differences at m = 5 (20 fits):

| | nDCG@20 RND | nDCG@20 SIM | P@20 RND | P@20 SIM | AP RND | AP SIM |
|---|---|---|---|---|---|---|
| XPO - AVG | +0.006 ± 0.011 [1/0] | +0.001 ± 0.010 [0/0] | **+0.018 ± 0.008** [18/0] | +0.004 ± 0.006 [0/0] | **+0.027 ± 0.007** [20/0] | **+0.019 ± 0.006** [20/0] |
| XPO - NPO | **+0.068 ± 0.008** [20/0] | **+0.066 ± 0.007** [20/0] | **+0.022 ± 0.007** [19/0] | **+0.012 ± 0.007** [11/0] | **+0.021 ± 0.005** [20/0] | **+0.017 ± 0.005** [20/0] |
| NPO - AVG | **-0.062 ± 0.011** [0/20] | **-0.065 ± 0.011** [0/20] | -0.003 ± 0.006 [0/0] | **-0.007 ± 0.004** [0/7] | +0.006 ± 0.006 [5/0] | +0.003 ± 0.007 [0/0] |
| AWM - AVG | **-0.012 ± 0.007** [0/18] | **-0.011 ± 0.006** [0/18] | **-0.006 ± 0.004** [0/9] | **-0.007 ± 0.004** [0/16] | **-0.003 ± 0.003** [0/3] | **-0.006 ± 0.004** [0/16] |
| BORDA - AVG | **-0.061 ± 0.012** [0/20] | **-0.060 ± 0.011** [0/20] | **-0.011 ± 0.006** [0/10] | **-0.016 ± 0.006** [0/19] | +0.008 ± 0.006 [7/0] | +0.002 ± 0.007 [0/0] |
| MAX - AVG | **+0.063 ± 0.026** [20/0] | **+0.031 ± 0.025** [13/0] | **-0.079 ± 0.012** [0/20] | **-0.107 ± 0.012** [0/20] | **-0.111 ± 0.013** [0/20] | **-0.169 ± 0.014** [0/20] |

Bold: 95% CI excludes 0.

### Findings at m = 5

1. **Under nDCG@20 the picture of the single-fit analysis holds:** XPO and AVG
   are level (+0.006 / +0.001, never significant in more than 1 of 20 fits);
   XPO is clearly fairer than NPO; NPO is clearly below AVG; LM last among
   the paper's main methods. The paper's +0.11 / +0.14 is not reproduced.
2. **Under precision the paper's main claim partly returns.** With P@20 and AP,
   XPO is the fairest of all nine methods in RND groups: +0.018 (P@20) and
   +0.027 (AP) over AVG, significant in 18 and 20 of 20 fits; in SIM groups
   significant for AP (+0.019), not for P@20. The margin is a fifth to a
   quarter of the paper's (P@20 fairness RND: paper +0.109, ours +0.018).
   Under P@20 the ordering is XPO > MED ≈ AVG ≈ MUL ≈ NPO > AWM > BORDA > MAX
   ≈ LM; the paper's is XPO > NPO > AVG > MUL > MED > MAX > BORDA > LM. Top and
   bottom agree, the middle is compressed.
3. **NPO ≈ AVG under precision** (P@20 -0.003 RND, AP +0.006 RND, both n.s.),
   while it is 0.06 below AVG under nDCG@20. NPO puts the right items in the
   list but in an order that misses the members' very first places.
4. **MAX is the fairest method under nDCG@20 and among the worst under P@20 and
   AP.** Checked that this is not a tie artefact: with ties broken in random
   order (list and ground truth), MAX still leads AVG at m = 5 (0.25 vs 0.19).
   Reason: MAX puts almost every member's personal number 1 into the list (93%
   of members at m = 5, AVG 74%), and under the gain 2^rel a member's number 1
   is worth about two thirds of the ideal DCG. MAX's other items are often
   outside the members' top 20, hence the low P@20 and AP. The paper has MAX
   clearly below AVG on nDCG@20 (0.208 vs 0.298) and near 0 on nDCG@1. This
   is a further sign that the paper's nDCG was not the printed one, and a
   strong illustration that nDCG@20 with gain 2^rel mostly measures "is my
   favourite in the list".
5. **BORDA (mean rank) is clearly below AVG under nDCG@20 also with exact
   tied ranks** (-0.061 RND, -0.060 SIM), and level or slightly below under
   precision. So the paper's low BORDA in RND (0.210 vs 0.298) is consistent
   with exact ranks; only its SIM gap (0.203 vs 0.437) remains much larger than
   ours. The earlier note that low BORDA "suggests the paper's ranks are not
   exact" is weakened: ranks lose the rating levels that AVG uses (a member
   who rates everything 3 to 4 counts as much as one who rates 1 to 5).
6. **MUL ≈ AVG** (as in the paper), slightly below on nDCG@20 (-0.013).
7. **Our precision levels are higher and our nDCG levels lower than the
   paper's**, for every method (e.g. AVG fairness P@20 0.395 vs 0.267, nDCG@20
   0.196 vs 0.298). We cannot explain both with one cause.

## Group size (E3, 20 fits)

Fairness, mean over groups and fits (`settings.csv`):

| nDCG@20 RND | 2 | 3 | 5 | 8 | 10 | 15 | 20 | 30 |
|---|---|---|---|---|---|---|---|---|
| AVG | 0.535 | 0.346 | 0.196 | 0.118 | 0.105 | 0.056 | 0.048 | 0.027 |
| LM | 0.317 | 0.182 | 0.092 | 0.049 | 0.040 | 0.015 | 0.010 | 0.006 |
| MAX | 0.555 | 0.391 | 0.260 | 0.154 | 0.135 | 0.064 | 0.028 | 0.011 |
| BORDA | 0.415 | 0.254 | 0.135 | 0.087 | 0.080 | 0.044 | 0.035 | 0.020 |
| AWM | 0.530 | 0.335 | 0.184 | 0.104 | 0.094 | 0.041 | 0.032 | 0.015 |
| NPO | 0.409 | 0.250 | 0.134 | 0.085 | 0.077 | 0.042 | 0.033 | 0.020 |
| XPO | 0.491 | 0.337 | 0.203 | 0.131 | 0.104 | 0.049 | 0.039 | 0.020 |

| P@20 RND | 2 | 3 | 5 | 8 | 10 | 15 | 20 | 30 |
|---|---|---|---|---|---|---|---|---|
| AVG | 0.611 | 0.507 | 0.395 | 0.342 | 0.310 | 0.274 | 0.238 | 0.215 |
| LM | 0.475 | 0.394 | 0.309 | 0.254 | 0.235 | 0.189 | 0.166 | 0.146 |
| MAX | 0.483 | 0.400 | 0.316 | 0.253 | 0.230 | 0.185 | 0.161 | 0.132 |
| AWM | 0.609 | 0.503 | 0.389 | 0.330 | 0.296 | 0.252 | 0.223 | 0.188 |
| NPO | 0.608 | 0.502 | 0.392 | 0.334 | 0.306 | 0.269 | 0.233 | 0.212 |
| XPO | 0.638 | 0.525 | 0.414 | 0.350 | 0.315 | 0.274 | 0.240 | 0.213 |

XPO - AVG, fairness, paired (95% CI, [fits significant for XPO / for AVG]):

| | 2 | 3 | 5 | 8 | 10 | 15 | 20 | 30 |
|---|---|---|---|---|---|---|---|---|
| nDCG@20 RND | **-0.044** [0/20] | -0.009 | +0.006 | **+0.013** [9/0] | -0.001 | **-0.008** [0/11] | **-0.009** [0/19] | **-0.007** [0/20] |
| nDCG@20 SIM | **-0.035** [0/18] | -0.008 | +0.001 | +0.005 | +0.003 | -0.007 | -0.006 | **-0.014** [0/19] |
| P@20 RND | **+0.028** [20/0] | **+0.019** [16/0] | **+0.018** [18/0] | **+0.007** [7/0] | +0.005 | +0.000 | +0.002 | -0.002 |
| P@20 SIM | **+0.016** [17/0] | **+0.006** [2/0] | +0.004 | -0.005 | -0.001 | **-0.006** [0/4] | **-0.012** [0/14] | **-0.011** [0/16] |
| AP RND | **+0.066** [20/0] | **+0.052** [20/0] | **+0.027** [20/0] | **+0.013** [14/0] | **+0.007** [9/0] | **-0.007** [0/13] | -0.001 | **-0.007** [0/18] |
| AP SIM | **+0.055** [20/0] | **+0.034** [20/0] | **+0.019** [20/0] | +0.005 | +0.002 | -0.002 | **-0.008** [0/8] | **-0.016** [0/20] |

### Findings over group size

- **The XPO lead at 8 random members under nDCG@20 is not a finding** (revised
  2026-11-20 after the presentation feedback). It halves with 20 fits
  (+0.013 ± 0.009, single fit 0: +0.026) and is significant in only 9 of 20
  fits on its own. It is one cell out of 16 (8 sizes x 2 group types), and
  with 16 tests at the 5% level about one "significant" cell is expected by
  chance. Its size is about what a single MF fit moves a setting mean (up to
  0.016, see above). The presentation's "XPO's only clear lead" was the
  largest of the fits. In the report: no lead at m = 8, not "a small lead".
- **Under precision and AP, XPO is fairer than AVG for small groups** (2 to 8
  members in RND, 2 to 3 (P@20) or 2 to 5 (AP) in SIM), and the lead shrinks
  steadily with m. From 15 members on AVG is level or ahead under every top-N
  metric (nDCG, P@20, AP).
  At 2 members the metrics disagree most: under nDCG@20 AVG is clearly fairer
  (-0.044), under P@20 and AP XPO is (+0.028, +0.066).
- **The pool explanation still holds:** the XPO level x drops from about 8
  (RND) / 9 (SIM) at m = 2 to 1 from m = 15 on (`figures/pool_size_vs_group_size.png`).
- **NPO** is below AVG under nDCG@20 at every size (-0.126 at m = 2 to -0.007
  at m = 30), about level under P@20 and above AVG under AP at m = 2 to 3.
- **AWM** is below AVG at every size under every top-N metric, increasingly so
  with m (nDCG@20 -0.012 at m = 5, P@20 -0.028 at m = 30).
- **MAX** leads under nDCG@20 from m = 3 to 10 and falls below AVG from m = 20;
  it is far below AVG under P@20 and AP at every size.

## Rating-based metrics (A18)

No-misery share (share of the 20 listed items the worst-off member rates at
least 3), fairness, RND:

| | 2 | 5 | 10 | 15 | 30 |
|---|---|---|---|---|---|
| AVG | 0.982 | 0.954 | 0.851 | 0.784 | 0.755 |
| LM | 0.988 | 0.990 | 0.942 | 0.911 | 0.889 |
| AWM | 0.988 | 0.989 | 0.937 | 0.903 | 0.883 |
| NPO | 0.986 | 0.962 | 0.854 | 0.785 | 0.764 |
| XPO | 0.972 | 0.930 | 0.839 | 0.779 | 0.761 |
| MAX | 0.929 | 0.822 | 0.687 | 0.608 | 0.551 |

- With few members almost no list contains disliked movies: at m = 5 the
  worst-off member dislikes 1 of 20 items under AVG (0.954). From 10 members
  on, AVG gives the worst-off member 3 to 5 disliked movies, AWM and LM about 1 to 2.
- **AWM and LM, last or near last under the paper's metrics, are best here**
  (AWM - AVG: +0.035 at m = 5 to +0.128 at m = 30, significant in all 20 fits).
  AWM avoids exactly these items by construction, so this is the trade-off,
  not a neutral win.
- **XPO is below AVG on this metric** for m = 2 to 15 (RND -0.024 at m = 5,
  significant in 20 of 20 fits): its lead under precision comes with slightly
  more disliked items for the worst-off member. XPO's Pareto pool is built
  from ranks only, so a movie one member hates can be Pareto-optimal if
  another member loves it.
- Mean rating of the list for the worst-off member tells the same story with
  smaller numbers (m = 5 RND: LM 3.80, AWM 3.76, AVG 3.75, XPO 3.73, MAX 3.55).
- Conclusion for the report: which method is "fairest" depends on what
  fairness means. "Everyone gets some of their favourites" (the paper's
  metrics) favours XPO (precision) or MAX/AVG (nDCG@20); "nobody gets movies
  they dislike" favours LM and AWM.

## E5 over 20 fits

Mean fairness (nDCG@20) hardly depends on S: NPO m = 5 0.1355 / 0.1344 /
0.1345 / 0.1340 for S = 1k / 5k / 10k / 50k, XPO 0.2029 / 0.2029 / 0.2027 /
0.2026; m = 20 within 0.0003. Mean absolute change of a group's fairness at
S = 10,000 against 50,000: at most 0.002. But **single groups can move a lot**:
the largest change at S = 10,000 is 0.23. When two items get almost the same
count, S decides which comes first, and under the top-heavy nDCG@20 that can
swing one member's score. (Correction to the presentation's Q&A notes, which
said a group's fairness changes "by at most 0.002": that is the mean change.)

## How SIM groups are built and how similar they are (2026-11-20)

Requested in the presentation feedback: explain in the report what makes a
SIM group similar. Numbers from `scripts/diagnostics/group_similarity.py`
(`results/diagnostics/group_similarity.csv`): the same 100 groups per setting
as in the experiments, fit 0 for the ground truth.

**Construction** (A5, A12, `src/gfair/groups.py`):

1. Every user is a vector over all 3,706 movies: their observed rating minus
   their own mean rating, 0 for unrated movies. Centering removes the
   difference between generous and strict raters, so two users are similar
   when they like and dislike the *same* movies relative to their own scale.
   Only observed ratings are used, never MF predictions.
2. Similarity of two users = cosine of these vectors (mean-centered cosine,
   the paper's measure; it is the "adjusted"/centered cosine of user-based
   neighbourhood CF, Aggarwal 2016, Ch. 2). We take the cosine over the full
   vectors, not only over co-rated movies (A12), because with few co-rated
   movies the co-rated version gives +1 or -1 by chance.
3. A random seed user starts the group. Then the user with the highest mean
   similarity to all current members is added, until the group has m members
   (greedy, A5).

**How similar the result is** (mean over groups):

| | m = 2 | 5 | 8 | 15 | 30 |
|---|---|---|---|---|---|
| Mean pairwise similarity, SIM | 0.239 | 0.218 | 0.210 | 0.195 | 0.176 |
| Mean pairwise similarity, RND | 0.025 | 0.021 | 0.020 | 0.020 | 0.020 |
| Lowest pair in the group, SIM | 0.239 | 0.117 | 0.075 | 0.045 | -0.009 |
| Co-rated movies per pair (median), SIM | 55 | 76 | 109 | 134 | 135 |
| Co-rated movies per pair (median), RND | 21 | 13 | 12 | 12 | 10 |
| Ground-truth top 20 shared by a pair, SIM | 47% | 46% | 44% | 46% | 45% |
| Ground-truth top 20 shared by a pair, RND | 38% | 36% | 36% | 36% | 36% |
| Ratings per member, SIM | 152 | 189 | 249 | 316 | 344 |
| Ratings per member, RND | 155 | 164 | 162 | 162 | 159 |
| Level-1 Pareto share of the 200 candidates, SIM | 1.4% | 4.7% | 8.4% | 15.5% | 24.4% |
| Level-1 Pareto share of the 200 candidates, RND | 1.5% | 8.0% | 12.7% | 24.9% | 39.3% |

Reference: over 2,000 random users, the mean similarity of a pair is 0.021
and the 99th percentile 0.145. So an average SIM pair is more similar than
99% of random pairs, and the similarity drops slowly as the group grows
(at m = 30 the least similar pair is no longer similar at all).

What this means for the results:

- Similar members agree more on their top 20 (46% vs 36% shared), so one list
  can serve all of them better: fairness and group utility are higher for SIM
  at every size, as in the paper.
- Fewer items are Pareto optimal in SIM groups (4.7% vs 8.0% at m = 5): the
  members' rankings conflict less. Pools are smaller and XPO's level x is
  higher (see E3).
- Even random pairs share 36% of their top 20: the 200 candidates are random,
  and well-liked movies are in most members' top 20. This is why RND fairness
  is not near 0 for small groups.
- **Side effect:** the full-vector cosine favours users with many ratings
  (more non-zero entries to overlap), so SIM members rate on average 189
  movies at m = 5 and 344 at m = 30, against about 160 for RND (MovieLens
  median: 96). Their MF predictions rest on more data. The paper does not
  report this; we note it as a limitation, not as a reason to change A12.

Draft paragraph for the report (shorten as needed):

> *Similar groups.* Following the paper, we measure user similarity with the
> mean-centered cosine: each user's observed ratings minus their mean rating,
> with unrated movies set to 0, compared by cosine (Aggarwal, 2016, Ch. 2).
> Centering makes two users similar when they like the same movies relative to
> their own rating scale, not when both rate generously. A SIM group starts
> from a random user and grows greedily: at each step the user with the
> highest mean similarity to all current members joins. The resulting groups
> are clearly more homogeneous than random ones: at m = 5 the mean pairwise
> similarity is 0.22 against 0.02 for random groups (an average SIM pair is
> more similar than 99% of random pairs), and two members share 46% instead of
> 36% of their ground-truth top 20. The similarity declines slowly with group
> size (0.18 at m = 30). Two choices are ours: the cosine runs over all movies
> rather than co-rated ones only, which avoids spurious similarities of ±1
> from one or two shared movies but favours users with many ratings; and the
> similarity to a group is the mean over its members, which the paper leaves
> open.

# Earlier single-fit analysis (fit 0)

## E1 (m = 5, N = 20)

Source: `results/E1.csv` as of 2026-11-15 (fit 0 only).

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
- In all 24 runs (6 fits x RND/SIM x m = 5/8) XPO is fairer than NPO, NPO is
  below AVG and LM is last.
- XPO vs AVG: level in 11 of 12 runs at m = 5; the exception is one fit at RND
  m = 5 with XPO ahead by +0.022 ± 0.019. At m = 8 RND XPO is ahead in all six
  fits (+0.013 to +0.026), significantly in four. In SIM groups XPO is never
  significantly ahead. No fit comes near the paper's +0.11.
- Only m = 5 and 8 were checked on six fits; the group-size results (E2, E3)
  rest on the main fit alone.

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
their number 2 and about half a million times (2^19) their number 20. With a less top-heavy
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
  *Update 2026-11-18:* with BORDA implemented, our BORDA is also clearly below
  AVG (-0.06 in RND and SIM), so low BORDA as such is consistent with exact
  ranks; only the size of the paper's SIM gap (0.23) stays unexplained.
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
  (+0.026 ± 0.015; +0.013 to +0.026 across six MF fits). *Superseded: over 20
  fits this lead is +0.013 and not reliable, see "Findings over group size"
  above.* At m = 2 AVG is
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

## AWM threshold and fill rule (diagnostic, 2026-11-18)

Average without misery (A16, A17) under thresholds 2 to 4 and two ways to fill
the list when fewer than 20 items are misery-free: "fewest" (our rule: items
with the fewest unhappy members first, then by mean) and "mean" (misery-free
items by mean, then the rest by mean, i.e. plain AVG order). Mean over 100
groups and MF fits 0 to 4, N = 20 (`scripts/diagnostics/awm_threshold.py`).

Fairness, nDCG@20:

| | RND m = 2 | 5 | 10 | 30 | SIM m = 2 | 5 | 10 | 30 |
|---|---|---|---|---|---|---|---|---|
| AVG | 0.535 | 0.202 | 0.107 | 0.027 | 0.624 | 0.332 | 0.195 | 0.090 |
| AWM 2 | 0.536 | 0.202 | 0.105 | 0.025 | 0.624 | 0.332 | 0.194 | 0.084 |
| AWM 2.5 | 0.535 | 0.200 | 0.103 | 0.018 | 0.623 | 0.329 | 0.186 | 0.070 |
| **AWM 3 (ours)** | 0.530 | 0.188 | 0.095 | 0.016 | 0.618 | 0.321 | 0.183 | 0.074 |
| AWM 3.5 | 0.475 | 0.148 | 0.071 | 0.017 | 0.601 | 0.283 | 0.142 | 0.070 |
| AWM 4 | 0.493 | 0.179 | 0.101 | 0.027 | 0.601 | 0.307 | 0.192 | 0.098 |
| LM | 0.314 | 0.090 | 0.042 | 0.005 | 0.460 | 0.212 | 0.099 | 0.040 |

Mean number of misery-free items among the 200 candidates (RND; SIM similar):

| threshold | m = 2 | 5 | 10 | 30 |
|---|---|---|---|---|
| 2 | 184 | 173 | 154 | 131 |
| 2.5 | 158 | 134 | 104 | 71 |
| 3 | 112 | 79 | 49 | 23 |
| 3.5 | 51 | 23 | 9 | 1.5 |
| 4 | 12 | 2.1 | 0.5 | 0.0 |

- **AWM is never fairer than AVG** by more than 0.001, at any threshold,
  group size or group type, for nDCG@20 and for P@20 (the +0.001 cases are at
  thresholds 2 and 2.5, where AWM barely removes anything). The stricter the threshold, the lower its
  fairness, down to 3.5. At 4 almost no item is misery-free, the fill rule
  decides the list and AWM drifts back towards AVG (with the "mean" rule it
  becomes AVG).
- At threshold 3 the two fill rules differ by at most 0.005; at 30 members
  there are still about 23 misery-free items, so the fill rule rarely acts.
- Why AWM loses: every metric of the paper compares the list with the member's
  top 20. An item outside it scores 0 whether the member rates it 4.5 or 1, so
  removing disliked items earns nothing, while removing an item that is in
  another member's top 20 costs a hit. The same explains why LM is last. This
  led to the rating-based metrics (A18), which do see disliked items.
- Threshold 3 kept: it is the middle of the scale and was fixed before this
  check; the check shows the conclusion (AWM <= AVG) does not depend on it.
