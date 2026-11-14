# Group Fairness Replication

Replication and extension of Sacharidis (2019), *Top-N Group Recommendations with
Fairness*, for the WU Vienna course Applications of Data Science.

We implement the paper's two Pareto-based methods (NPO, XPO), compare them with
the AVG and LM baselines on MovieLens 1M, and extend the group-size experiment
beyond the paper's range (m = 2..8) up to m = 30.

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
python scripts/run_experiment.py --exp E1 --smoke   # 5 groups, quick check
python scripts/run_experiment.py --exp E1
python scripts/make_figures.py
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
- `results/`: one tidy CSV per experiment
- `figures/`: generated plots
- `docs/`: paper text and `replication_notes.md` (where our results differ from the paper and why)
- `ASSUMPTIONS.md`: every choice the paper leaves open, with the reason
- `AI_USE.md`: AI use disclosure log
