"""Composition, reversal detection, standardisation and decomposition (R3-R7).

The exact definitions are in README section D.1. Read them carefully: the hidden tests
check these functions on data generated with a different seed and a different
referral hospital.
"""
from __future__ import annotations

import pandas as pd


def mix_table(df: pd.DataFrame, group_col: str, stratum_col: str) -> pd.DataFrame:
    """R3: case-mix table. Index = groups (sorted), columns = strata (sorted).

    Each cell is the share of that group's rows that fall in that stratum, so each row sums to 1.
    """
    raise NotImplementedError("R3: implement mix_table")


def find_reversals(df: pd.DataFrame, group_col: str, stratum_col: str, outcome: str = "died_30d",
                   min_n: int = 20) -> pd.DataFrame:
    """R4: one row per unordered pair of groups, with group_a < group_b alphabetically.

    Columns: group_a, group_b, crude_diff, n_strata_compared, n_strata_opposite, reversal.
    See README R4 for the definitions of each column.
    """
    raise NotImplementedError("R4: implement find_reversals")


def direct_standardise(df: pd.DataFrame, group_col: str, stratum_col: str, outcome: str = "died_30d") -> pd.DataFrame:
    """R5: columns <group_col>, crude_rate, standardised_rate; one row per group, sorted by group.

    The standard population is the pooled distribution of `stratum_col` over all rows.
    A group with no rows in some stratum gets standardised_rate = NaN.
    """
    raise NotImplementedError("R5: implement direct_standardise")


def decompose_gap(df: pd.DataFrame, a: str, b: str, group_col: str, stratum_col: str,
                  outcome: str = "died_30d") -> dict:
    """R6: decompose crude_rate(a) - crude_rate(b) into composition and rate effects.

    Return {"crude_gap": float, "composition_effect": float, "rate_effect": float}, where the two
    effects sum to crude_gap (to floating-point precision). Raise ValueError if a stratum is
    missing from either group.
    """
    raise NotImplementedError("R6: implement decompose_gap")


def screen_stratifiers(df: pd.DataFrame, group_col: str, candidates: list[str], outcome: str = "died_30d",
                       min_n: int = 20) -> pd.DataFrame:
    """R7: one row per candidate stratifier: candidate, max_shift, n_reversal_pairs.

    Sorted by max_shift descending (ties broken by candidate name ascending).
    """
    raise NotImplementedError("R7: implement screen_stratifiers")
