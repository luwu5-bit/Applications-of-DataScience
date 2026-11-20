import numpy as np

from gfair.aggregators import avg, awm, borda, lm, max_pleasure, med, mul
from gfair.pareto import rank_matrix


# Two members (rows), five items (columns).
PREDS = np.array([
    [5.0, 4.0, 2.0, 3.0, 4.5],
    [1.0, 4.0, 5.0, 3.5, 3.0],
])


def test_avg_and_lm():
    # means: 3.0, 4.0, 3.5, 3.25, 3.75; minima: 1, 4, 2, 3, 3
    assert avg(PREDS, 3).tolist() == [1, 4, 2]
    assert lm(PREDS, 3).tolist() == [1, 3, 4]


def test_awm_drops_items_with_misery():
    # Threshold 3: items 0 (member 2 gives 1) and 2 (member 1 gives 2) are out.
    # Misery-free items 1, 4, 3 ordered by mean 4.0, 3.75, 3.25.
    sigma, info = awm(PREDS, 3, threshold=3.0)
    assert sigma.tolist() == [1, 4, 3]
    assert info["pool_size"] == 3


def test_awm_rating_equal_to_threshold_is_not_misery():
    sigma, info = awm(np.array([[3.0, 2.9], [5.0, 5.0]]), 1, threshold=3.0)
    assert sigma.tolist() == [0]
    assert info["pool_size"] == 1


def test_awm_fills_with_fewest_miserable_members():
    # Three members. No item is misery-free; item 1 has one unhappy member,
    # items 0 and 2 have two. Fill: item 1, then items 0 and 2 by mean.
    preds = np.array([
        [1.0, 2.0, 5.0],
        [2.0, 4.0, 1.0],
        [5.0, 4.0, 2.5],
    ])
    sigma, info = awm(preds, 3, threshold=3.0)
    assert info["pool_size"] == 0
    assert sigma.tolist() == [1, 2, 0]   # means: 2.67, 3.33, 2.83


def test_awm_equals_avg_without_misery():
    # With a threshold below every rating, AWM is plain AVG.
    sigma, info = awm(PREDS, 5, threshold=0.0)
    assert sigma.tolist() == avg(PREDS, 5).tolist()
    assert info["pool_size"] == 5


def test_mul_and_max():
    # products: 5, 16, 10, 10.5, 13.5; maxima: 5, 4, 5, 3.5, 4.5
    assert mul(PREDS, 3).tolist() == [1, 4, 3]
    assert max_pleasure(PREDS, 3).tolist() == [0, 2, 4]


def test_borda_and_med_on_ranks():
    # Three members, four items; ranks per member (1 = best):
    #   item 0: 1, 4, 4   mean 3.0  median 4
    #   item 1: 2, 1, 3   mean 2.0  median 2
    #   item 2: 3, 2, 1   mean 2.0  median 2
    #   item 3: 4, 3, 2   mean 3.0  median 3
    ranks = np.array([[1, 4, 4], [2, 1, 3], [3, 2, 1], [4, 3, 2]], dtype=float)
    assert borda(ranks, 4).tolist() == [1, 2, 0, 3]
    assert med(ranks, 4).tolist() == [1, 2, 3, 0]


def test_borda_uses_tied_ranks():
    # Member 0 rates items 0 and 1 equally: both get rank 1.5.
    preds = np.array([[5.0, 5.0, 1.0], [1.0, 5.0, 3.0]])
    ranks = rank_matrix(preds)
    assert ranks[:, 0].tolist() == [1.5, 1.5, 3]
    assert borda(ranks, 3).tolist() == [1, 0, 2]   # mean ranks: 2.25, 1.25, 2.5
