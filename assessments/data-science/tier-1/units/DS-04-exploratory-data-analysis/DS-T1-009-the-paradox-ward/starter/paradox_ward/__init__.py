"""paradox_ward: stratified rate analysis for the DS-T1-009 admissions data.

The public API is fixed because the tests import it.
"""
from .io import CANDIDATE_STRATIFIERS, INPUT_COLUMNS, load_admissions
from .rates import rate_table, wilson_interval
from .paradox import decompose_gap, direct_standardise, find_reversals, mix_table, screen_stratifiers
from .findings import build_findings

__all__ = [
    "CANDIDATE_STRATIFIERS", "INPUT_COLUMNS", "load_admissions", "rate_table", "wilson_interval",
    "decompose_gap", "direct_standardise", "find_reversals", "mix_table", "screen_stratifiers", "build_findings",
]
