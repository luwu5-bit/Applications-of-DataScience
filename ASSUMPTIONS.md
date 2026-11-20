# Assumptions

Every choice the code makes that goes beyond the paper (Sacharidis, 2019), with
what the paper says about it and our reason. Rule: never change one silently. If
one changes, update this file and `configs/default.yaml` in the same commit.

The **Status** column says how each choice relates to the paper text
(`docs/paper.md`, checked 2026-11-15):

- **From paper**: the paper states it; nothing was assumed.
- **Supported**: the paper does not state it outright, but its text points to our choice.
- **Open**: the paper says nothing; the choice is ours.
- **Departs**: our choice differs from what the paper says or most likely means.

| # | Topic | Our choice | Paper says | Status | Reason | Config key |
|---|---|---|---|---|---|---|
| A1 | Weight distribution | Uniform on the simplex, `rng.dirichlet(np.ones(m))` | Only "a large number of random weight vectors". But the 2-member example puts the tie at w = (3/7, 4/7) and gives i2 a probability of 4/7 "if all aggregation strategies are equally probable". That is what uniform weights on the simplex give (w1 uniform on [0, 1], P(w1 > 3/7) = 4/7); uniformly random directions would give 0.59 | Supported | Matches the paper's own example and encodes "no member is preferred a priori". (The example's tie point is itself wrong: with the printed ranks it is (2/5, 3/5), so P(i2) = 0.6. Our tests use the correct value) | n/a |
| A2 | Monte Carlo samples S | 10,000 | Nothing ("a large number") | Open | Checked for convergence in E5 (S in 1k, 5k, 10k, 50k): enough, also for m = 20 | `monte_carlo.n_samples` |
| A3 | MF model | Biased MF `mu + b_u + b_i + p_u . q_i`, own numpy implementation trained with alternating least squares (ALS), 50 factors, 20 sweeps, reg 0.06 scaled by rating count | Only "a simple matrix factorization technique" | Open | Own code avoids an extra dependency; ALS has no learning rate to tune and is fast in numpy. Hyperparameters picked on a 10% hold-out (see below). The model is trained several times with different random starts, see A15 | `mf.*` |
| A4 | Ranks | Exact over all 200 candidates, rank 1 = best. Movies a member rates equally share the **average** of the ranks they span (two movies tied for places 2 and 3 both get 2.5). Only the ground-truth top-N list (A8), which needs a strict order, orders equal ratings by item id | Exact ranks are the main definition; the top-N' approximation is only for when "this is impractical". Lower rank = better follows from the dominance definition. On ties: "we assume that ties in ranks are possible" | From paper (exact ranks, ties possible); Open (how tied ranks are assigned) | 200 items is small, so exact ranks are practical. The average rank is the usual convention when ranks are summed; giving both movies the better rank yields the same dominance and nearly the same results. Ties are common because of A9. Until 2026-11-15 ties were broken by item id (strict ranks). That gave XPO about 0.02 more fairness at m = 3 to 10, partly because the same id order also decides the ground truth (`docs/replication_notes.md`) | `n_candidates` |
| A5 | SIM groups | Random seed user, then repeatedly add the user with the highest **mean** mean-centered cosine similarity **to all members so far**; ties go to the lower user index | "starting from a randomly selected user, the group is build incrementally by adding the most similar (in terms of mean-centered cosine similarity) user to the group" | Supported (similarity to the group); Open (mean over members) | The paper does not say how similarity to a group of several users is measured; the mean over members treats all members alike. Until 2026-11-15 we used similarity to the seed user only, the weaker reading of the sentence. Effect of the switch: tighter groups, SIM fairness 0.01 to 0.04 higher, same ordering of methods (`docs/replication_notes.md`) | n/a |
| A6 | RND groups | Users sampled uniformly without replacement | "sampling uniformly at random from MovieLens" | From paper | "Without replacement" is implicit: a group cannot contain the same user twice | n/a |
| A7 | Seeds | One global seed; groups, candidates and weights derive from it | Nothing | Open | Reproducibility | `seed` |
| A8 | Ground truth | Each member's top-N of the 200 candidates by predicted rating | "we select 200 items at random, and we set the ground truth of each member to her top-N items among them recommended by the system" | From paper | Not an assumption; listed for completeness | n/a |
| A9 | Rating matrix used for ranking | Observed ratings are kept; MF predictions are used only for the missing user-item pairs and are clipped to [1, 5] | MF is used "to fill in the missing ratings in the dataset". Nothing on clipping | Supported (keep real ratings); Open (clipping) | Clipping makes every filled-in value a valid rating, so no prediction outranks a real 5 (also keeps out-of-range values out of AVG and LM). Consequence: more ties (integer observed ratings, predictions capped at 1 or 5), broken by item id (A4) | `mf.clip` |
| A10 | Items | Only the 3,706 movies with at least one rating (the paper counts 3,952 movie ids) | Nothing | Open | A movie without ratings has no learned factors, its prediction would be the same for every user up to the user bias | n/a |
| A11 | nDCG gain | `2^rel` with rel = N - p + 1; nDCG reported at k = 1, 5, 10, 20 | Relevance N - p + 1 ("Borda semantics"), gain `2^rel` and the cutoffs 1, 5, 10, 20 (Table 1) | From paper | Not an assumption any more. Caveat: under `2^rel` a movie outside the member's ground truth still earns 2^0 = 1. Effect: about 1e-5 at N = 20, but at N = 5 (E4) a completely wrong list would score about 0.06. From 2026-11-14 to 2026-11-15 we used the standard `2^rel - 1`; the numbers at N = 20 are the same to 3 decimals. Note: the paper's own nDCG values do not fit its formula, see `docs/replication_notes.md` | `metrics.ndcg_ks` |
| A12 | SIM similarity | Cosine over the full mean-centered rating vectors (unrated = 0), not only over co-rated movies | Only "mean-centered cosine similarity" | Open | With co-rated-only, two users who share one or two movies get similarity +1 or -1 and groups fill up with noise. Side effect: the full-vector cosine favours users with many ratings (SIM members rate 189 movies on average at m = 5, 344 at m = 30, RND about 160; `docs/replication_notes.md`) | n/a |
| A13 | Equal Monte Carlo counts | Ties ordered by lower mean rank over members, then by item id | Nothing | Open | Ties are certain when the pool has exactly N items (all counts = S). Mean rank is the equal-weights strategy, the centre of the weight simplex | n/a |
| A14 | Group seeds | One generator per group, keyed by (seed, group type, m, N, group id) | Nothing | Open | A group does not depend on the order in which settings are run; all methods see the same group and candidates. The same groups, candidates and weight samples are used in every MF fit (A15) | `seed` |
| A15 | Number of MF fits | Every experiment is run on **20 MF fits** that differ only in the random start of the factors. For each group a method's value is averaged over the 20 fits; the reported number is the mean over the 100 groups of these averages, the 95% CI is computed over the 100 per-group averages. The spread between fits is reported separately (`fit_sd`). Fit 0 is the fit behind `predictions.npy`; fit k uses the stream `SeedSequence(seed, spawn_key=(2 + k,))` | Nothing; one MF model is implied | Open | A single fit's random start alone moves a method's fairness by up to 0.03, as much as the CI over groups, and the CI does not include it. Averaging over fits removes most of that noise. 20 because the running mean over fits is stable to about 0.002 by then (`results/summary/convergence.csv`). Fits 1 to 19 are not saved, each is retrained from its seed (about 10 s) | `mf.n_fits` |
| A16 | AWM threshold | Average without misery (extension, not in the paper): a member rating **below 3** counts as misery; misery-free items are ranked by mean rating. A rating of exactly 3 is not misery | Not in the paper (AWM is from Masthoff's group strategies) | Open | 3 is the middle of the 1 to 5 scale, so misery means 1 or 2 stars or a prediction below 3. Sensitivity to thresholds 2 to 4 in `docs/replication_notes.md` | `awm.threshold` |
| A17 | AWM when too few items are misery-free | Items that the fewest members rate below the threshold come first, then by mean rating, ties by item id. With at least N misery-free items this is exactly plain AWM | Not in the paper | Open | Plain AWM does not say what to do when fewer than N items qualify, which happens often in large groups. This rule keeps the idea (avoid unhappy members as far as possible) instead of falling back to plain AVG. The alternative (fill by mean only) is compared in `scripts/diagnostics/awm_threshold.py` | n/a |
| A18 | Rating-based metrics (extension) | Two extra member utilities, both "higher is better": **no-misery share** = share of the 20 listed items the member rates at least 3; **mean rating** = the member's mean rating of the listed items. Ratings are the filled matrix (A9), as for the ground truth. Fairness = min over members, group utility = mean, as for the paper's metrics | Not in the paper; all its metrics compare the list with the member's top N | Open | The paper's metrics give the same 0 to an item the member ranks 21st and to one they rate 1 star, so they cannot see whether a list contains movies a member dislikes, which is what LM and AWM try to avoid. Threshold 3 as for AWM (A16). AWM avoids exactly these items by construction, so its no-misery score is high by design; the metric shows the trade-off, it is not a neutral test of AWM | `metrics.misery_threshold` |
| A19 | Further baselines MUL, MAX, BORDA, MED | MUL: product of member ratings (computed as sum of logs). MAX: highest member rating. BORDA: mean rank over members. MED: median rank. Ranks are the tied average ranks of A4; ties in the score go to the lower item id, as for AVG and LM | "AVG, LM, MAX, and MUL implement the additive, least-misery, maximum-pleasure, and multiplicative score aggregation strategies"; "BORDA and MED ... assign to an item its average or median rank" | From paper (definitions); Open (ranks over what, tie order) | Gives eight methods to compare with the paper's tables instead of four. The paper's BORDA is far below AVG for similar users (0.203 vs 0.437); with our exact ranks BORDA is also below AVG, by 0.06 (`docs/replication_notes.md`). None of them draws random numbers, so adding them changes no other result | `methods` |
| A20 | nDCG with linear gain, reported next to the printed gain | nDCG@20 also with gain = rel (rel = N - p + 1, 0 outside the ground truth), same discount and normalization; metric `ndcg_lin@20` | Gain `2^rel` (as printed, kept as A11) | Extension | The printed gain makes a member's number 1 worth 2^19 times their number 20, so nDCG@20 mostly measures whether each member's favourite is near the top. The paper's own nDCG values do not fit the printed gain (`docs/replication_notes.md`), so we report both instead of picking one; the printed-gain results stay unchanged | `metrics.ndcg_linear_ks` |

## MF sanity check (A3)

10% random hold-out, seed 42, 20 ALS sweeps. The regularization strength was chosen
on this hold-out, so the test RMSE of the chosen setting is slightly optimistic.
This selection only looks at rating prediction error, never at the paper's
fairness numbers.

| factors | reg | train RMSE | test RMSE |
|---|---|---|---|
| 50 | 0.02 | 0.532 | 0.936 |
| 50 | 0.04 | 0.597 | 0.871 |
| **50** | **0.06** | **0.665** | **0.852** |
| 50 | 0.08 | 0.733 | 0.852 |
| 50 | 0.10 | 0.793 | 0.861 |
| 20 | 0.06 | 0.732 | 0.852 |
| 100 | 0.06 | 0.622 | 0.850 |

Test RMSE is flat for reg 0.06 to 0.08 and barely depends on the number of
factors, so we keep 50 factors and reg 0.06. The prediction matrix used in the
experiments comes from a second fit on all ratings with the same settings.

## Change log

| Date | Assumption | Change | Why |
|---|---|---|---|
| 2026-11-14 | all | Initial version | Project setup |
| 2026-11-14 | A3 | MF fixed: own numpy ALS, reg 0.02 (placeholder) -> 0.06, learning rate removed | Placeholder overfitted (test RMSE 0.936); ALS has no learning rate |
| 2026-11-14 | A9, A10 | Added | Came up while implementing MF |
| 2026-11-14 | A9 | Predictions for all pairs -> observed ratings kept, only missing pairs predicted | Closer reading of the paper's wording (team decision) |
| 2026-11-14 | A9 | Filled-in predictions now clipped to [1, 5] | Same scale as the kept real ratings (team decision; paper is silent) |
| 2026-11-14 | A11 to A14 | Added | Came up while implementing metrics, groups, aggregators and the runner |
| 2026-11-14 | A11 | Gain `2^rel` -> `2^rel - 1` | Movies outside the ground truth should not count (team decision). E1 numbers unchanged to 3 decimals |
| 2026-11-15 | all | Added the "Paper says" and "Status" columns after checking each assumption against the paper text. A4 (ties), A5 and A11 (gain) are now marked as departures. No choice, config value or result changed | The old table presented everything as "left open by the paper", which was not accurate for A1, A4, A5, A6, A8, A11 |
| 2026-11-15 | A5 | Not changed. Diagnostic run with group-based similarity added to the notes | Levels shift a little, conclusions do not; switching would mean rerunning all SIM results |
| 2026-11-15 | A11 | Gain `2^rel - 1` -> `2^rel` (as printed in the paper) | Team decision: do not depart from the paper where it is explicit. Largest change in any group's result: 4e-6 |
| 2026-11-15 | A5 | SIM groups: similarity to the seed user -> mean similarity to all members so far | Team decision: closer to the paper's wording. E1, E2, E3 rerun; SIM fairness 0.01 to 0.04 higher, ordering unchanged |
| 2026-11-15 | A4 | Not changed. Diagnostic run with tied ranks added to the notes | Tied ranks remove XPO's lead over AVG at m = 5; decision pending |
| 2026-11-15 | A4 | Ties in ranks: broken by item id (strict ranks) -> tied average ranks; ground truth keeps the item-id order | Team decision: the paper allows tied ranks. E1, E2, E3, E5 rerun. XPO loses about 0.02 fairness at m = 3 to 10 and is no longer fairer than AVG at m = 5; AVG and LM unchanged |
| 2026-11-18 | A15 | One MF fit -> results averaged over 20 MF fits | Team decision for the report: the random start of a single fit moves results by up to 0.03 (six-fit check). Fit 0 reproduces the earlier single-fit results exactly. E1, E2, E3, E5 rerun |
| 2026-11-18 | A16, A17 | Added: Average without misery (AWM) as an extra baseline, threshold 3, fill rule for too few misery-free items | Team decision: extension. AWM does not use random numbers, so adding it changes no other method's result |
| 2026-11-18 | A18 | Added: rating-based metrics (no-misery share, mean rating) | Team decision: the paper's top-N metrics cannot see disliked items, which is why LM and AWM lose under them. Needs a rerun of all experiments; other metrics unchanged |
| 2026-11-18 | A19 | Added the paper's other score and rank baselines MUL, MAX, BORDA, MED | Team decision: they are in the paper's tables, so they add replication points. Checked that AVG, LM, NPO and XPO give identical results with them added |
| 2026-11-20 | A20 | Added: nDCG@20 with linear gain as a second nDCG metric; E1/E2/E3/E5 rerun over 20 fits | Presentation feedback: the headline should not depend only on the printed gain, which we argue the paper did not use. All other numbers unchanged (same seeds) |
| 2026-11-20 | A12 | Not changed. Documented the heavy-rater side effect of the full-vector cosine | Found while describing SIM groups for the report (`scripts/diagnostics/group_similarity.py`) |
