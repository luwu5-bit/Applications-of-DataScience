import numpy as np
import pandas as pd

from gfair.data import reindex
from gfair.mf import fill_missing, rmse, train_mf, train_test_split


def _synthetic(rng, n_users=60, n_items=40, k=3, density=0.5):
    """Ratings generated exactly by the biased MF model, partly observed."""
    truth = (
        3.5
        + rng.normal(0, 0.5, (n_users, 1))
        + rng.normal(0, 0.5, (1, n_items))
        + rng.normal(0, 0.7, (n_users, k)) @ rng.normal(0, 0.7, (n_items, k)).T
    )
    u, i = np.nonzero(rng.random((n_users, n_items)) < density)
    return pd.DataFrame({"u": u, "i": i, "rating": truth[u, i]})


def test_mf_recovers_low_rank_ratings():
    rng = np.random.default_rng(0)
    ratings = _synthetic(rng)
    train, test = train_test_split(ratings, 0.2, rng)
    pred = train_mf(train, 60, 40, n_factors=3, n_epochs=30, reg=0.001, rng=rng)
    assert pred.shape == (60, 40)
    assert rmse(pred, train) < 0.1
    # Far better than predicting the global mean for unseen ratings.
    baseline = float(np.sqrt(np.mean((test["rating"] - train["rating"].mean()) ** 2)))
    assert rmse(pred, test) < 0.5 * baseline


def test_mf_is_deterministic_given_seed():
    ratings = _synthetic(np.random.default_rng(1))
    kwargs = dict(n_users=60, n_items=40, n_factors=3, n_epochs=3, reg=0.05)
    a = train_mf(ratings, rng=np.random.default_rng(7), **kwargs)
    b = train_mf(ratings, rng=np.random.default_rng(7), **kwargs)
    assert np.array_equal(a, b)


def test_split_is_a_partition():
    ratings = _synthetic(np.random.default_rng(2))
    train, test = train_test_split(ratings, 0.25, np.random.default_rng(3))
    assert len(test) == round(0.25 * len(ratings))
    assert sorted(train.index.tolist() + test.index.tolist()) == ratings.index.tolist()


def test_reindex_is_contiguous_and_ordered_by_id():
    raw = pd.DataFrame({"user_id": [10, 3, 10], "item_id": [7, 7, 2], "rating": [5, 4, 3]})
    out, user_ids, item_ids = reindex(raw)
    assert out["u"].tolist() == [1, 0, 1]
    assert out["i"].tolist() == [1, 1, 0]
    assert user_ids.tolist() == [3, 10] and item_ids.tolist() == [2, 7]


def test_fill_missing_keeps_observed_ratings():
    pred = np.full((2, 3), 3.3)
    ratings = pd.DataFrame({"u": [0, 1], "i": [2, 0], "rating": [5, 1]})
    filled = fill_missing(pred, ratings)
    assert filled.tolist() == [[3.3, 3.3, 5.0], [1.0, 3.3, 3.3]]
    assert (pred == 3.3).all()  # input untouched


def test_fill_missing_clips_predictions_only():
    pred = np.array([[6.4, -1.2, 3.0]])
    ratings = pd.DataFrame({"u": [0], "i": [2], "rating": [4]})
    assert fill_missing(pred, ratings).tolist() == [[5.0, 1.0, 4.0]]
