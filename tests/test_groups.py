import numpy as np
import pandas as pd

from gfair.groups import (
    centered_ratings,
    sample_candidates,
    sample_rnd_group,
    sample_sim_group,
    user_similarity_to,
)


def _ratings() -> pd.DataFrame:
    """4 users x 4 items. Users 0 and 1 agree, user 2 is the opposite of user 0,
    user 3 rates everything the same (zero vector after centering)."""
    matrix = np.array([
        [5, 4, 2, 1],
        [5, 5, 1, 1],
        [1, 2, 4, 5],
        [3, 3, 3, 3],
    ])
    u, i = np.nonzero(matrix)
    return pd.DataFrame({"u": u, "i": i, "rating": matrix[u, i]})


def test_rnd_group_has_distinct_users():
    group = sample_rnd_group(100, 30, np.random.default_rng(0))
    assert len(group) == 30 == len(set(group.tolist()))
    assert group.min() >= 0 and group.max() < 100


def test_candidates_distinct_and_sorted():
    cand = sample_candidates(500, 200, np.random.default_rng(0))
    assert len(cand) == 200 == len(set(cand.tolist()))
    assert (np.diff(cand) > 0).all()


def test_similarity_values():
    C = centered_ratings(_ratings(), 4, 4)
    sim = user_similarity_to(0, C)
    assert np.isclose(sim[0], 1.0)
    assert sim[1] > 0.9          # same taste
    assert np.isclose(sim[2], -1.0)  # exact opposite
    assert sim[3] == 0.0         # no variation in ratings


def test_sim_group_is_seed_plus_most_similar():
    C = centered_ratings(_ratings(), 4, 4)
    for seed in range(20):
        group = sample_sim_group(C, 2, np.random.default_rng(seed))
        assert len(set(group.tolist())) == 2
        sim = user_similarity_to(group[0], C)
        sim[group[0]] = -np.inf
        assert sim[group[1]] == sim.max()


def test_sim_group_reproducible():
    C = centered_ratings(_ratings(), 4, 4)
    a = sample_sim_group(C, 3, np.random.default_rng(5))
    b = sample_sim_group(C, 3, np.random.default_rng(5))
    assert a.tolist() == b.tolist()
