"""Train MF once and write data/processed/predictions.npy.

Usage: python scripts/train_mf.py [--config configs/default.yaml]

Two fits: one on a train split to report train/test RMSE (sanity check), then
one on all ratings. The saved matrix keeps the observed ratings and uses the
MF predictions, clipped to the rating scale, only for the missing user-item
pairs (ASSUMPTIONS.md, A9).
"""

import argparse
import time
from pathlib import Path

import numpy as np

from gfair.config import DEFAULT_CONFIG, REPO_ROOT, load_config
from gfair.data import load_ratings, reindex
from gfair.mf import fill_missing, rmse, train_mf, train_test_split


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=DEFAULT_CONFIG)
    args = parser.parse_args()
    cfg = load_config(args.config)
    mf = cfg["mf"]
    fit = dict(n_factors=mf["n_factors"], n_epochs=mf["n_epochs"], reg=mf["reg"])

    ratings, user_ids, item_ids = reindex(load_ratings(REPO_ROOT / cfg["data"]["raw_dir"]))
    n_users, n_items = len(user_ids), len(item_ids)
    print(f"{len(ratings):,} ratings, {n_users:,} users, {n_items:,} rated items")

    # Independent streams for the split and the two fits, all from the global seed.
    split_rng, check_rng, final_rng = np.random.default_rng(cfg["seed"]).spawn(3)

    t0 = time.perf_counter()
    train, test = train_test_split(ratings, mf["test_fraction"], split_rng)
    check = train_mf(train, n_users, n_items, rng=check_rng, **fit)
    print(f"sanity check: train RMSE {rmse(check, train):.4f}, "
          f"test RMSE {rmse(check, test):.4f} ({time.perf_counter() - t0:.0f}s)")

    t0 = time.perf_counter()
    predictions = train_mf(ratings, n_users, n_items, rng=final_rng, **fit)
    out = REPO_ROOT / cfg["data"]["predictions_path"]
    out.parent.mkdir(parents=True, exist_ok=True)
    np.save(out, fill_missing(predictions, ratings, clip=tuple(mf["clip"])))
    # Column j of the matrix is MovieLens movie id item_ids[j]; same for users.
    np.save(out.with_name("item_ids.npy"), item_ids.to_numpy())
    np.save(out.with_name("user_ids.npy"), user_ids.to_numpy())
    print(f"final fit on all ratings: RMSE {rmse(predictions, ratings):.4f} "
          f"({time.perf_counter() - t0:.0f}s)")
    print(f"wrote {Path(out).relative_to(REPO_ROOT)} with shape {predictions.shape}: "
          f"{len(ratings) / predictions.size:.1%} observed ratings, rest MF predictions")


if __name__ == "__main__":
    main()
