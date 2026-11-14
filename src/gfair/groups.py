"""Group sampling (RND, SIM) and candidate sampling."""

import numpy as np
import pandas as pd


def sample_rnd_group(n_users: int, m: int, rng: np.random.Generator) -> np.ndarray:
    """m user indices, uniform without replacement (ASSUMPTIONS.md, A6)."""
    return rng.choice(n_users, size=m, replace=False)


def centered_ratings(ratings: pd.DataFrame, n_users: int, n_items: int) -> np.ndarray:
    """Observed ratings minus each user's mean rating, 0 where unrated.

    `ratings` needs the columns u, i, rating (see data.reindex). Each row is
    scaled to unit length, so a dot product of two rows is their mean-centered
    cosine similarity. Shape (n_users, n_items), float32 to halve the memory.
    """
    u = ratings["u"].to_numpy()
    r = ratings["rating"].to_numpy(dtype=float)
    user_mean = np.bincount(u, weights=r, minlength=n_users) / np.maximum(
        np.bincount(u, minlength=n_users), 1
    )
    C = np.zeros((n_users, n_items), dtype=np.float32)
    C[u, ratings["i"].to_numpy()] = r - user_mean[u]
    norms = np.linalg.norm(C, axis=1, keepdims=True)
    # A user who gave every movie the same rating has a zero vector: similarity 0.
    return C / np.where(norms == 0, 1, norms)


def user_similarity_to(seed_user: int, centered: np.ndarray) -> np.ndarray:
    """Mean-centered cosine similarity of every user to the seed user.

    `centered` comes from `centered_ratings`. The cosine runs over the full
    item vectors (unrated = 0), not only over co-rated movies (A12).
    """
    return centered @ centered[seed_user]


def sample_sim_group(
    centered: np.ndarray, m: int, rng: np.random.Generator
) -> np.ndarray:
    """Random seed user plus the m - 1 users most similar to the seed (A5).

    The seed user is first in the returned array, then by decreasing similarity.
    """
    seed_user = int(rng.integers(centered.shape[0]))
    sim = user_similarity_to(seed_user, centered)
    sim[seed_user] = -np.inf                                    # never pick the seed twice
    others = np.argsort(-sim, kind="stable")[: m - 1]
    return np.concatenate(([seed_user], others))


def sample_candidates(
    n_items: int, n_candidates: int, rng: np.random.Generator
) -> np.ndarray:
    """n_candidates item indices, uniform without replacement, sorted ascending.

    Sorted so that "ties broken by item id" equals "ties broken by position".
    """
    return np.sort(rng.choice(n_items, size=n_candidates, replace=False))
