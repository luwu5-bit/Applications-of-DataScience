"""Run one experimental setting and return a tidy DataFrame."""

import time

import numpy as np
import pandas as pd

from gfair import aggregators, metrics
from gfair.groups import sample_candidates, sample_rnd_group, sample_sim_group
from gfair.pareto import ground_truth, rank_matrix

# One row per (group, method, metric). pool_size is NaN for AVG / LM.
RESULT_COLUMNS = [
    "exp", "group_type", "m", "N", "group_id", "method", "metric",
    "fairness", "group_utility", "pool_size", "runtime_s", "seed",
]
# Not in the base schema but needed for E3 (XPO level), E5 (S) and the
# averaging over MF fits (A15). pool_size of AWM = number of misery-free items.
EXTRA_COLUMNS = ["xpo_level", "n_samples", "mf_fit"]

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
    sigma: np.ndarray, truth: np.ndarray, N: int, ndcg_ks: list[int], precision_ks: list[int],
    preds: np.ndarray | None = None, misery_threshold: float | None = None,
    ndcg_linear_ks: list[int] = (),
) -> dict[str, np.ndarray]:
    """All metrics of the group list against every member's ground truth.

    `truth` has shape (m, N). Returns metric name -> array of m utilities.
    Cut-offs k > N are skipped. With `preds` (m, candidates) also the
    rating-based metrics of A18: "no_misery" (share of the list the member
    rates >= misery_threshold) and "rating" (the member's mean rating of it).
    """
    out: dict[str, list[float]] = {"tau": [], "ap": []}
    out |= {f"p@{k}": [] for k in precision_ks if k <= N}
    out |= {f"ndcg@{k}": [] for k in ndcg_ks if k <= N}
    out |= {f"ndcg_lin@{k}": [] for k in ndcg_linear_ks if k <= N}   # A20
    if preds is not None:
        out["no_misery"] = [metrics.no_misery_share(sigma, r, misery_threshold) for r in preds]
        out["rating"] = [metrics.mean_rating(sigma, r) for r in preds]
    for sigma_u in truth:
        out["tau"].append(metrics.kendall_tau(sigma, sigma_u))
        out["ap"].append(metrics.average_precision(sigma, sigma_u))
        for k in precision_ks:
            if k <= N:
                out[f"p@{k}"].append(metrics.precision_at_k(sigma, sigma_u, k))
        for k in ndcg_ks:
            if k <= N:
                out[f"ndcg@{k}"].append(metrics.ndcg_at_k(sigma, sigma_u, k))
        for k in ndcg_linear_ks:
            if k <= N:
                out[f"ndcg_lin@{k}"].append(metrics.ndcg_at_k(sigma, sigma_u, k, gain="linear"))
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
    mf_fit: int = 0,
) -> pd.DataFrame:
    """Evaluate all configured methods on n_groups groups of size m.

    `predictions` is the filled rating matrix (users x items); `centered` the
    matrix from groups.centered_ratings (only needed for SIM groups).
    `n_groups` and `n_samples` override the config (smoke runs, E5).
    `mf_fit` only labels the rows: which MF fit produced `predictions` (A15).
    Groups, candidates and weight samples do not depend on it.
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
        truth = ground_truth(preds, N)                              # (m, N), best first

        for method in cfg["methods"]:
            info: dict = {}
            t0 = time.perf_counter()
            if method == "AVG":
                sigma = aggregators.avg(preds, N)
            elif method == "LM":
                sigma = aggregators.lm(preds, N)
            elif method == "MUL":
                sigma = aggregators.mul(preds, N)
            elif method == "MAX":
                sigma = aggregators.max_pleasure(preds, N)
            elif method == "BORDA":
                sigma = aggregators.borda(ranks, N)
            elif method == "MED":
                sigma = aggregators.med(ranks, N)
            elif method == "AWM":
                sigma, info = aggregators.awm(preds, N, cfg["awm"]["threshold"])
            elif method == "NPO":
                sigma, info = aggregators.npo(ranks, N, S, rng, batch)
            elif method == "XPO":
                sigma, info = aggregators.xpo(ranks, N, S, rng, batch)
            else:
                raise ValueError(f"unknown method {method!r}")
            runtime = time.perf_counter() - t0

            utils = member_utilities(
                sigma, truth, N, cfg["metrics"]["ndcg_ks"], cfg["metrics"]["precision_ks"],
                preds=preds, misery_threshold=cfg["metrics"]["misery_threshold"],
                ndcg_linear_ks=cfg["metrics"].get("ndcg_linear_ks", []),
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
                    "mf_fit": mf_fit,
                })

    return pd.DataFrame(rows, columns=RESULT_COLUMNS + EXTRA_COLUMNS)
