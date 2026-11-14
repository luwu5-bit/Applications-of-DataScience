import numpy as np

from gfair.pareto import dom_counts, npo_pool, rank_matrix, xpo_pool


def test_rank_matrix_shape_and_tie_break():
    preds = np.array([[5.0, 3.0, 3.0, 4.0], [1.0, 2.0, 3.0, 4.0]])  # (m=2, items=4)
    ranks = rank_matrix(preds)
    assert ranks.shape == (4, 2)
    # member 0: item 0 best, then item 3, then the tie 1 vs 2 goes to the lower id
    assert ranks[:, 0].tolist() == [1, 3, 4, 2]
    assert ranks[:, 1].tolist() == [4, 3, 2, 1]


def test_dom_counts_toy(toy_ranks):
    assert dom_counts(toy_ranks).tolist() == [0, 0, 1, 1, 2, 3]


def test_pareto_levels_toy(toy_ranks):
    dom = dom_counts(toy_ranks)
    assert npo_pool(dom, 1).tolist() == [0, 1]          # level 1 = {i1, i2}
    assert npo_pool(dom, 2).tolist() == [0, 1, 2, 3]    # level 2 = {i1, i2, i3, i4}


def test_xpo_pool_toy(toy_ranks):
    pool, x = xpo_pool(dom_counts(toy_ranks), 2)
    assert x == 1
    assert pool.tolist() == [0, 1]


def test_xpo_level_grows_when_needed(toy_ranks):
    # N = 3: level 1 has only 2 items, level 2 has 4
    pool, x = xpo_pool(dom_counts(toy_ranks), 3)
    assert x == 2
    assert pool.tolist() == [0, 1, 2, 3]
