# CLAUDE.md: Group Fairness Replication

WU Vienna course project (Applications of Data Science). We replicate
Sacharidis (2019), *Top-N Group Recommendations with Fairness* (ACM SAC '19,
https://doi.org/10.1145/3297280.3297442), and extend it to larger and smaller groups.

Deadlines: **18 Nov 2026** final presentation (results + critical evaluation),
**22 Nov 2026** final report (max 5 pages excl. code) and code submission.
Priority order: core replication first, then the group-size extension, then extras.

## Goal

1. **Replicate:** implement NPO and XPO and compare them against AVG and LM on
   MovieLens 1M for random (RND) and similar (SIM) groups. Main setting: m = 5, N = 20.
2. **Extend (group size scaling):** run the same pipeline for smaller and larger
   groups than the paper (paper: m = 2..8), e.g. m in {2, 3, 5, 8, 10, 15, 20, 30}.
   Track how fairness, group utility, candidate pool size and runtime change with m.
3. Report where our numbers match the paper, where they differ, and why.

## Method in short (what the code must do)

For one group of m users and a candidate set of 200 random movies:

1. **Predictions:** fill the rating matrix with matrix factorization (MF).
2. **Ground truth:** for each member, rank the 200 candidates by predicted rating.
   The member's top-N is their ground truth list. Rank 1 = best.
3. **Item vectors:** every item i is a vector r(i) = (rank_u1(i), ..., rank_um(i)).
4. **Dominance:** i dominates j if r_u(i) <= r_u(j) for all u and < for at least one u.
   `dom_count(i)` = number of items that dominate i.
5. **Candidate pools:**
   - NPO: all items with `dom_count <= N - 1`.
   - XPO: smallest level x in [1, N] (binary search) such that
     `|{i : dom_count(i) <= x - 1}| >= N`; pool = those items.
6. **Monte Carlo scoring:** draw S weight vectors w from the simplex. For each w,
   score(i) = sum_u w_u * r_u(i) (lower is better); every pool item in the top N
   gets +1. Rank the pool by count (descending) and return the top N.
7. **Evaluate** the group list against each member's ground truth.

Baselines: AVG (mean predicted rating), LM (min predicted rating). Optional if
time allows: MUL, MAX, BORDA (mean rank). The paper's fairness-aware baselines
(GRF, SPG, EFG, GVAR, PEN) are out of scope.

## Metrics

Member utility = similarity of group list sigma to member's ground truth sigma_u.
- **Fairness** = min over members. **Group utility** = mean over members.
- Report values averaged over 100 groups per setting, plus std / 95% CI.

| Metric | Definition we use |
|---|---|
| nDCG@k (primary, k = 20) | relevance of ground-truth item at position p = N - p + 1, else 0; gain 2^rel; discount log2(pos + 1); normalized by ideal DCG@k |
| AP | sum over k of P@k * [sigma[k] in sigma_u], divided by N |
| P@k | \|sigma[1:k] ∩ sigma_u\| / k, for k in {1, 5, 10, 20} |
| Kendall's tau | items missing from a list are tied at the last rank; (concordant - discordant) / number of pairs |

## Documented assumptions (paper leaves these open)

Keep every assumption in `ASSUMPTIONS.md` with the reason. Never change one
silently; if you change one, update that file and the config.

- **Weights:** uniform on the simplex, `rng.dirichlet(np.ones(m))`.
- **Monte Carlo samples:** S = 10,000 default; run a sensitivity check with
  S in {1k, 5k, 10k, 50k} and report convergence.
- **MF:** explicit-rating MF (e.g. biased SVD), fixed hyperparameters in the config,
  report train/test RMSE once as a sanity check.
- **Ranks:** computed exactly over all 200 candidates (no top-N' approximation
  needed in the experiments). Ties are broken by item id.
- **SIM groups:** start from a random seed user, then repeatedly add the user with
  the highest mean-centered cosine similarity to the seed user. (The paper does not
  say whether similarity is to the seed or to the whole group; document the choice.)
- **RND groups:** users sampled uniformly without replacement.
- **Seeds:** one global seed in the config; groups, candidates and weights derive from it.

## Known issues in the paper (useful for the report)

- Toy example (Fig. 1): the paper states the tie at w = (3/7, 4/7) and P(i2 top-1) = 4/7.
  With ranks i1 = (4, 1), i2 = (1, 3) the tie is at w = (2/5, 3/5), so P(i2) = 0.6
  under uniform weights. Our tests use the correct values.
- Text cites XPO 0.579 / NPO 0.472 / MUL 0.438 as RND results, but these are in
  Table 2 (SIM). Both tables are called "Table 1" in the text.
- Not reported: S, weight distribution, MF settings, runtime, significance tests.

## Reference values to compare against (m = 5, N = 20, nDCG@20)

| | Fairness RND | Fairness SIM | Group utility RND | Group utility SIM |
|---|---|---|---|---|
| AVG | 0.298 | 0.437 | 0.455 | 0.577 |
| LM | 0.197 | 0.403 | 0.341 | 0.542 |
| NPO | 0.311 | 0.472 | 0.466 | 0.601 |
| XPO | 0.406 | 0.579 | 0.532 | 0.674 |

Aim to reproduce the **ranking and trends** (XPO > NPO > AVG > LM on fairness),
not exact numbers. Exact numbers depend on MF and sampling choices.

## Experiment grid

| Experiment | m | N | Groups | Purpose |
|---|---|---|---|---|
| E1 core | 5 | 20 | RND, SIM | Replicate Tables 1/2 (all metrics) |
| E2 group size (paper) | 2..8 | 20 | RND, SIM | Replicate Fig. 2/3 |
| E3 group size (extension) | 2, 3, 5, 8, 10, 15, 20, 30 | 20 | RND, SIM | Our contribution |
| E4 top-N (optional) | 5 | 5, 10, 20, 50, 100 | RND, SIM | Replicate Fig. 4/5 |
| E5 MC sensitivity | 5, 20 | 20 | RND | Stability of NPO/XPO vs S |

For E3 also log per group: NPO pool size, XPO pool size and level x, runtime per method.
Hypothesis to check: with large m almost every item becomes Pareto optimal, so the
NPO pool approaches all 200 items and NPO may behave more like AVG, while XPO
stays selective. For m >= 15, check whether S = 10,000 is still enough.

## Project structure

```
group-fairness-replication/
├── CLAUDE.md
├── ASSUMPTIONS.md
├── README.md
├── requirements.txt
├── configs/
│   └── default.yaml          # seed, MF params, S, m/N grids, n_groups, n_candidates
├── data/
│   ├── raw/ml-1m/            # ratings.dat etc. (gitignored)
│   └── processed/            # predicted rating matrix (.npy, gitignored)
├── src/gfair/
│   ├── data.py               # load MovieLens 1M
│   ├── mf.py                 # train MF, save full prediction matrix
│   ├── groups.py             # RND / SIM group sampling, candidate sampling
│   ├── pareto.py             # rank matrix, dominance counts, NPO/XPO pools
│   ├── aggregators.py        # AVG, LM, (MUL, MAX, BORDA), NPO, XPO
│   ├── metrics.py            # nDCG@k, AP, P@k, Kendall tau, fairness, group utility
│   └── experiment.py         # run one setting, return tidy DataFrame
├── scripts/
│   ├── train_mf.py
│   ├── run_experiment.py     # python scripts/run_experiment.py --exp E1
│   └── make_figures.py
├── tests/
│   ├── test_toy_example.py
│   ├── test_pareto.py
│   └── test_metrics.py
├── results/                  # CSV per experiment, one row per (group, method, metric)
└── figures/
```

## Commands

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt      # numpy, pandas, scipy, pyyaml, matplotlib, pytest (+ MF lib)
python scripts/train_mf.py           # once; writes data/processed/predictions.npy
pytest -q                            # must pass before any experiment run
python scripts/run_experiment.py --exp E1
python scripts/make_figures.py
```

MovieLens 1M: https://grouplens.org/datasets/movielens/1m/ (download manually into `data/raw/ml-1m/`).

## Required tests (toy example from Fig. 1)

Ranks (u1, u2): i1 (4,1), i2 (1,3), i3 (2,4), i4 (6,2), i5 (3,6), i6 (5,5).
- dom_count: i1 0, i2 0, i3 1, i4 1, i5 2, i6 3.
- Level-1 Pareto set = {i1, i2}; level-2 = {i1, i2, i3, i4}.
- XPO with N = 2: x = 1, pool = {i1, i2}.
- Top-1 probabilities (uniform weights, large S): i2 ≈ 0.60, i1 ≈ 0.40.
- Top-2 inclusion over NPO pool: i2 ≈ 0.833, i1 ≈ 0.60, i3 ≈ 0.40, i4 ≈ 0.167
  (tolerance ±0.01 with S = 200,000). NPO top-2 list = [i2, i1].
- Metric tests: identical lists give nDCG = AP = P@k = tau = 1; reversed list gives tau = -1.

## Coding conventions

- Python 3.11+, numpy-vectorized. No Python loops over items inside the Monte Carlo
  step: compute scores as `W @ R.T` (S × items) in batches, then `argpartition`.
- Dominance counts via broadcasting on the (items × m) rank matrix; fine for 200 items.
- Pure functions in `src/`, all randomness through a passed `np.random.Generator`.
- Core logic never lives in notebooks; notebooks only for exploration and plots.
- Results as tidy CSV: `exp, group_type, m, N, group_id, method, metric, fairness, group_utility, pool_size, runtime_s, seed`.
- Before a long run, do a smoke run with `n_groups = 5`.
- Do not modify `data/raw/`. Do not commit data or large result files.

## Working with Claude

- Explain non-obvious design choices briefly in code comments or ASSUMPTIONS.md.
- When results differ from the paper, investigate (metric definition, tie handling,
  MF quality, S) before tuning anything, and write down what you found.
- Never tune choices to match the paper's numbers without documenting it.
- AI use must be disclosed in the report (WU guidelines). Keep a short log in
  `AI_USE.md`: tool, date, what it was used for.
