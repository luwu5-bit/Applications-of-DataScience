"""How much do the results depend on the random start of the MF (A3), and on
keeping the real ratings (A9)?

Six MF fits that differ only in the random start ("main" reproduces the fit behind
data/processed/predictions.npy). For each fit two rating matrices:
- kept: real ratings kept, missing pairs predicted and clipped (the main setting)
- pure: MF predictions for every pair, not clipped
Same groups and candidates everywhere; m = 5 and 8, N = 20.

Usage: python scripts/diagnostics/mf_seed.py   (about 3 minutes)
Writes results/diagnostics/mf_seed.csv. See docs/replication_notes.md.
"""
import time, numpy as np, pandas as pd
from gfair import experiment
from gfair.config import DEFAULT_CONFIG, REPO_ROOT, load_config
from gfair.data import load_ratings, reindex
from gfair.groups import centered_ratings
from gfair.mf import train_mf, fill_missing

cfg = load_config(DEFAULT_CONFIG); mf = cfg["mf"]
ratings, uids, iids = reindex(load_ratings(REPO_ROOT / cfg["data"]["raw_dir"]))
C = centered_ratings(ratings, len(uids), len(iids))
main = np.load(REPO_ROOT / cfg["data"]["predictions_path"])
def ci(x): return 1.96 * x.std(ddof=1) / np.sqrt(len(x))
rows = []
for seed in ["main", 1, 2, 3, 4, 5]:
    t0 = time.perf_counter()
    for kind in ["kept", "pure"]:
        if seed == "main" and kind == "kept":
            M = main
        else:
            if kind == "kept" or seed == "main":
                rng = np.random.default_rng(cfg["seed"]).spawn(3)[2] if seed == "main" else np.random.default_rng(seed)
                raw = train_mf(ratings, len(uids), len(iids), rng=rng, n_factors=mf["n_factors"], n_epochs=mf["n_epochs"], reg=mf["reg"])
            M = fill_missing(raw, ratings, clip=tuple(mf["clip"])) if kind == "kept" else raw
        for gt in ["RND", "SIM"]:
            for m in [5, 8]:
                d = experiment.run_setting(M, C, "diag", gt, m, 20, cfg); d = d[d.metric == "ndcg@20"]
                w = d.pivot_table(index="group_id", columns="method", values="fairness")
                x = w["XPO"] - w["AVG"]
                rows.append(dict(seed=seed, matrix=kind, gt=gt, m=m, AVG=w["AVG"].mean(), LM=w["LM"].mean(), NPO=w["NPO"].mean(), XPO=w["XPO"].mean(), xpo_avg=x.mean(), ci=ci(x)))
    print(seed, round(time.perf_counter() - t0), "s", flush=True)
df = pd.DataFrame(rows)
out = REPO_ROOT / "results" / "diagnostics" / "mf_seed.csv"
out.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(out, index=False)
pd.set_option("display.width", 250)
print(df.round(3).sort_values(["matrix", "gt", "m"]).to_string(index=False))
print(df.groupby(["matrix", "gt", "m"])[["AVG", "LM", "NPO", "XPO", "xpo_avg"]].agg(["mean", "min", "max"]).round(3).to_string())
