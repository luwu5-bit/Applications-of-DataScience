import numpy as np
import pytest


@pytest.fixture
def toy_ranks() -> np.ndarray:
    """Paper Fig. 1: rows i1..i6, columns (u1, u2), rank 1 = best."""
    return np.array([[4, 1], [1, 3], [2, 4], [6, 2], [3, 6], [5, 5]])
