"""Two sensitivity checks on the main MF fit, m = 5, N = 20, same 100 groups:
(a) nDCG gain (A11): 2^rel as printed vs linear vs binary;
(b) rating matrix (A9): real ratings kept (main setting) vs MF predictions for
    every pair, with and without clipping.

Usage: python scripts/diagnostics/rating_matrix_and_gain.py   (about 1 minute)
Prints the tables used in docs/replication_notes.md; writes no file.
"""
import numpy as np, pandas as pd
from gfair import experiment, metrics
from gfair.config import DEFAULT_CONFIG, REPO_ROOT, load_config
from gfair.data import load_ratings, reindex
from gfair.groups import centered_ratings
from gfair.mf import train_mf

cfg = load_config(DEFAULT_CONFIG); mf = cfg["mf"]
ratings, uids, iids = reindex(load_ratings(REPO_ROOT / cfg["data"]["raw_dir"]))
C = centered_ratings(ratings, len(uids), len(iids))
P = np.load(REPO_ROOT / cfg["data"]["predictions_path"])
_, _, final_rng = np.random.default_rng(cfg["seed"]).spawn(3)       # same stream as train_mf.py
raw = train_mf(ratings, len(uids), len(iids), rng=final_rng, n_factors=mf["n_factors"], n_epochs=mf["n_epochs"], reg=mf["reg"])
u, i = ratings["u"].to_numpy(), ratings["i"].to_numpy()
chk = np.clip(raw, 1, 5); chk[u, i] = ratings["rating"].to_numpy()
print("refit reproduces saved matrix: max abs diff", np.abs(chk - P).max())

def ndcg_gain(gain):
    def f(sigma, sigma_u, k):
        N = len(sigma_u); top = np.asarray(sigma)[:k]
        hit = top[:, None] == np.asarray(sigma_u)[None, :]
        rel = (hit * (N - np.arange(N))).sum(axis=1); ideal = np.clip(N - np.arange(k), 0, None)
        g = {"exp": lambda r: 2.0 ** r, "linear": lambda r: r.astype(float), "binary": lambda r: (r > 0).astype(float)}[gain]
        disc = np.log2(np.arange(k) + 2)
        return float((g(rel) / disc[:len(top)]).sum() / (g(ideal) / disc).sum())
    return f

orig = metrics.ndcg_at_k
def ci(x): return 1.96 * x.std(ddof=1) / np.sqrt(len(x))
def report(label, M, gain="exp"):
    metrics.ndcg_at_k = ndcg_gain(gain)
    out = []
    for gt in ["RND", "SIM"]:
        d = experiment.run_setting(M, C, "diag", gt, 5, 20, cfg); d = d[d.metric == "ndcg@20"]
        w = d.pivot_table(index="group_id", columns="method", values="fairness")
        x = w["XPO"] - w["AVG"]; n = w["NPO"] - w["AVG"]
        out.append(f"{gt}: " + " ".join(f"{k} {w[k].mean():.3f}" for k in ["AVG", "LM", "NPO", "XPO"]) +
                   f" | XPO-AVG {x.mean():+.3f}±{ci(x):.3f} NPO-AVG {n.mean():+.3f}±{ci(n):.3f}")
    metrics.ndcg_at_k = orig
    print(label); print("  " + "\n  ".join(out), flush=True)

for g in ["exp", "linear", "binary"]:
    report(f"current matrix, gain {g}", P, g)
report("MF predictions for all pairs, not clipped", raw)
report("MF predictions for all pairs, clipped", np.clip(raw, 1, 5))
for name, M in [("current", P), ("pure MF", raw), ("pure MF clipped", np.clip(raw, 1, 5))]:
    rng = np.random.default_rng(0); us = rng.choice(M.shape[0], 500); 
    fr = np.mean([1 - len(np.unique(M[uu, rng.choice(M.shape[1], 200, replace=False)])) / 200 for uu in us])
    print(name, "share of repeated values among 200 candidates:", round(fr, 3))
