"""Average the results over MF fits and write summary tables (A15).

Usage: python scripts/summarize.py

Reads results/E1.csv, E2.csv, E3.csv, E5.csv (one row per fit, group, method,
metric) and writes small CSVs to results/summary/:

- settings.csv     mean per (exp, group type, m, N, S, method, metric) over
                   groups and fits, with a 95% CI over groups and the spread
                   between fits
- differences.csv  paired differences between methods (XPO - AVG etc.)
- e1_vs_paper.csv  E1, every metric, next to the paper's Tables 1 and 2
- convergence.csv  how the E1/E3 means move as fits are added

How the averaging works: for each group, a method's fairness (or group
utility) is first averaged over the K fits. The mean over the 100 groups of
these per-group averages is the reported value, and the 95% CI is computed
over the 100 per-group averages (1.96 * sd / sqrt(100)). Groups, candidates
and weight samples are the same in every fit; only the MF predictions, and so
the ground truth, differ. "fit_sd" is the standard deviation of the setting
mean between fits: how much a single fit would have moved the result.
"""

import numpy as np
import pandas as pd

from gfair.config import REPO_ROOT

RESULTS = REPO_ROOT / "results"
OUT = RESULTS / "summary"
EXPS = ["E1", "E2", "E3", "E5"]
SETTING = ["exp", "group_type", "m", "N", "n_samples_key"]
PAIRS = [("XPO", "AVG"), ("NPO", "AVG"), ("AWM", "AVG"), ("XPO", "NPO"), ("AWM", "LM"), ("XPO", "AWM"),
         ("BORDA", "AVG"), ("MUL", "AVG"), ("MED", "AVG"), ("MAX", "AVG")]
MEASURES = ["fairness", "group_utility"]


def ci(x: pd.Series) -> float:
    return 1.96 * x.std(ddof=1) / np.sqrt(len(x))


def load(exp: str) -> pd.DataFrame:
    df = pd.read_csv(RESULTS / f"{exp}.csv")
    if exp != "E5":
        df["n_samples_key"] = 0            # S is fixed outside E5
        return df
    # E5 varies S, which only NPO and XPO use. The other methods have no S and
    # their rows are identical in every S run: keep one copy and pair it with
    # every S, so that differences such as XPO - AVG can be formed per S.
    mc = df[df["n_samples"].notna()].copy()
    mc["n_samples_key"] = mc["n_samples"].astype(int)
    base = df[df["n_samples"].isna()].drop_duplicates(
        ["mf_fit", "group_type", "m", "N", "group_id", "method", "metric"])
    copies = [base.assign(n_samples_key=s) for s in sorted(mc["n_samples_key"].unique())]
    return pd.concat([mc, *copies], ignore_index=True)


def setting_table(df: pd.DataFrame) -> pd.DataFrame:
    keys = SETTING + ["method", "metric"]
    per_group = df.groupby(keys + ["group_id"])[MEASURES + ["pool_size", "xpo_level", "runtime_s"]].mean()
    per_fit = df.groupby(keys + ["mf_fit"])[MEASURES].mean()
    g = per_group.groupby(level=keys)
    out = g[MEASURES + ["pool_size", "xpo_level", "runtime_s"]].mean()
    for col in MEASURES:
        out[f"{col}_ci"] = g[col].agg(ci)
        out[f"{col}_fit_sd"] = per_fit.groupby(level=keys)[col].std(ddof=1)
    out["n_groups"] = g.size()
    out["n_fits"] = df.groupby(keys)["mf_fit"].nunique()
    return out.reset_index()


def difference_table(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    wide = df.pivot_table(index=SETTING + ["metric", "group_id", "mf_fit"], columns="method", values=MEASURES)
    for a, b in PAIRS:
        for col in MEASURES:
            if (col, a) not in wide or (col, b) not in wide:
                continue
            d = (wide[(col, a)] - wide[(col, b)]).rename("d").reset_index()
            keys = SETTING + ["metric"]
            for key, grp in d.groupby(keys):
                per_group = grp.groupby("group_id")["d"].mean()
                per_fit = grp.groupby("mf_fit")
                # Per fit: is the difference significant on that fit alone?
                fit_mean = per_fit["d"].mean()
                fit_ci = per_fit["d"].agg(ci)
                rows.append(dict(zip(keys, key)) | {
                    "pair": f"{a} - {b}", "measure": col,
                    "diff": per_group.mean(), "ci": ci(per_group),
                    "fit_min": fit_mean.min(), "fit_max": fit_mean.max(),
                    "fits_a_better": int((fit_mean - fit_ci > 0).sum()),
                    "fits_b_better": int((fit_mean + fit_ci < 0).sum()),
                    "n_fits": len(fit_mean),
                })
    return pd.DataFrame(rows)


def convergence_table(df: pd.DataFrame) -> pd.DataFrame:
    """Setting mean using only the first k fits, for k = 1..K."""
    rows = []
    keys = SETTING + ["method", "metric"]
    sub = df[df["metric"].isin(["ndcg@20", "p@20", "ap", "no_misery", "rating"])]
    per_fit = sub.groupby(keys + ["mf_fit"])[MEASURES].mean().reset_index()
    for k in range(1, per_fit["mf_fit"].max() + 2):
        part = per_fit[per_fit["mf_fit"] < k].groupby(keys)[MEASURES].mean().reset_index()
        part["k"] = k
        rows.append(part)
    return pd.concat(rows, ignore_index=True)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    frames = {exp: load(exp) for exp in EXPS if (RESULTS / f"{exp}.csv").exists()}

    settings = pd.concat([setting_table(df) for df in frames.values()], ignore_index=True)
    settings.to_csv(OUT / "settings.csv", index=False)

    diffs = pd.concat([difference_table(df) for df in frames.values()], ignore_index=True)
    diffs.to_csv(OUT / "differences.csv", index=False)

    conv = pd.concat([convergence_table(frames[e]) for e in ["E1", "E3"] if e in frames], ignore_index=True)
    conv.to_csv(OUT / "convergence.csv", index=False)

    if "E1" in frames:
        paper = pd.read_csv(REPO_ROOT / "docs" / "paper_tables.csv")
        e1 = settings[settings["exp"] == "E1"]
        merged = e1.merge(paper, on=["group_type", "method", "metric"], how="left", suffixes=("", "_paper"))
        cols = ["group_type", "method", "metric", "fairness", "fairness_ci", "fairness_paper",
                "group_utility", "group_utility_ci", "group_utility_paper"]
        merged[cols].to_csv(OUT / "e1_vs_paper.csv", index=False)

    # Short console overview of the primary metric.
    pd.set_option("display.width", 200)
    show = settings[(settings["metric"] == "ndcg@20") & (settings["exp"].isin(["E1", "E3"]))]
    print(show.pivot_table(index=["exp", "group_type", "m"], columns="method", values="fairness").round(3).to_string())
    for name in ["settings", "differences", "convergence", "e1_vs_paper"]:
        print(f"wrote results/summary/{name}.csv")


if __name__ == "__main__":
    main()
