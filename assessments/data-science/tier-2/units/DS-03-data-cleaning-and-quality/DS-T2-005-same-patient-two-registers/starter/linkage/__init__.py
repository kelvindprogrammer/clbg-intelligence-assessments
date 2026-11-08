"""linkage: record linkage between the PHC and General Hospital registers (DS-T2-005).

Only the three functions below and their output formats are fixed (the tests import them).
How you standardise, block, compare, weight and decide is your design. Put it in as many
modules as you like.
"""
from __future__ import annotations

import pandas as pd

from .io import evaluate_links, load_clerical_sample, load_register


def candidate_pairs(a: pd.DataFrame, b: pd.DataFrame) -> pd.DataFrame:
    """R2: blocking. Return the candidate pairs your linker will compare.

    a, b: the raw PHC and GH registers as loaded by load_register.
    Returns a DataFrame with exactly the columns a_id (phc_id) and b_id (gh_id), no duplicates.
    """
    raise NotImplementedError("R2: implement candidate_pairs")


def deterministic_link(a: pd.DataFrame, b: pd.DataFrame) -> pd.DataFrame:
    """R3: your rule-based baseline. Return one-to-one matches as columns a_id, b_id."""
    raise NotImplementedError("R3: implement deterministic_link")


def link(a: pd.DataFrame, b: pd.DataFrame, clerical: pd.DataFrame) -> pd.DataFrame:
    """R4/R5: your probabilistic linker.

    clerical: the clerical sample for THESE registers (you may use it to estimate parameters or
    choose a threshold, or ignore it). Return columns a_id, b_id, score, decision, where decision
    is 'match' or 'review'. 'match' pairs must be one-to-one.
    """
    raise NotImplementedError("R4: implement link")


__all__ = ["candidate_pairs", "deterministic_link", "link", "evaluate_links", "load_clerical_sample", "load_register"]
