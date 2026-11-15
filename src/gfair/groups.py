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
    """Random seed user, then grow the group one user at a time (A5).

    Each step adds the user with the highest mean similarity to all members so
    far (the paper: "adding the most similar user to the group"). Ties go to
    the lower user index. Members are returned in the order they were added.
    """
    seed_user = int(rng.integers(centered.shape[0]))
    members = [seed_user]
    taken = np.zeros(centered.shape[0], dtype=bool)
    taken[seed_user] = True
    # Sum of similarities to the current members; same argmax as the mean.
    total = user_similarity_to(seed_user, centered).astype(np.float64)
    while len(members) < m:
        nxt = int(np.argmax(np.where(taken, -np.inf, total)))
        members.append(nxt)
        taken[nxt] = True
        total += user_similarity_to(nxt, centered)
    return np.array(members)


def sample_candidates(
    n_items: int, n_candidates: int, rng: np.random.Generator
) -> np.ndarray:
    """n_candidates item indices, uniform without replacement, sorted ascending.

    Sorted so that "ties broken by item id" equals "ties broken by position".
    """
    return np.sort(rng.choice(n_items, size=n_candidates, replace=False))
