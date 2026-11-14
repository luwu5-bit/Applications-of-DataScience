"""Monte Carlo checks on the paper's toy example (Fig. 1).

Expected values are the corrected ones (CLAUDE.md, "Known issues in the paper"):
the i1/i2 tie is at w = (2/5, 3/5), so P(i2 top-1) = 0.6, not 4/7.
"""

import numpy as np

from gfair.aggregators import monte_carlo_counts, npo, xpo

S = 200_000
TOL = 0.01


def test_top1_probabilities(toy_ranks):
    rng = np.random.default_rng(0)
    p = monte_carlo_counts(toy_ranks, N=1, n_samples=S, rng=rng) / S
    assert abs(p[1] - 0.60) < TOL  # i2
    assert abs(p[0] - 0.40) < TOL  # i1
    assert p[2:].sum() == 0        # dominated items never win


def test_top2_inclusion_over_npo_pool(toy_ranks):
    rng = np.random.default_rng(0)
    pool = [0, 1, 2, 3]  # NPO pool for N = 2
    p = monte_carlo_counts(toy_ranks[pool], N=2, n_samples=S, rng=rng) / S
    expected = [0.60, 0.833, 0.40, 0.167]  # i1, i2, i3, i4
    assert np.allclose(p, expected, atol=TOL)


def test_npo_top2_list(toy_ranks):
    sigma, info = npo(toy_ranks, N=2, n_samples=S, rng=np.random.default_rng(0))
    assert sigma.tolist() == [1, 0]  # [i2, i1]
    assert info["pool_size"] == 4


def test_xpo_top2_list(toy_ranks):
    sigma, info = xpo(toy_ranks, N=2, n_samples=S, rng=np.random.default_rng(0))
    assert sorted(sigma.tolist()) == [0, 1]
    assert info == {"pool_size": 2, "x": 1}
