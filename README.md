# Group Fairness Replication

Replication and extension of Sacharidis (2019), *Top-N Group Recommendations with
Fairness*, for the WU Vienna course Applications of Data Science.

We implement the paper's two Pareto-based methods (NPO, XPO), compare them with
the paper's score and rank baselines (AVG, LM, MUL, MAX, BORDA, MED) on MovieLens 1M, and extend the group-size experiment
beyond the paper's range (m = 2..8) up to m = 30. As an extension we add
Average without Misery (AWM) as a further baseline. All results are averaged
over 20 MF fits with different random starts.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Download [MovieLens 1M](https://grouplens.org/datasets/movielens/1m/) and unpack it
so that `data/raw/ml-1m/ratings.dat` exists.

## Run

```bash
python scripts/train_mf.py                   # once; writes data/processed/predictions.npy
pytest -q                                    # must pass before any experiment run
python scripts/run_experiment.py --exp E1 --fits 2 --smoke   # 5 groups, 2 MF fits, quick check
python scripts/run_experiment.py --exp E1 E2 E3 E5            # 20 MF fits, about 40 minutes
python scripts/summarize.py                  # averages over fits -> results/summary/*.csv
python scripts/make_figures.py
python scripts/diagnostics/tie_order.py      # optional sensitivity checks, see docs/replication_notes.md
python scripts/diagnostics/awm_threshold.py  # AWM threshold and fill rule
```

## Experiments

| ID | What | Setting |
|---|---|---|
| E1 | Core replication (paper Tables 1/2) | m = 5, N = 20 |
| E2 | Group size, paper range (Fig. 2/3) | m = 2..8 |
| E3 | Group size extension (our contribution) | m up to 30 |
| E4 | Top-N (optional, Fig. 4/5) | N = 5..100 |
| E5 | Monte Carlo sensitivity | S = 1k..50k |

All settings live in `configs/default.yaml`.

## Layout

- `src/gfair/`: library code (data, MF, groups, Pareto pools, aggregators, metrics, experiment runner)
- `scripts/`: command-line entry points
- `tests/`: unit tests, including the paper's toy example (Fig. 1)
- `results/`: one tidy CSV per experiment (one row per MF fit, group, method, metric); `results/summary/` the averaged tables. The raw per-experiment CSVs (35 to 290 MB) are not in git; rerun `scripts/run_experiment.py` to regenerate them (same seed, same numbers)
- `docs/paper_tables.csv`: the paper's Tables 1 and 2 as data, for comparisons
- `figures/`: generated plots
- `docs/`: paper text and `replication_notes.md` (where our results differ from the paper and why)
- `ASSUMPTIONS.md`: every choice the paper leaves open, with the reason
- `AI_USE.md`: AI use disclosure log
