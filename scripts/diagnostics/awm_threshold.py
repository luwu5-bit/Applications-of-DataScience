"""How much does Average Without Misery depend on its threshold (A16) and on
how the list is filled when fewer than N items are free of misery (A17)?

Thresholds 2, 2.5, 3, 3.5, 4; two fill rules:
- fewest: items with the fewest unhappy members first, then by mean (our rule)
- mean:   misery-free items by mean, then all others by mean (plain AVG order)
AVG and LM as reference. Same groups and candidates as the main runs,
MF fits 0-4, m as in E3, N = 20, nDCG@20 and P@20.

Usage: python scripts/diagnostics/awm_threshold.py   (about 2 minutes)
Writes results/diagnostics/awm_threshold.csv. See docs/replication_notes.md.
"""
import numpy as np
import pandas as pd

from gfair import aggregators, metrics
from gfair.config import DEFAULT_CONFIG, REPO_ROOT, load_config
from gfair.data import load_ratings, reindex
from gfair.experiment import group_rng
from gfair.groups import centered_ratings, sample_candidates, sample_rnd_group, sample_sim_group
from gfair.mf import fill_missing, fit_rng, train_mf
from gfair.pareto import ground_truth

THRESHOLDS = [2.0, 2.5, 3.0, 3.5, 4.0]
FITS = range(5)
N = 20

cfg = load_config(DEFAULT_CONFIG); mf = cfg["mf"]
ratings, uids, iids = reindex(load_ratings(REPO_ROOT / cfg["data"]["raw_dir"]))
C = centered_ratings(ratings, len(uids), len(iids))


def awm_mean_fill(preds, threshold):
    ok = (preds >= threshold).all(axis=0)
    order = np.lexsort((np.arange(preds.shape[1]), -preds.mean(axis=0), ~ok))
    return order[:N]


def score(sigma, truth):
    nd = [metrics.ndcg_at_k(sigma, t, 20) for t in truth]
    p = [metrics.precision_at_k(sigma, t, 20) for t in truth]
    return min(nd), min(p)


rows = []
for fit in FITS:
    if fit == 0:
        M = np.load(REPO_ROOT / cfg["data"]["predictions_path"])
    else:
        raw = train_mf(ratings, len(uids), len(iids), rng=fit_rng(cfg["seed"], fit),
                       n_factors=mf["n_factors"], n_epochs=mf["n_epochs"], reg=mf["reg"])
        M = fill_missing(raw, ratings, clip=tuple(mf["clip"]))
    for gt in ["RND", "SIM"]:
        for m in cfg["experiments"]["E3"]["m"]:
            for gid in range(cfg["n_groups"]):
                rng = group_rng(cfg["seed"], gt, m, N, gid)
                members = sample_rnd_group(M.shape[0], m, rng) if gt == "RND" else sample_sim_group(C, m, rng)
                cand = sample_candidates(M.shape[1], cfg["n_candidates"], rng)
                preds = M[np.ix_(members, cand)]
                truth = ground_truth(preds, N)
                base = dict(fit=fit, gt=gt, m=m, group_id=gid)
                for name, sigma in [("AVG", aggregators.avg(preds, N)), ("LM", aggregators.lm(preds, N))]:
                    nd, p = score(sigma, truth)
                    rows.append(base | dict(method=name, threshold=np.nan, ndcg=nd, p20=p, pool=np.nan))
                for t in THRESHOLDS:
                    sigma, info = aggregators.awm(preds, N, t)
                    nd, p = score(sigma, truth)
                    rows.append(base | dict(method="AWM fewest", threshold=t, ndcg=nd, p20=p, pool=info["pool_size"]))
                    nd, p = score(awm_mean_fill(preds, t), truth)
                    rows.append(base | dict(method="AWM mean", threshold=t, ndcg=nd, p20=p, pool=info["pool_size"]))
    print("fit", fit, "done", flush=True)

df = pd.DataFrame(rows)
out = REPO_ROOT / "results" / "diagnostics" / "awm_threshold.csv"
out.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(out, index=False)

pd.set_option("display.width", 250)
df["label"] = df["method"] + df["threshold"].map(lambda t: "" if np.isnan(t) else f" {t:g}")
for col in ["ndcg", "p20", "pool"]:
    print(f"\nmean {col} (fairness for ndcg / p20; pool = misery-free items), over groups and fits")
    print(df.pivot_table(index="label", columns=["gt", "m"], values=col).round(3).to_string())
