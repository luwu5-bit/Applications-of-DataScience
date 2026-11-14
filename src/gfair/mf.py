"""Matrix factorization: train once, save the full predicted rating matrix.

Model (ASSUMPTIONS.md, A3): biased explicit-rating MF,
    r_hat(u, i) = mu + b_u + b_i + p_u . q_i

Trained with alternating least squares (ALS): with the item side fixed, the best
(b_u, p_u) of each user is the solution of a small ridge regression, and vice
versa. We use ALS instead of SGD because it has no learning rate to tune and
every update is an exact numpy solve, so it is fast without a Python loop over
the 1M ratings.
"""

import numpy as np
import pandas as pd


def train_test_split(
    ratings: pd.DataFrame, test_fraction: float, rng: np.random.Generator
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Random hold-out split, used only for the RMSE sanity check."""
    perm = rng.permutation(len(ratings))
    n_test = int(round(test_fraction * len(ratings)))
    return ratings.iloc[perm[n_test:]], ratings.iloc[perm[:n_test]]


def _update_side(
    rows: np.ndarray,
    cols: np.ndarray,
    targets: np.ndarray,
    n_rows: int,
    other_bias: np.ndarray,
    other_factors: np.ndarray,
    reg: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Exact ridge update of (bias, factors) for every row entity.

    `rows` are the entities being updated (e.g. users), `cols` the fixed side
    (e.g. items), `targets` = rating - mu. For one entity with n ratings:
        minimize sum (target - b_other - b - p . q)^2 + reg * n * (b^2 + |p|^2)
    Scaling the penalty by n (ALS-WR, Zhou et al. 2008) keeps the amount of
    regularization comparable between entities with few and many ratings.
    Entities without ratings keep bias 0 and a zero vector.
    """
    k = other_factors.shape[1]
    bias = np.zeros(n_rows)
    factors = np.zeros((n_rows, k))

    order = np.argsort(rows, kind="stable")
    rows, cols, targets = rows[order], cols[order], targets[order]
    bounds = np.searchsorted(rows, np.arange(n_rows + 1))
    eye = np.eye(k + 1)

    for a in range(n_rows):
        lo, hi = bounds[a], bounds[a + 1]
        n = hi - lo
        if n == 0:
            continue
        c = cols[lo:hi]
        # Design matrix [1, q]: the first coefficient is the bias.
        X = np.hstack([np.ones((n, 1)), other_factors[c]])
        y = targets[lo:hi] - other_bias[c]
        coef = np.linalg.solve(X.T @ X + reg * n * eye, X.T @ y)
        bias[a], factors[a] = coef[0], coef[1:]
    return bias, factors


def train_mf(
    ratings: pd.DataFrame,
    n_users: int,
    n_items: int,
    n_factors: int,
    n_epochs: int,
    reg: float,
    rng: np.random.Generator,
) -> np.ndarray:
    """Train biased MF with ALS and return the full prediction matrix.

    `ratings` needs the columns u, i (0-based indices, see data.reindex) and
    rating. Returns an array of shape (n_users, n_items) with the raw model
    output; clipping to the rating scale happens in `fill_missing`.
    """
    u = ratings["u"].to_numpy()
    i = ratings["i"].to_numpy()
    r = ratings["rating"].to_numpy(dtype=float)
    mu = r.mean()
    targets = r - mu

    b_i = np.zeros(n_items)
    Q = rng.normal(0.0, 0.1, size=(n_items, n_factors))
    for _ in range(n_epochs):
        b_u, P = _update_side(u, i, targets, n_users, b_i, Q, reg)
        b_i, Q = _update_side(i, u, targets, n_items, b_u, P, reg)

    return mu + b_u[:, None] + b_i[None, :] + P @ Q.T


def fill_missing(
    predictions: np.ndarray,
    ratings: pd.DataFrame,
    clip: tuple[float, float] = (1.0, 5.0),
) -> np.ndarray:
    """Rating matrix for the experiments: observed ratings kept, rest predicted.

    Follows the paper's wording that MF "fills in the missing ratings"
    (ASSUMPTIONS.md, A9). Predictions are clipped to the rating scale first, so
    every filled-in value is a valid rating and no prediction can outrank a
    real 5. Returns a new array; `predictions` is not modified.
    """
    filled = np.clip(predictions, *clip)
    filled[ratings["u"].to_numpy(), ratings["i"].to_numpy()] = ratings["rating"].to_numpy()
    return filled


def rmse(predictions: np.ndarray, ratings: pd.DataFrame) -> float:
    """RMSE of the prediction matrix on the given (u, i, rating) rows."""
    pred = predictions[ratings["u"].to_numpy(), ratings["i"].to_numpy()]
    return float(np.sqrt(np.mean((pred - ratings["rating"].to_numpy()) ** 2)))
