"""Run one experiment from the grid and write results/<exp>.csv.

Usage: python scripts/run_experiment.py --exp E1 [--smoke]
--smoke uses cfg["smoke_n_groups"] groups and writes results/<exp>_smoke.csv.
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


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exp", required=True, choices=["E1", "E2", "E3", "E4", "E5"])
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--config", default=DEFAULT_CONFIG)
    args = parser.parse_args()
    cfg = load_config(args.config)
    grid = cfg["experiments"][args.exp]
    n_groups = cfg["smoke_n_groups"] if args.smoke else cfg["n_groups"]

    predictions = np.load(REPO_ROOT / cfg["data"]["predictions_path"])
    centered = None
    if "SIM" in grid["group_types"]:
        ratings, user_ids, item_ids = reindex(load_ratings(REPO_ROOT / cfg["data"]["raw_dir"]))
        centered = centered_ratings(ratings, len(user_ids), len(item_ids))

    frames = []
    settings = itertools.product(
        grid["group_types"], grid["m"], grid["N"], grid.get("n_samples", [None])
    )
    for group_type, m, N, S in settings:
        t0 = time.perf_counter()
        frames.append(run_setting(
            predictions, centered, args.exp, group_type, m, N, cfg,
            n_groups=n_groups, n_samples=S,
        ))
        label = f"{group_type} m={m} N={N}" + (f" S={S}" if S else "")
        print(f"{label}: {n_groups} groups in {time.perf_counter() - t0:.1f}s", flush=True)

    results = pd.concat(frames, ignore_index=True)
    out = REPO_ROOT / "results" / f"{args.exp}{'_smoke' if args.smoke else ''}.csv"
    results.to_csv(out, index=False)
    print(f"wrote {out.relative_to(REPO_ROOT)} ({len(results):,} rows)\n")

    # Quick look at the primary metric; the full analysis is in make_figures.py.
    primary = f"ndcg@{min(max(cfg['metrics']['ndcg_ks']), min(grid['N']))}"
    keys = ["group_type", "m", "N"] + (["n_samples"] if "n_samples" in grid else []) + ["method"]
    summary = (
        results[results["metric"] == primary]
        .groupby(keys, dropna=False)[["fairness", "group_utility", "pool_size"]]
        .mean()
        .round(3)
    )
    print(f"mean over {n_groups} groups, metric = {primary}")
    print(summary.to_string())


if __name__ == "__main__":
    main()
