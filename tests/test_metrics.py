import numpy as np
import pytest

from gfair.metrics import (
    average_precision,
    fairness,
    group_utility,
    kendall_tau,
    mean_rating,
    ndcg_at_k,
    no_misery_share,
    precision_at_k,
)

SIGMA = np.arange(20)


def test_identical_lists_score_one():
    assert ndcg_at_k(SIGMA, SIGMA, 20) == pytest.approx(1.0)
    assert average_precision(SIGMA, SIGMA) == pytest.approx(1.0)
    for k in (1, 5, 10, 20):
        assert precision_at_k(SIGMA, SIGMA, k) == pytest.approx(1.0)
    assert kendall_tau(SIGMA, SIGMA) == pytest.approx(1.0)


def test_reversed_list_tau_minus_one():
    assert kendall_tau(SIGMA[::-1], SIGMA) == pytest.approx(-1.0)


def test_disjoint_lists_score_zero():
    other = np.arange(100, 120)
    # Gain 2^rel as printed in the paper: a miss still earns 2^0 = 1 (A11).
    assert 0 < ndcg_at_k(other, SIGMA, 20) < 1e-4
    assert 0.05 < ndcg_at_k(other[:5], SIGMA[:5], 5) < 0.07
    assert average_precision(other, SIGMA) == 0.0
    assert precision_at_k(other, SIGMA, 10) == 0.0


def test_ndcg_hand_computed():
    # N = 2, truth [a, b]: relevances 2 and 1. List [b, x]: gains 2^1 = 2 and 2^0 = 1.
    dcg = 2 / np.log2(2) + 1 / np.log2(3)
    idcg = 4 / np.log2(2) + 2 / np.log2(3)
    assert ndcg_at_k(np.array([1, 9]), np.array([0, 1]), 2) == pytest.approx(dcg / idcg)
    assert ndcg_at_k(np.array([1, 9]), np.array([0, 1]), 1) == pytest.approx(2 / 4)


def test_tau_missing_items_tied_at_last_rank():
    # sigma [a, b], truth [a, c]. Union {a, b, c}; positions in sigma: a0 b1 c2(last),
    # in truth: a0 c1 b2(last). Pairs: (a,b) concordant, (a,c) concordant, (b,c) discordant.
    assert kendall_tau(np.array([0, 1]), np.array([0, 2])) == pytest.approx(1 / 3)


def test_average_precision_hand_computed():
    # hits at positions 1 and 3: (1/1 + 2/3) / N with N = 4
    sigma = np.array([0, 100, 1, 101])
    assert average_precision(sigma, np.arange(4)) == pytest.approx((1 + 2 / 3) / 4)


def test_precision_partial_overlap():
    sigma = np.array([0, 100, 1, 101])
    assert precision_at_k(sigma, np.arange(4), 4) == pytest.approx(0.5)
    assert precision_at_k(sigma, np.arange(4), 1) == pytest.approx(1.0)


def test_fairness_and_group_utility():
    u = np.array([0.2, 0.5, 0.8])
    assert fairness(u) == pytest.approx(0.2)
    assert group_utility(u) == pytest.approx(0.5)


def test_no_misery_share_and_mean_rating():
    ratings = np.array([5.0, 1.0, 3.0, 2.9, 4.0])   # member's ratings of 5 candidates
    sigma = np.array([0, 1, 2, 3])
    # 5 and 3 are fine (3 is not below the threshold), 1 and 2.9 are disliked.
    assert no_misery_share(sigma, ratings, 3.0) == 0.5
    assert mean_rating(sigma, ratings) == pytest.approx((5 + 1 + 3 + 2.9) / 4)
    assert no_misery_share(np.array([0, 4]), ratings, 3.0) == 1.0


def test_rating_metrics_see_what_top_n_metrics_miss():
    # Both lists miss the member's top 1 (item 0); P@1 cannot tell them apart,
    # the rating-based metrics can.
    ratings = np.array([5.0, 4.5, 1.0])
    truth = np.array([0])
    liked, hated = np.array([1]), np.array([2])
    assert precision_at_k(liked, truth, 1) == precision_at_k(hated, truth, 1) == 0.0
    assert no_misery_share(liked, ratings, 3.0) == 1.0
    assert no_misery_share(hated, ratings, 3.0) == 0.0
    assert mean_rating(liked, ratings) > mean_rating(hated, ratings)
