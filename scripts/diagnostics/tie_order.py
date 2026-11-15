"""A4 check: how NPO / XPO react to the handling of equally rated movies.

Variants of the rank matrix given to NPO and XPO (ground truth, groups, candidates
and weight samples are the same in all of them):
- tied_avg:      tied movies share the average rank (the main setting)
- tied_min:      tied movies share the better rank
- strict_id:     ties broken by item id, the same order as the ground truth (setting until 2026-11-15)
- strict_random: ties broken in a random order, unrelated to the ground truth

Usage: python scripts/diagnostics/tie_order.py   (about 3 minutes)
Writes results/diagnostics/tie_order.csv. See docs/replication_notes.md.
"""
import numpy as np, pandas as pd
from scipy.stats import rankdata
from gfair import aggregators, metrics
from gfair.config import DEFAULT_CONFIG, REPO_ROOT, load_config
from gfair.data import load_ratings, reindex
from gfair.experiment import group_rng
from gfair.groups import centered_ratings, sample_candidates, sample_rnd_group, sample_sim_group
from gfair.pareto import ground_truth, rank_matrix

cfg = load_config(DEFAULT_CONFIG)
P = np.load(REPO_ROOT / cfg["data"]["predictions_path"])
ratings, uids, iids = reindex(load_ratings(REPO_ROOT / cfg["data"]["raw_dir"]))
C = centered_ratings(ratings, len(uids), len(iids))
N, S, B = 20, cfg["monte_carlo"]["n_samples"], cfg["monte_carlo"]["batch_size"]

def strict(preds, key):
    """Strict ranks (n, m); equal ratings ordered by `key` (lower first)."""
    m, n = preds.shape
    R = np.empty((m, n))
    for u in range(m):
        order = np.lexsort((key, -preds[u]))
        R[u, order] = np.arange(1, n + 1)
    return R.T

rows = []
for gt in ["RND", "SIM"]:
    for m in [2, 3, 5, 8, 10, 15, 20, 30]:
        for g in range(cfg["n_groups"]):
            for variant in ["tied_avg", "tied_min", "strict_id", "strict_random"]:
                rng = group_rng(cfg["seed"], gt, m, N, g)
                mem = sample_rnd_group(P.shape[0], m, rng) if gt == "RND" else sample_sim_group(C, m, rng)
                cand = sample_candidates(P.shape[1], cfg["n_candidates"], rng)
                preds = P[np.ix_(mem, cand)]
                truth = ground_truth(preds, N)
                if variant == "tied_avg":
                    R = rank_matrix(preds)
                elif variant == "tied_min":
                    R = rankdata(-preds, method="min", axis=1).T
                elif variant == "strict_id":
                    R = strict(preds, np.arange(preds.shape[1]))
                else:
                    R = strict(preds, np.random.default_rng([99, g, m]).permutation(preds.shape[1]))
                avg_u = np.array([metrics.ndcg_at_k(aggregators.avg(preds, N), t, 20) for t in truth])
                for name, fn in [("NPO", aggregators.npo), ("XPO", aggregators.xpo)]:
                    sigma, info = fn(R, N, S, rng, B)
                    u = np.array([metrics.ndcg_at_k(sigma, t, 20) for t in truth])
                    rows.append(dict(group_type=gt, m=m, group_id=g, variant=variant, method=name, fairness=u.min(),
                                     group_utility=u.mean(), avg_fairness=avg_u.min()))
        print(gt, m, flush=True)
df = pd.DataFrame(rows)
out = REPO_ROOT / "results" / "diagnostics" / "tie_order.csv"
out.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(out, index=False)

pd.set_option("display.width", 250)
print("fairness (nDCG@20)")
print(df.pivot_table(index=["group_type", "method", "variant"], columns="m", values="fairness").round(3).to_string())
x = df[df.method == "XPO"].assign(d=lambda d: d.fairness - d.avg_fairness)
g = x.groupby(["group_type", "variant", "m"])["d"].agg(["mean", "sem"])
print("XPO minus AVG, mean"); print(g["mean"].round(3).unstack().to_string())
print("XPO minus AVG, 95% CI half-width"); print((1.96 * g["sem"]).round(3).unstack().to_string())
