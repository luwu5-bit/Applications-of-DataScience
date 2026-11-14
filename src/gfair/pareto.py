"""Rank matrix, dominance counts and the NPO / XPO candidate pools.

Conventions used across the package:
- `preds` has shape (m, n_items): (predicted) ratings of the group members for the
  candidates (rows = members, columns = candidates in ascending item id).
- `ranks` (R) has shape (n_items, m): R[i, u] = rank of item i for member u,
  1 = best. Row i is the item vector r(i) from the paper.
- Items are referred to by their position in the candidate array.
"""

import numpy as np


def rank_matrix(preds: np.ndarray) -> np.ndarray:
    """Per-member ranks of all candidates, 1 = best, ties broken by position.

    Input (m, n_items) ratings, output (n_items, m) integer ranks.
    """
    m, n = preds.shape
    # Stable sort: among equal ratings the lower position (= lower item id) wins.
    order = np.argsort(-preds, axis=1, kind="stable")
    ranks = np.empty((m, n), dtype=np.int64)
    ranks[np.arange(m)[:, None], order] = np.arange(1, n + 1)
    return ranks.T


def dom_counts(ranks: np.ndarray) -> np.ndarray:
    """Number of items that dominate each item.

    i dominates j if R[i, u] <= R[j, u] for all u and < for at least one u.
    Computed by broadcasting on the (n_items, m) rank matrix.
    """
    a, b = ranks[:, None, :], ranks[None, :, :]
    dominates = (a <= b).all(axis=2) & (a < b).any(axis=2)  # [i, j]: i dominates j
    return dominates.sum(axis=0)


def npo_pool(dom: np.ndarray, N: int) -> np.ndarray:
    """Indices of all items with dom_count <= N - 1 (N-level Pareto optimal)."""
    return np.flatnonzero(dom <= N - 1)


def xpo_pool(dom: np.ndarray, N: int) -> tuple[np.ndarray, int]:
    """Smallest level x in [1, N] whose pool has at least N items.

    Pool at level x = {i : dom_count(i) <= x - 1}. Found by binary search
    (pool size is monotone in x). Returns (pool indices, x).
    """
    lo, hi = 1, N
    while lo < hi:
        mid = (lo + hi) // 2
        if np.count_nonzero(dom <= mid - 1) >= N:
            hi = mid
        else:
            lo = mid + 1
    return np.flatnonzero(dom <= lo - 1), lo
