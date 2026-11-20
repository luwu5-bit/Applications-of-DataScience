"""Read results/*.csv and write the report figures to figures/.

Usage: python scripts/make_figures.py

Figures are drawn for the primary metric nDCG@20, for nDCG@20 with linear
gain (A20, _lin), for P@20 (file names end in _p20) and for the rating-based no-misery share (A18, _nomisery). Every value is first averaged per group over the MF fits (A15);
error bars and bands are 95% confidence intervals over the 100 per-group
averages (1.96 * std / sqrt(n)), as in scripts/summarize.py.
"""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from gfair.config import REPO_ROOT

RESULTS = REPO_ROOT / "results"
FIGURES = REPO_ROOT / "figures"
METRICS = {
    "ndcg@20": ("nDCG@20", ""),
    "ndcg_lin@20": ("nDCG@20, linear gain", "_lin"),               # A20
    "p@20": ("P@20", "_p20"),
    "no_misery": ("share of list not disliked", "_nomisery"),   # extension, A18
}
PAPER_METRICS = ["ndcg@20", "ndcg_lin@20", "p@20"]   # metrics with a paper value to compare
# The paper reports one nDCG@20; its values do not fit the printed gain (see
# docs/replication_notes.md), so both of our nDCG variants are shown against it.
PAPER_REF = {"ndcg_lin@20": "ndcg@20"}

# Fixed colour and marker per method, so a method looks the same in every figure.
# Colours are colour-blind checked; the marker is a second cue for print.
METHODS = {
    "AVG": ("#2a78d6", "o"),
    "LM": ("#eb6834", "s"),
    "NPO": ("#1baf7a", "^"),
    "XPO": ("#eda100", "D"),
    "AWM": ("#8a5cd1", "v"),
}
# Shown in the E1 comparison only (in the line plots they would crowd out the
# main story); all of them are in results/summary/.
OTHER = {"MUL": "#7f8c8d", "MAX": "#a0522d", "BORDA": "#c2185b", "MED": "#00838f"}
REPLICATED = ["AVG", "LM", "MUL", "MAX", "BORDA", "MED", "NPO", "XPO"]    # methods in the paper's tables
GROUP_LABEL = {"RND": "Random groups (RND)", "SIM": "Similar groups (SIM)"}
INK, MUTED, GRID, SURFACE, PAPER_GREY = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb", "#b9b8b2"

# Paper Tables 1/2 (m = 5, N = 20), extracted from docs/paper.md.
PAPER = pd.read_csv(REPO_ROOT / "docs" / "paper_tables.csv").set_index(["group_type", "method", "metric"])

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "font.size": 10, "axes.titlesize": 11, "axes.titleweight": "bold", "axes.titlelocation": "left",
    "text.color": INK, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.edgecolor": GRID, "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "axes.grid.axis": "y", "grid.color": GRID, "grid.linewidth": 0.8,
    "axes.axisbelow": True, "lines.linewidth": 2, "lines.markersize": 6,
    "legend.frameon": False, "savefig.dpi": 200, "savefig.bbox": "tight",
})


def load(exp: str, metric: str) -> pd.DataFrame:
    """One row per (setting, group, method): values averaged over the MF fits."""
    df = pd.read_csv(RESULTS / f"{exp}.csv")
    df = df[df["metric"] == metric]
    keys = ["group_type", "m", "N", "n_samples", "group_id", "method"]
    cols = ["fairness", "group_utility", "pool_size", "xpo_level"]
    return df.groupby(keys, dropna=False)[cols].mean().reset_index()


def mean_ci(values: pd.Series) -> tuple[float, float]:
    return values.mean(), 1.96 * values.std() / np.sqrt(len(values))


def save(fig: plt.Figure, name: str) -> None:
    fig.savefig(FIGURES / name)
    plt.close(fig)
    print(f"wrote figures/{name}")


def m_axis(ax: plt.Axes, ms: list[int]) -> None:
    """Log-spaced group-size axis with the actual sizes as tick labels."""
    ax.set_xscale("log")
    ax.set_xticks(ms, [str(m) for m in ms])
    ax.minorticks_off()
    ax.set_xlabel("Group size m")


def fig_e1_vs_paper(metric: str) -> None:
    """E1: our fairness and group utility next to the paper's values."""
    label, suffix = METRICS[metric]
    df = load("E1", metric)
    fig, axes = plt.subplots(2, 2, figsize=(12, 6.5), sharey="row")
    for row, (col, title) in enumerate([("fairness", "Fairness"), ("group_utility", "Group utility")]):
        for c, gt in enumerate(["RND", "SIM"]):
            ax = axes[row, c]
            x = np.arange(len(REPLICATED))
            for k, method in enumerate(REPLICATED):
                mean, ci = mean_ci(df[(df.group_type == gt) & (df.method == method)][col])
                ax.bar(k - 0.19, mean, 0.36, color=METHODS.get(method, (OTHER.get(method),))[0], yerr=ci,
                       error_kw={"ecolor": INK, "elinewidth": 1, "capsize": 2})
                paper = PAPER.loc[(gt, method, PAPER_REF.get(metric, metric)), col]
                ax.bar(k + 0.19, paper, 0.36, color=PAPER_GREY)
                ax.text(k - 0.19, mean + ci + 0.01, f"{mean:.2f}", ha="center", va="bottom", fontsize=6.5)
                ax.text(k + 0.19, paper + 0.01, f"{paper:.2f}", ha="center", va="bottom", fontsize=6.5, color=MUTED)
            ax.set_xticks(x, REPLICATED, fontsize=8)
            ax.set_title(f"{title}, {GROUP_LABEL[gt]}")
            ax.set_ylim(0, 0.8)
        axes[row, 0].set_ylabel(label)
    # A caption instead of a legend: "ours" has four colours, so one swatch would mislead.
    fig.text(0.5, -0.02, "Coloured bars: ours, mean of 100 groups averaged over the MF fits, with 95% CI.   "
             "Grey bars: paper (Sacharidis 2019, Tables 1 and 2).", ha="center", color=MUTED, fontsize=9)
    fig.suptitle(f"E1: replication vs paper (m = 5, N = 20, {label})", x=0.02, ha="left", fontweight="bold")
    fig.tight_layout()
    save(fig, f"e1_vs_paper{suffix}.png")


def fig_vs_group_size(col: str, metric: str) -> None:
    """E3: one line per method against group size, RND and SIM side by side."""
    label, suffix = METRICS[metric]
    ylabel = f"{'Fairness' if col == 'fairness' else 'Group utility'} ({label})"
    name = f"{col}_vs_group_size{suffix}.png"
    df = load("E3", metric)
    ms = sorted(df.m.unique())
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.8), sharey=True)
    for ax, gt in zip(axes, ["RND", "SIM"]):
        for method, (color, marker) in METHODS.items():
            stats = [mean_ci(df[(df.group_type == gt) & (df.method == method) & (df.m == m)][col]) for m in ms]
            mean, ci = np.array(stats).T
            ax.fill_between(ms, mean - ci, mean + ci, color=color, alpha=0.15, linewidth=0)
            ax.plot(ms, mean, color=color, marker=marker, label=method,
                    markeredgecolor=SURFACE, markeredgewidth=1)
        # The paper covers m = 2..8: shaded band ending exactly at m = 8.
        ax.set_xlim(1.75, 34)
        ax.axvspan(1.75, 8, color=GRID, alpha=0.45, linewidth=0)
        # y in axes coordinates, so the labels stay at the top whatever the data range is.
        tr = ax.get_xaxis_transform()
        ax.text(7.7, 0.97, "paper: m = 2 to 8", color=MUTED, fontsize=8, va="top", ha="right", transform=tr)
        ax.text(8.6, 0.97, "our extension: m = 10 to 30", color=MUTED, fontsize=8, va="top", transform=tr)
        m_axis(ax, ms)
        ax.set_title(GROUP_LABEL[gt])
    axes[0].set_ylim(0, df[col].groupby([df.group_type, df.method, df.m]).mean().max() * 1.25)
    axes[0].set_ylabel(ylabel)
    fig.tight_layout()
    # Outside the plot area: inside it would cover lines in one of the two figures.
    fig.legend(*axes[1].get_legend_handles_labels(), title="Method",
               loc="center left", bbox_to_anchor=(1.0, 0.55))
    save(fig, name)


def fig_difference(a: str, b: str, metric: str) -> None:
    """E3: paired fairness difference a - b per group, with 95% CI."""
    label, suffix = METRICS[metric]
    df = load("E3", metric)
    ms = sorted(df.m.unique())
    fig, ax = plt.subplots(figsize=(6.5, 3.8))
    for gt, color, marker, shift in [("RND", "#2a78d6", "o", 0.97), ("SIM", "#eb6834", "s", 1.03)]:
        stats = []
        for m in ms:
            wide = df[(df.group_type == gt) & (df.m == m)].pivot(index="group_id", columns="method", values="fairness")
            stats.append(mean_ci(wide[a] - wide[b]))
        mean, ci = np.array(stats).T
        # Small horizontal shift so the two error bars do not overlap.
        ax.errorbar(np.array(ms) * shift, mean, yerr=ci, color=color, marker=marker, capsize=3,
                    linewidth=1.5, label=GROUP_LABEL[gt], markeredgecolor=SURFACE, markeredgewidth=1)
    ax.axhline(0, color=INK, linewidth=1)
    lo, hi = ax.get_ylim()
    lim = max(abs(lo), abs(hi), 0.03) * 1.15
    ax.set_ylim(-lim, lim)
    ax.text(0.02, 0.95, f"{a} fairer", color=MUTED, fontsize=8, va="top", transform=ax.transAxes)
    ax.text(0.02, 0.05, f"{b} fairer", color=MUTED, fontsize=8, va="bottom", transform=ax.transAxes)
    m_axis(ax, ms)
    ax.set_ylabel(f"Fairness difference ({label})")
    ax.set_title(f"{a} minus {b}, paired per group (95% CI)")
    ax.legend(loc="upper right")
    fig.tight_layout()
    save(fig, f"{a.lower()}_minus_{b.lower()}_vs_group_size{suffix}.png")


def fig_xpo_lead_by_metric() -> None:
    """E3: XPO - AVG fairness by group size under four metrics, RND and SIM side by side.

    The report's main figure: the metrics that count how much of each member's
    top 20 reaches the list (linear nDCG, P@20, AP) agree; the printed gain 2^rel
    is drawn as a grey dashed reference.
    """
    series = [  # metric, label, colour, marker, linestyle
        ("ndcg_lin@20", "nDCG@20, linear gain", "#2a78d6", "o", "-"),
        ("p@20", "P@20", "#eb6834", "s", "-"),
        ("ap", "AP", "#1baf7a", "^", "-"),
        ("ndcg@20", "nDCG@20, gain $2^{rel}$ (as printed)", MUTED, "x", "--"),
    ]
    data = {metric: load("E3", metric) for metric, *_ in series}
    ms = sorted(data["p@20"].m.unique())
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.9), sharey=True)
    for ax, gt in zip(axes, ["RND", "SIM"]):
        for metric, label, color, marker, ls in series:
            df = data[metric]
            stats = []
            for m in ms:
                wide = df[(df.group_type == gt) & (df.m == m)].pivot(index="group_id", columns="method", values="fairness")
                stats.append(mean_ci(wide["XPO"] - wide["AVG"]))
            mean, ci = np.array(stats).T
            ax.fill_between(ms, mean - ci, mean + ci, color=color, alpha=0.12, linewidth=0)
            ax.plot(ms, mean, ls, color=color, marker=marker, label=label,
                    markeredgecolor=color if marker == "x" else SURFACE, markeredgewidth=1 if marker != "x" else 1.5)
        ax.axhline(0, color=INK, linewidth=1)
        ax.axvspan(1.8, 8.5, color=GRID, alpha=0.35, linewidth=0)
        ax.text(2.0, 0.088, "paper's range (m = 2 to 8)", color=MUTED, fontsize=8, va="top")
        ax.text(0.98, 0.04, "AVG fairer", color=MUTED, fontsize=8, ha="right", transform=ax.transAxes)
        m_axis(ax, ms)
        ax.set_title(GROUP_LABEL[gt])
        ax.set_ylim(-0.06, 0.09)
    axes[0].set_ylabel("Fairness XPO minus AVG")
    axes[1].legend(loc="upper right", fontsize=8, frameon=False)
    fig.text(0.5, -0.02, "Paired per group; mean of 100 groups, each averaged over 20 MF fits; bands: 95% CI over groups.",
             ha="center", color=MUTED, fontsize=8.5)
    fig.tight_layout()
    save(fig, "xpo_lead_by_metric.png")


def fig_pool_size() -> None:
    """E3: candidate pool size of NPO and XPO, misery-free items of AWM, and the XPO level x."""
    df = load("E3", "ndcg@20")
    ms = sorted(df.m.unique())
    fig, (ax_pool, ax_x) = plt.subplots(1, 2, figsize=(9, 3.8))
    for gt, style, fill in [("RND", "-", True), ("SIM", "--", False)]:
        for method in ["NPO", "XPO", "AWM"]:
            color, marker = METHODS[method]
            d = df[(df.group_type == gt) & (df.method == method)]
            ax_pool.plot(ms, d.groupby("m").pool_size.mean(), style, color=color, marker=marker,
                         markerfacecolor=color if fill else SURFACE, label=f"{method}, {gt}")
        d = df[(df.group_type == gt) & (df.method == "XPO")]
        ax_x.plot(ms, d.groupby("m").xpo_level.mean(), style, color=METHODS["XPO"][0], marker="D",
                  markerfacecolor=METHODS["XPO"][0] if fill else SURFACE, label=f"XPO, {gt}")
    ax_pool.axhline(200, color=MUTED, linewidth=0.8, linestyle=":")
    ax_pool.text(2, 193, "all 200 candidates", color=MUTED, fontsize=8, va="top")
    ax_pool.axhline(20, color=MUTED, linewidth=0.8, linestyle=":")
    ax_pool.text(30, 13, "N = 20", color=MUTED, fontsize=8, va="top", ha="right")
    ax_pool.set_ylim(0, 210)
    ax_pool.set_ylabel("Mean pool size (items)")
    ax_pool.set_title("Candidate pool size (AWM: misery-free items)")
    ax_pool.legend(loc="upper left", fontsize=7.5, bbox_to_anchor=(0.0, 0.9), ncol=2)
    ax_x.axhline(1, color=MUTED, linewidth=0.8, linestyle=":")
    ax_x.text(2, 0.85, "x = 1: plain Pareto-optimal set, cannot go lower", color=MUTED, fontsize=8, va="top")
    ax_x.set_ylim(0, 10)
    ax_x.set_ylabel("Mean XPO level x")
    ax_x.set_title("XPO level")
    ax_x.legend(loc="upper right", fontsize=8)
    for ax in (ax_pool, ax_x):
        m_axis(ax, ms)
    fig.tight_layout()
    save(fig, "pool_size_vs_group_size.png")


def fig_mc_sensitivity() -> None:
    """E5: how much a group's fairness moves when S changes (reference: largest S)."""
    # Not averaged over fits first: the change caused by S is measured per fit
    # and group, then averaged.
    df = pd.read_csv(RESULTS / "E5.csv")
    df = df[(df.metric == "ndcg@20") & df.method.isin(["NPO", "XPO"])]
    s_values = sorted(df.n_samples.unique())
    fig, ax = plt.subplots(figsize=(6.5, 3.8))
    for m, style, fill in [(5, "-", True), (20, "--", False)]:
        for method in ["NPO", "XPO"]:
            color, marker = METHODS[method]
            wide = df[(df.m == m) & (df.method == method)].pivot(index=["mf_fit", "group_id"], columns="n_samples", values="fairness")
            dev = wide.sub(wide[s_values[-1]], axis=0).abs().mean()
            ax.plot(s_values[:-1], dev[s_values[:-1]], style, color=color, marker=marker,
                    markerfacecolor=color if fill else SURFACE, label=f"{method}, m = {m}")
    ax.set_xscale("log")
    ax.set_xticks(s_values[:-1], [f"{int(s):,}" for s in s_values[:-1]])
    ax.minorticks_off()
    ax.set_ylim(0, 0.005)
    ax.set_xlabel("Monte Carlo samples S")
    ax.set_ylabel("Mean |change| in group fairness")
    ax.set_title(f"Monte Carlo sensitivity (vs S = {int(s_values[-1]):,}, RND, nDCG@20)")
    ax.legend(fontsize=8)
    fig.tight_layout()
    save(fig, "mc_sensitivity.png")


def main() -> None:
    FIGURES.mkdir(exist_ok=True)
    for metric in METRICS:
        if metric in PAPER_METRICS:
            fig_e1_vs_paper(metric)
        fig_vs_group_size("fairness", metric)
        fig_vs_group_size("group_utility", metric)
        fig_difference("XPO", "AVG", metric)
        fig_difference("AWM", "AVG", metric)
    fig_xpo_lead_by_metric()
    fig_pool_size()
    fig_mc_sensitivity()


if __name__ == "__main__":
    main()
