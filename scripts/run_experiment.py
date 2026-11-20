"""Run experiments from the grid over several MF fits and write results/<exp>.csv.

Usage:
    python scripts/run_experiment.py --exp E1 [E2 E3 ...] [--fits K] [--smoke]

Every experiment is run on K MF fits that differ only in their random start
(A15; default K = cfg["mf"]["n_fits"]). Fit 0 is the saved matrix
data/processed/predictions.npy; fits 1..K-1 are trained here, one at a time,
and not saved (each is reproducible from the global seed). Each MF fit is
trained once and used for all requested experiments. The CSV has one row per
(fit, group, method, metric) and is rewritten after every fit.

--fits 1 runs on the saved fit only. --smoke uses cfg["smoke_n_groups"]
groups and writes results/<exp>_smoke.csv.
"""

import argparse
import itertools
import time

import numpy as np
import pandas as pd

from gfair.config import DEFAULT_CONFIG, REPO_ROOT, load_config
from gfair.data import load_ratings, reindex
from gfair.experiment import run_setting
from gfair.groups import centered_ratings
from gfair.mf import fill_missing, fit_rng, train_mf

EXPERIMENTS = ["E1", "E2", "E3", "E4", "E5"]


def predictions_for_fit(fit: int, ratings: pd.DataFrame, n_users: int, n_items: int, cfg: dict) -> np.ndarray:
    """Filled rating matrix of MF fit `fit` (A9, A15)."""
    if fit == 0:
        return np.load(REPO_ROOT / cfg["data"]["predictions_path"])
    mf = cfg["mf"]
    raw = train_mf(ratings, n_users, n_items, rng=fit_rng(cfg["seed"], fit),
                   n_factors=mf["n_factors"], n_epochs=mf["n_epochs"], reg=mf["reg"])
    return fill_missing(raw, ratings, clip=tuple(mf["clip"]))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--exp", required=True, nargs="+", choices=EXPERIMENTS)
    parser.add_argument("--fits", type=int, default=None, help="number of MF fits (default: config)")
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--config", default=DEFAULT_CONFIG)
    args = parser.parse_args()
    cfg = load_config(args.config)
    n_fits = args.fits or cfg["mf"]["n_fits"]
    n_groups = cfg["smoke_n_groups"] if args.smoke else cfg["n_groups"]

    ratings, user_ids, item_ids = reindex(load_ratings(REPO_ROOT / cfg["data"]["raw_dir"]))
    n_users, n_items = len(user_ids), len(item_ids)
    # SIM groups use observed ratings only, so they are the same for every fit.
    centered = centered_ratings(ratings, n_users, n_items)

    frames: dict[str, list[pd.DataFrame]] = {exp: [] for exp in args.exp}
    for fit in range(n_fits):
        t_fit = time.perf_counter()
        predictions = predictions_for_fit(fit, ratings, n_users, n_items, cfg)
        print(f"fit {fit}: MF ready in {time.perf_counter() - t_fit:.0f}s", flush=True)
        for exp in args.exp:
            grid = cfg["experiments"][exp]
            t0 = time.perf_counter()
            settings = itertools.product(
                grid["group_types"], grid["m"], grid["N"], grid.get("n_samples", [None])
            )
            for group_type, m, N, S in settings:
                frames[exp].append(run_setting(
                    predictions, centered, exp, group_type, m, N, cfg,
                    n_groups=n_groups, n_samples=S, mf_fit=fit,
                ))
            out = REPO_ROOT / "results" / f"{exp}{'_smoke' if args.smoke else ''}.csv"
            pd.concat(frames[exp], ignore_index=True).to_csv(out, index=False)
            print(f"  {exp}: {time.perf_counter() - t0:.0f}s, wrote {out.relative_to(REPO_ROOT)}", flush=True)
        del predictions

    # Quick look at the primary metric, averaged over groups and fits.
    for exp in args.exp:
        grid = cfg["experiments"][exp]
        results = pd.concat(frames[exp], ignore_index=True)
        primary = f"ndcg@{min(max(cfg['metrics']['ndcg_ks']), min(grid['N']))}"
        keys = ["group_type", "m", "N"] + (["n_samples"] if "n_samples" in grid else []) + ["method"]
        summary = (
            results[results["metric"] == primary]
            .groupby(keys, dropna=False)[["fairness", "group_utility", "pool_size"]]
            .mean()
            .round(3)
        )
        print(f"\n{exp}: mean over {n_groups} groups and {n_fits} MF fits, metric = {primary}")
        print(summary.to_string())


if __name__ == "__main__":
    main()
