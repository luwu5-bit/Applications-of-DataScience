"""Run one experimental setting and return a tidy DataFrame."""

import time

import numpy as np
import pandas as pd

from gfair import aggregators, metrics
from gfair.groups import sample_candidates, sample_rnd_group, sample_sim_group
from gfair.pareto import rank_matrix

# One row per (group, method, metric). pool_size is NaN for AVG / LM.
RESULT_COLUMNS = [
    "exp", "group_type", "m", "N", "group_id", "method", "metric",
    "fairness", "group_utility", "pool_size", "runtime_s", "seed",
]
# Not in the base schema but needed for E3 (XPO level) and E5 (S).
EXTRA_COLUMNS = ["xpo_level", "n_samples"]

GROUP_TYPES = ["RND", "SIM"]


def group_rng(seed: int, group_type: str, m: int, N: int, group_id: int) -> np.random.Generator:
    """Generator for one group, derived from the global seed (A7).

    Keyed by the setting, so a group does not depend on the order in which
    settings are run, and the same (type, m, N, id) gives the same group in
    every experiment.
    """
    key = (GROUP_TYPES.index(group_type), m, N, group_id)
    return np.random.default_rng(np.random.SeedSequence(seed, spawn_key=key))


def member_utilities(
    sigma: np.ndarray, truth: np.ndarray, N: int, ndcg_ks: list[int], precision_ks: list[int]
) -> dict[str, np.ndarray]:
    """All metrics of the group list against every member's ground truth.

    `truth` has shape (m, N). Returns metric name -> array of m utilities.
    Cut-offs k > N are skipped.
    """
    out: dict[str, list[float]] = {"tau": [], "ap": []}
    out |= {f"p@{k}": [] for k in precision_ks if k <= N}
    out |= {f"ndcg@{k}": [] for k in ndcg_ks if k <= N}
    for sigma_u in truth:
        out["tau"].append(metrics.kendall_tau(sigma, sigma_u))
        out["ap"].append(metrics.average_precision(sigma, sigma_u))
        for k in precision_ks:
            if k <= N:
                out[f"p@{k}"].append(metrics.precision_at_k(sigma, sigma_u, k))
        for k in ndcg_ks:
            if k <= N:
                out[f"ndcg@{k}"].append(metrics.ndcg_at_k(sigma, sigma_u, k))
    return {name: np.array(vals) for name, vals in out.items()}


def run_setting(
    predictions: np.ndarray,
    centered: np.ndarray | None,
    exp: str,
    group_type: str,
    m: int,
    N: int,
    cfg: dict,
    n_groups: int | None = None,
    n_samples: int | None = None,
) -> pd.DataFrame:
    """Evaluate all configured methods on n_groups groups of size m.

    `predictions` is the filled rating matrix (users x items); `centered` the
    matrix from groups.centered_ratings (only needed for SIM groups).
    `n_groups` and `n_samples` override the config (smoke runs, E5).
    """
    seed = cfg["seed"]
    n_groups = n_groups or cfg["n_groups"]
    S = n_samples or cfg["monte_carlo"]["n_samples"]
    batch = cfg["monte_carlo"]["batch_size"]
    n_users, n_items = predictions.shape
    rows = []

    for group_id in range(n_groups):
        rng = group_rng(seed, group_type, m, N, group_id)
        if group_type == "RND":
            members = sample_rnd_group(n_users, m, rng)
        else:
            members = sample_sim_group(centered, m, rng)
        candidates = sample_candidates(n_items, cfg["n_candidates"], rng)

        preds = predictions[np.ix_(members, candidates)]            # (m, 200)
        ranks = rank_matrix(preds)                                  # (200, m)
        truth = np.argsort(ranks, axis=0)[:N].T                     # (m, N), best first

        for method in cfg["methods"]:
            info: dict = {}
            t0 = time.perf_counter()
            if method == "AVG":
                sigma = aggregators.avg(preds, N)
            elif method == "LM":
                sigma = aggregators.lm(preds, N)
            elif method == "NPO":
                sigma, info = aggregators.npo(ranks, N, S, rng, batch)
            elif method == "XPO":
                sigma, info = aggregators.xpo(ranks, N, S, rng, batch)
            else:
                raise ValueError(f"unknown method {method!r}")
            runtime = time.perf_counter() - t0

            utils = member_utilities(
                sigma, truth, N, cfg["metrics"]["ndcg_ks"], cfg["metrics"]["precision_ks"]
            )
            for metric, values in utils.items():
                rows.append({
                    "exp": exp, "group_type": group_type, "m": m, "N": N,
                    "group_id": group_id, "method": method, "metric": metric,
                    "fairness": metrics.fairness(values),
                    "group_utility": metrics.group_utility(values),
                    "pool_size": info.get("pool_size", np.nan),
                    "runtime_s": runtime, "seed": seed,
                    "xpo_level": info.get("x", np.nan),
                    "n_samples": S if method in ("NPO", "XPO") else np.nan,
                })

    return pd.DataFrame(rows, columns=RESULT_COLUMNS + EXTRA_COLUMNS)
