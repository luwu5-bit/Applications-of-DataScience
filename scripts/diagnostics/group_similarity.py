"""How similar are SIM groups compared with RND groups?

For the same groups as in the experiments (same seeds, fit 0), per group size:
- mean pairwise mean-centered cosine similarity of the members (A5, A12),
  plus the same for the users' overall average as a reference
- number of movies a pair of members has both rated
- overlap of the members' ground-truth top-20 lists (mean pairwise share of
  shared items, out of 20)
- share of the candidate items that are Pareto optimal (level 1)

Usage: python scripts/diagnostics/group_similarity.py   (a few minutes)
Writes results/diagnostics/group_similarity.csv.
"""
import numpy as np, pandas as pd
from gfair.config import DEFAULT_CONFIG, REPO_ROOT, load_config
from gfair.data import load_ratings, reindex
from gfair.experiment import group_rng
from gfair.groups import centered_ratings, sample_candidates, sample_rnd_group, sample_sim_group
from gfair.pareto import dom_counts, rank_matrix

cfg = load_config(DEFAULT_CONFIG)
N = 20
P = np.load(REPO_ROOT / cfg["data"]["predictions_path"])
ratings, uids, iids = reindex(load_ratings(REPO_ROOT / cfg["data"]["raw_dir"]))
C = centered_ratings(ratings, len(uids), len(iids))
R = np.zeros(C.shape, dtype=bool)
R[ratings["u"].to_numpy(), ratings["i"].to_numpy()] = True

rng0 = np.random.default_rng(0)
sample = rng0.choice(len(uids), 2000, replace=False)
G = C[sample] @ C[sample].T
all_pairs = G[np.triu_indices(len(sample), 1)]
print(f"all user pairs (2000 random users): mean sim {all_pairs.mean():.3f}, "
      f"99th pct {np.percentile(all_pairs, 99):.3f}")

rows = []
for gt in ["RND", "SIM"]:
    for m in cfg["experiments"]["E3"]["m"]:
        for g in range(cfg["n_groups"]):
            rng = group_rng(cfg["seed"], gt, m, N, g)
            mem = sample_rnd_group(len(uids), m, rng) if gt == "RND" else sample_sim_group(C, m, rng)
            cand = sample_candidates(len(iids), cfg["n_candidates"], rng)
            iu = np.triu_indices(m, 1)
            sim = (C[mem] @ C[mem].T)[iu]
            co = (R[mem].astype(np.int32) @ R[mem].T.astype(np.int32))[iu]
            preds = P[np.ix_(mem, cand)]
            truth = np.argsort(-preds, axis=1, kind="stable")[:, :N]
            T = np.zeros((m, len(cand)), dtype=np.int32)
            T[np.arange(m)[:, None], truth] = 1
            overlap = (T @ T.T)[iu] / N
            pareto = (dom_counts(rank_matrix(preds)) == 0).mean()
            rows.append(dict(group_type=gt, m=m, group_id=g, mean_sim=sim.mean(), min_sim=sim.min(),
                             co_rated=np.median(co), top20_overlap=overlap.mean(),
                             n_ratings=R[mem].sum(axis=1).mean(), pareto_share=pareto))
        print(gt, m, flush=True)

df = pd.DataFrame(rows)
out = REPO_ROOT / "results" / "diagnostics" / "group_similarity.csv"
df.to_csv(out, index=False)
pd.set_option("display.width", 200)
print(df.groupby(["group_type", "m"]).mean(numeric_only=True).drop(columns="group_id").round(3).to_string())
print("wrote", out)
