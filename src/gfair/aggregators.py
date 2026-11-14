"""Group recommenders: baselines (AVG, LM) and the Pareto methods (NPO, XPO).

Every recommender returns the group list sigma: an array of N item positions
(into the candidate array), best first. See pareto.py for shape conventions.
"""

import numpy as np

from gfair.pareto import dom_counts, npo_pool, xpo_pool


def avg(preds: np.ndarray, N: int) -> np.ndarray:
    """Top-N by mean rating over members (ties: lower position first)."""
    return np.argsort(-preds.mean(axis=0), kind="stable")[:N]


def lm(preds: np.ndarray, N: int) -> np.ndarray:
    """Least misery: top-N by minimum rating over members."""
    return np.argsort(-preds.min(axis=0), kind="stable")[:N]


def monte_carlo_counts(
    ranks: np.ndarray,
    N: int,
    n_samples: int,
    rng: np.random.Generator,
    batch_size: int = 1000,
) -> np.ndarray:
    """How often each item lands in the top N under random linear weights.

    Draw w ~ Dirichlet(1, ..., 1) (A1), score(i) = sum_u w_u * R[i, u] (lower is
    better), +1 for every item in the top N. Vectorized: scores = W @ R.T per
    batch, then argpartition. Returns counts of shape (n_items,).
    """
    n_items, m = ranks.shape
    if n_items <= N:
        # Every item is in the top N of every strategy; no sampling needed.
        return np.full(n_items, n_samples, dtype=np.int64)

    R_T = ranks.T.astype(float)
    counts = np.zeros(n_items, dtype=np.int64)
    done = 0
    while done < n_samples:
        b = min(batch_size, n_samples - done)
        W = rng.dirichlet(np.ones(m), size=b)                    # (b, m)
        scores = W @ R_T                                         # (b, n_items)
        top = np.argpartition(scores, N - 1, axis=1)[:, :N]
        counts += np.bincount(top.ravel(), minlength=n_items)
        done += b
    return counts


def rank_by_counts(counts: np.ndarray, pool_ranks: np.ndarray, N: int) -> np.ndarray:
    """Order pool items by count (descending) and return the best N positions
    within the pool.

    The paper does not say how equal counts are ordered. We break ties by the
    lower mean rank over members (the equal-weights strategy, i.e. the centre
    of the weight simplex), then by position (A13). This matters most when the
    pool has exactly N items: then every count equals S.
    """
    mean_rank = pool_ranks.mean(axis=1)
    # lexsort: last key is the primary one.
    order = np.lexsort((np.arange(len(counts)), mean_rank, -counts))
    return order[:N]


def _pareto_recommend(
    ranks: np.ndarray, pool: np.ndarray, N: int, n_samples: int,
    rng: np.random.Generator, batch_size: int,
) -> np.ndarray:
    pool_ranks = ranks[pool]
    counts = monte_carlo_counts(pool_ranks, N, n_samples, rng, batch_size)
    return pool[rank_by_counts(counts, pool_ranks, N)]


def npo(
    ranks: np.ndarray, N: int, n_samples: int, rng: np.random.Generator,
    batch_size: int = 1000,
) -> tuple[np.ndarray, dict]:
    """NPO: Monte Carlo scoring over the N-level Pareto pool.

    Returns (sigma, info) with info = {"pool_size": int}.
    """
    pool = npo_pool(dom_counts(ranks), N)
    sigma = _pareto_recommend(ranks, pool, N, n_samples, rng, batch_size)
    return sigma, {"pool_size": len(pool)}


def xpo(
    ranks: np.ndarray, N: int, n_samples: int, rng: np.random.Generator,
    batch_size: int = 1000,
) -> tuple[np.ndarray, dict]:
    """XPO: Monte Carlo scoring over the smallest x-level pool with >= N items.

    Returns (sigma, info) with info = {"pool_size": int, "x": int}.
    """
    pool, x = xpo_pool(dom_counts(ranks), N)
    sigma = _pareto_recommend(ranks, pool, N, n_samples, rng, batch_size)
    return sigma, {"pool_size": len(pool), "x": x}
