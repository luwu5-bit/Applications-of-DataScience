"""Member utility metrics, fairness and group utility.

`sigma` is the group list, `sigma_u` the member's ground-truth list; both are
arrays of item positions, best first. N = len(sigma_u). Definitions follow
Section 4.1 of the paper (docs/paper.md).
"""

import numpy as np


def ndcg_at_k(sigma: np.ndarray, sigma_u: np.ndarray, k: int) -> float:
    """nDCG@k with Borda relevance.

    The ground-truth item at position p (1-based) has relevance N - p + 1, any
    other item 0. Gain is 2^rel as printed in the paper, so an item outside
    the ground truth still earns 2^0 = 1 (negligible at N = 20, see
    ASSUMPTIONS.md A11), discount log2(pos + 1), normalized by the ideal DCG@k.
    """
    N = len(sigma_u)
    top = np.asarray(sigma)[:k]
    hit = top[:, None] == np.asarray(sigma_u)[None, :]          # (k, N)
    rel = (hit * (N - np.arange(N))).sum(axis=1)                # 0 if not in sigma_u
    ideal = np.clip(N - np.arange(k), 0, None)                  # N, N-1, ...
    dcg = ((2.0 ** rel) / np.log2(np.arange(len(top)) + 2)).sum()
    idcg = ((2.0 ** ideal) / np.log2(np.arange(k) + 2)).sum()
    return float(dcg / idcg)


def precision_at_k(sigma: np.ndarray, sigma_u: np.ndarray, k: int) -> float:
    """|sigma[1:k] ∩ sigma_u| / k."""
    return float(np.isin(np.asarray(sigma)[:k], sigma_u).sum() / k)


def average_precision(sigma: np.ndarray, sigma_u: np.ndarray) -> float:
    """Sum over k of P@k * [sigma[k] in sigma_u], divided by N."""
    hit = np.isin(sigma, sigma_u)
    p_at_k = np.cumsum(hit) / np.arange(1, len(hit) + 1)
    return float((p_at_k * hit).sum() / len(sigma_u))


def kendall_tau(sigma: np.ndarray, sigma_u: np.ndarray) -> float:
    """Kendall's tau over the union of both lists.

    An item missing from a list is placed at that list's last rank, so all
    missing items are tied there. A pair tied in either list is neither
    concordant nor discordant. tau = (concordant - discordant) / all pairs.
    """
    sigma, sigma_u = np.asarray(sigma), np.asarray(sigma_u)
    items = np.union1d(sigma, sigma_u)

    def positions(lst: np.ndarray) -> np.ndarray:
        pos = np.full(len(items), len(lst))                     # missing -> last rank
        pos[np.searchsorted(items, lst)] = np.arange(len(lst))
        return pos

    a, b = positions(sigma), positions(sigma_u)
    i, j = np.triu_indices(len(items), k=1)
    return float((np.sign(a[i] - a[j]) * np.sign(b[i] - b[j])).sum() / len(i))


# The two metrics below are our extension (A18). They use the member's ratings
# of the listed items, not the ground-truth list: an item outside the member's
# top N counts the same for nDCG, P@k, AP and tau whether the member rates it
# 4.5 or 1, so those metrics cannot see whether a list contains items a member
# dislikes. Both are "higher is better", so fairness (min) and group utility
# (mean) apply unchanged.


def no_misery_share(sigma: np.ndarray, member_ratings: np.ndarray, threshold: float) -> float:
    """Share of the group list the member rates at or above `threshold`.

    `member_ratings` holds the member's (filled) ratings of all candidates,
    indexed by item position. 1 = nothing in the list the member dislikes.
    """
    return float((np.asarray(member_ratings)[sigma] >= threshold).mean())


def mean_rating(sigma: np.ndarray, member_ratings: np.ndarray) -> float:
    """The member's mean (filled) rating of the items in the group list, 1 to 5."""
    return float(np.asarray(member_ratings)[sigma].mean())


def fairness(member_utilities: np.ndarray) -> float:
    """Minimum member utility."""
    return float(np.min(member_utilities))


def group_utility(member_utilities: np.ndarray) -> float:
    """Mean member utility."""
    return float(np.mean(member_utilities))
