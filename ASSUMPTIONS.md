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
| A3 | MF model | Biased MF `mu + b_u + b_i + p_u . q_i`, own numpy implementation trained with alternating least squares (ALS), 50 factors, 20 sweeps, reg 0.06 scaled by rating count | Only "a simple matrix factorization technique" | Open | Own code avoids an extra dependency; ALS has no learning rate to tune and is fast in numpy. Hyperparameters picked on a 10% hold-out (see below) | `mf.*` |
| A4 | Ranks | Exact over all 200 candidates, rank 1 = best; equal ratings are broken by item id, so every member's ranks are strict | Exact ranks are the main definition; the top-N' approximation is only for when "this is impractical". Lower rank = better follows from the dominance definition. On ties: "we assume that ties in ranks are possible" | From paper (exact ranks); **Departs** (ties) | 200 items is small, so exact ranks are practical. Strict ranks keep the code simple and deterministic. Consequence: of two movies a member rates equally, the one with the lower id counts as better for that member, which can create a dominance the paper's tied ranks would not. Ties are common because of A9 | `n_candidates` |
| A5 | SIM groups | Random seed user, then add the users with the highest mean-centered cosine similarity **to the seed user** | "starting from a randomly selected user, the group is build incrementally by adding the most similar (in terms of mean-centered cosine similarity) user to the group" | **Departs** (probably) | The wording is ambiguous but leans towards similarity to the whole group so far, not to the seed. Ours is the weaker reading, kept because it is simpler and deterministic given the seed. Likely effect: our SIM groups are somewhat less homogeneous than the paper's, since members are similar to the seed but not necessarily to each other. Tested on 2026-11-15 (`docs/replication_notes.md`): the group-based reading gives tighter groups and 0.01 to 0.04 higher fairness, but the same ordering of methods, so the choice was not changed | n/a |
| A6 | RND groups | Users sampled uniformly without replacement | "sampling uniformly at random from MovieLens" | From paper | "Without replacement" is implicit: a group cannot contain the same user twice | n/a |
| A7 | Seeds | One global seed; groups, candidates and weights derive from it | Nothing | Open | Reproducibility | `seed` |
| A8 | Ground truth | Each member's top-N of the 200 candidates by predicted rating | "we select 200 items at random, and we set the ground truth of each member to her top-N items among them recommended by the system" | From paper | Not an assumption; listed for completeness | n/a |
| A9 | Rating matrix used for ranking | Observed ratings are kept; MF predictions are used only for the missing user-item pairs and are clipped to [1, 5] | MF is used "to fill in the missing ratings in the dataset". Nothing on clipping | Supported (keep real ratings); Open (clipping) | Clipping makes every filled-in value a valid rating, so no prediction outranks a real 5 (also keeps out-of-range values out of AVG and LM). Consequence: more ties (integer observed ratings, predictions capped at 1 or 5), broken by item id (A4) | `mf.clip` |
| A10 | Items | Only the 3,706 movies with at least one rating (the paper counts 3,952 movie ids) | Nothing | Open | A movie without ratings has no learned factors, its prediction would be the same for every user up to the user bias | n/a |
| A11 | nDCG gain | `2^rel - 1` with rel = N - p + 1; nDCG reported at k = 1, 5, 10, 20 | Relevance N - p + 1 ("Borda semantics") and the cutoffs 1, 5, 10, 20 (Table 1) are the paper's. The printed gain is `2^rel` | From paper (relevance, cutoffs); **Departs** (gain) | Under `2^rel` a movie outside the member's ground truth still earns 2^0 = 1. With `- 1` (the standard form) a miss earns nothing. Effect: about 1e-5 at N = 20, but at N = 5 a completely wrong list would score about 0.06 under the printed form. Note: the paper's own nDCG values fit neither form, see `docs/replication_notes.md` | `metrics.ndcg_ks` |
| A12 | SIM similarity | Cosine over the full mean-centered rating vectors (unrated = 0), not only over co-rated movies | Only "mean-centered cosine similarity" | Open | With co-rated-only, two users who share one or two movies get similarity +1 or -1 and groups fill up with noise | n/a |
| A13 | Equal Monte Carlo counts | Ties ordered by lower mean rank over members, then by item id | Nothing | Open | Ties are certain when the pool has exactly N items (all counts = S). Mean rank is the equal-weights strategy, the centre of the weight simplex | n/a |
| A14 | Group seeds | One generator per group, keyed by (seed, group type, m, N, group id) | Nothing | Open | A group does not depend on the order in which settings are run; all methods see the same group and candidates | `seed` |

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
