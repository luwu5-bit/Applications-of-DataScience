"""Load MovieLens 1M."""

from pathlib import Path

import pandas as pd


def load_ratings(raw_dir: str | Path) -> pd.DataFrame:
    """Read ratings.dat into columns user_id, item_id, rating, timestamp.

    Ids are the original MovieLens ids (1-based, with gaps for items).
    Use `reindex` to get contiguous 0-based indices for the rating matrix.
    """
    return pd.read_csv(
        Path(raw_dir) / "ratings.dat",
        sep="::",
        engine="python",  # multi-character separator
        names=["user_id", "item_id", "rating", "timestamp"],
    )


def reindex(ratings: pd.DataFrame) -> tuple[pd.DataFrame, pd.Index, pd.Index]:
    """Map user and item ids to contiguous 0-based indices.

    Returns the ratings with added columns `u` and `i`, plus the user and item
    id lookups (position = index, value = original id).
    """
    # sort=True: index order follows id order, so "ties broken by item id"
    # is the same as "ties broken by column index" everywhere downstream.
    u, user_ids = pd.factorize(ratings["user_id"], sort=True)
    i, item_ids = pd.factorize(ratings["item_id"], sort=True)
    return ratings.assign(u=u, i=i), pd.Index(user_ids), pd.Index(item_ids)
