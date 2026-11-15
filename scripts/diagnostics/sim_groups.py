"""A5 check: SIM groups grown by similarity to the whole group (the main setting)
vs by similarity to the seed user only (setting until 2026-11-15).

Same seed users and candidates in both variants. N = 20, all group sizes of E3.

Usage: python scripts/diagnostics/sim_groups.py   (about 1 minute)
Writes results/diagnostics/sim_groups.csv. See docs/replication_notes.md.
"""
import numpy as np, pandas as pd
from gfair import experiment
from gfair.config import DEFAULT_CONFIG, REPO_ROOT, load_config
from gfair.data import load_ratings, reindex
from gfair.groups import centered_ratings, sample_sim_group, user_similarity_to


def sample_sim_group_seed(centered, m, rng):
    """Random seed user plus the m - 1 users most similar to the seed user."""
    seed_user = int(rng.integers(centered.shape[0]))      # same draw as the main version
    sim = user_similarity_to(seed_user, centered)
    sim[seed_user] = -np.inf
    return np.concatenate(([seed_user], np.argsort(-sim, kind="stable")[: m - 1]))


cfg = load_config(DEFAULT_CONFIG)
P = np.load(REPO_ROOT / cfg["data"]["predictions_path"])
ratings, uids, iids = reindex(load_ratings(REPO_ROOT / cfg["data"]["raw_dir"]))
C = centered_ratings(ratings, len(uids), len(iids))


def pairwise(members):
    G = C[members] @ C[members].T
    return G[np.triu_indices(len(members), 1)].mean()


frames, coh = [], []
for m in cfg["experiments"]["E3"]["m"]:
    for name, fn in [("group", sample_sim_group), ("seed", sample_sim_group_seed)]:
        experiment.sample_sim_group = fn                    # run_setting looks the sampler up here
        df = experiment.run_setting(P, C, "A5diag", "SIM", m, 20, cfg)
        df["variant"] = name
        frames.append(df[df.metric == "ndcg@20"])
        sims, shared = [], 0
        for g in range(cfg["n_groups"]):
            a = sample_sim_group(C, m, experiment.group_rng(cfg["seed"], "SIM", m, 20, g))
            b = fn(C, m, experiment.group_rng(cfg["seed"], "SIM", m, 20, g))
            sims.append(pairwise(b)); shared += len(set(a) & set(b))
        coh.append(dict(m=m, variant=name, mean_pairwise_sim=np.mean(sims), members_shared_with_main=shared / cfg["n_groups"]))
    print("m =", m, flush=True)
experiment.sample_sim_group = sample_sim_group
res = pd.concat(frames)
out = REPO_ROOT / "results" / "diagnostics" / "sim_groups.csv"
out.parent.mkdir(parents=True, exist_ok=True)
res.to_csv(out, index=False)

pd.set_option("display.width", 250)
print(pd.DataFrame(coh).pivot(index="m", columns="variant").round(3).to_string())
print("fairness (nDCG@20)")
print(res.pivot_table(index=["method", "variant"], columns="m", values="fairness").round(3).to_string())
w = res.pivot_table(index=["variant", "m", "group_id"], columns="method", values="fairness")
x = (w["XPO"] - w["AVG"]).groupby(["variant", "m"]).agg(["mean", "sem"])
print("XPO minus AVG, mean"); print(x["mean"].round(3).unstack().to_string())
print("XPO minus AVG, 95% CI half-width"); print((1.96 * x["sem"]).round(3).unstack().to_string())
