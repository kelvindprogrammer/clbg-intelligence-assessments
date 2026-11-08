"""smallarea: small-area estimation of school pass rates (DS-T2-009).

This is the CONTRACT the automated tests use. Everything else in your package (modules,
estimators, evaluation code) is your design. Keep these two functions and their signatures.
"""
from __future__ import annotations

import pandas as pd

OUTPUT_COLUMNS = ["school_id", "estimate", "lower", "upper"]


def estimate_rates(results: pd.DataFrame, schools: pd.DataFrame, level: float = 0.90) -> pd.DataFrame:
    """Estimate every school's long-run credit-pass rate (the rate it would show in a typical
    year), with a central interval at `level`.

    results: rows of (school_id, year, candidates, credit_passes), any subset of years.
    schools: one row per school (school_id, lga, ownership, location).
    Returns one row per school in `schools`, sorted by school_id, with OUTPUT_COLUMNS, where
    0 <= lower <= estimate <= upper <= 1. Must not fail for a school with no results rows.
    This should be the estimator you RECOMMEND after your comparison.
    """
    raise NotImplementedError("R1: implement estimate_rates with your recommended estimator")


def select_schools(results: pd.DataFrame, schools: pd.DataFrame, k: int, which: str = "top") -> list[str]:
    """Return k distinct school_ids: the schools you would recommend for the award (which="top")
    or for the intervention programme (which="bottom"). Raises ValueError for another `which`."""
    raise NotImplementedError("R2: implement select_schools")
