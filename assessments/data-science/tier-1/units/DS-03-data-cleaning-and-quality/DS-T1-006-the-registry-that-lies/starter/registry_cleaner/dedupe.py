"""Duplicate detection (requirement R8).

Design question to answer in your report: what evidence is strong enough to
conclude that two rows describe the same student? Names alone are not enough.
"""
from __future__ import annotations

import pandas as pd


def find_duplicate_groups(df: pd.DataFrame) -> list[set[str]]:
    """Return a partition of df['record_id'] into groups that refer to the same student.

    Every record_id must appear in exactly one group. Singletons are groups of size 1.
    `df` is the RAW export as loaded by `load_export` (all columns are strings).
    """
    raise NotImplementedError("R8: implement find_duplicate_groups")
