# Assumptions

The paper (Sacharidis, 2019) leaves the points below open. Each one is fixed here
with a reason. Rule: never change one silently. If one changes, update this file
and `configs/default.yaml` in the same commit.

| # | Topic | Our choice | Reason | Config key |
|---|---|---|---|---|
| A1 | Weight distribution | Uniform on the simplex, `rng.dirichlet(np.ones(m))` | Paper gives no distribution; uniform encodes "no member is preferred a priori" | n/a |
| A2 | Monte Carlo samples S | 10,000 | Paper does not report S; checked for convergence in E5 (S in 1k, 5k, 10k, 50k) | `monte_carlo.n_samples` |
| A3 | MF model | Biased MF `mu + b_u + b_i + p_u . q_i`, own numpy implementation trained with alternating least squares (ALS), 50 factors, 20 sweeps, reg 0.06 scaled by rating count | Paper only says "a simple matrix factorization technique". Own code avoids an extra dependency; ALS has no learning rate to tune and is fast in numpy. Hyperparameters picked on a 10% hold-out (see below) | `mf.*` |
| A4 | Ranks | Exact over all 200 candidates, rank 1 = best, ties broken by item id | 200 items is small, so the paper's top-N' approximation is not needed | `n_candidates` |
| A5 | SIM groups | Random seed user, then add the users with the highest mean-centered cosine similarity **to the seed user** | Paper does not say whether similarity is to the seed or to the whole group; seed-based is simpler and deterministic given the seed | n/a |
| A6 | RND groups | Users sampled uniformly without replacement | Standard reading of "random groups" | n/a |
| A7 | Seeds | One global seed; groups, candidates and weights derive from it | Reproducibility | `seed` |
| A8 | Ground truth | Each member's top-N of the 200 candidates by predicted rating | Follows the paper's evaluation protocol | n/a |
| A9 | Rating matrix used for ranking | Observed ratings are kept; MF predictions are used only for the missing user-item pairs and are clipped to [1, 5] | The paper says MF is used "to fill in the missing ratings", so real ratings stay. It does not mention clipping; we clip so that every filled-in value is a valid rating and no prediction outranks a real 5 (also keeps out-of-range values out of AVG and LM). Consequence: more ties (integer observed ratings, predictions capped at 1 or 5), broken by item id (A4) | `mf.clip` |
| A10 | Items | Only the 3,706 movies with at least one rating (the paper counts 3,952 movie ids) | A movie without ratings has no learned factors, its prediction would be the same for every user up to the user bias | n/a |
| A11 | nDCG gain | `2^rel` exactly as printed in the paper, with rel = N - p + 1; nDCG reported at k = 1, 5, 10, 20 | Follows the paper's text. A miss earns 2^0 = 1 instead of 0: negligible at N = 20 (about 1e-5), visible at N = 5 (E4). Note: the paper's own nDCG values do not fit this formula, see `docs/replication_notes.md` | `metrics.ndcg_ks` |
| A12 | SIM similarity | Cosine over the full mean-centered rating vectors (unrated = 0), not only over co-rated movies | With co-rated-only, two users who share one or two movies get similarity +1 or -1 and groups fill up with noise | n/a |
| A13 | Equal Monte Carlo counts | Ties ordered by lower mean rank over members, then by item id | The paper does not address ties. They are certain when the pool has exactly N items (all counts = S). Mean rank is the equal-weights strategy, the centre of the weight simplex | n/a |
| A14 | Group seeds | One generator per group, keyed by (seed, group type, m, N, group id) | A group does not depend on the order in which settings are run; all methods see the same group and candidates | `seed` |

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
