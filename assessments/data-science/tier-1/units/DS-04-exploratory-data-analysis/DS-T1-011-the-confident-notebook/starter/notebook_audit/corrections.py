"""Corrected quantities for claims C1-C10 (R1-R10).

Each function takes (agents, act) as returned by load_all and returns one float. The exact
definition of each quantity is in resources/CLAIMS.md under "Corrected quantity".
"""
from __future__ import annotations

import pandas as pd


def c1_cohort_ratio(agents: pd.DataFrame, act: pd.DataFrame) -> float:
    """R1: corrected quantity for claim C1 (see resources/CLAIMS.md)."""
    raise NotImplementedError("R1: implement c1_cohort_ratio")


def c2_ppv(agents: pd.DataFrame, act: pd.DataFrame) -> float:
    """R2: corrected quantity for claim C2 (see resources/CLAIMS.md)."""
    raise NotImplementedError("R2: implement c2_ppv")


def c3_value_ratio(agents: pd.DataFrame, act: pd.DataFrame) -> float:
    """R3: corrected quantity for claim C3 (see resources/CLAIMS.md)."""
    raise NotImplementedError("R3: implement c3_value_ratio")


def c4_stratified_training_ratio(agents: pd.DataFrame, act: pd.DataFrame) -> float:
    """R4: corrected quantity for claim C4 (see resources/CLAIMS.md)."""
    raise NotImplementedError("R4: implement c4_stratified_training_ratio")


def c5_mh_rate_ratio(agents: pd.DataFrame, act: pd.DataFrame) -> float:
    """R5: corrected quantity for claim C5 (see resources/CLAIMS.md)."""
    raise NotImplementedError("R5: implement c5_mh_rate_ratio")


def c6_coaching_difference(agents: pd.DataFrame, act: pd.DataFrame) -> float:
    """R6: corrected quantity for claim C6 (see resources/CLAIMS.md)."""
    raise NotImplementedError("R6: implement c6_coaching_difference")


def c7_float_ratio(agents: pd.DataFrame, act: pd.DataFrame) -> float:
    """R7: corrected quantity for claim C7 (see resources/CLAIMS.md)."""
    raise NotImplementedError("R7: implement c7_float_ratio")


def c8_relative_flag_rate_change(agents: pd.DataFrame, act: pd.DataFrame) -> float:
    """R8: corrected quantity for claim C8 (see resources/CLAIMS.md)."""
    raise NotImplementedError("R8: implement c8_relative_flag_rate_change")


def c9_december_ratio(agents: pd.DataFrame, act: pd.DataFrame) -> float:
    """R9: corrected quantity for claim C9 (see resources/CLAIMS.md)."""
    raise NotImplementedError("R9: implement c9_december_ratio")


def c10_bonferroni_min_p(agents: pd.DataFrame, act: pd.DataFrame) -> float:
    """R10: corrected quantity for claim C10 (see resources/CLAIMS.md)."""
    raise NotImplementedError("R10: implement c10_bonferroni_min_p")


def state_churn_pvalues(agents: pd.DataFrame, act: pd.DataFrame) -> pd.Series:
    """R10 helper: p-value per "<state>/<lga_type>" group, sorted by group (see CLAIMS.md C10)."""
    raise NotImplementedError("R10: implement state_churn_pvalues")


CORRECTIONS = {f"C{i}": f for i, f in enumerate([
    c1_cohort_ratio,
    c2_ppv,
    c3_value_ratio,
    c4_stratified_training_ratio,
    c5_mh_rate_ratio,
    c6_coaching_difference,
    c7_float_ratio,
    c8_relative_flag_rate_change,
    c9_december_ratio,
    c10_bonferroni_min_p,
], start=1)}


def corrected_values(agents: pd.DataFrame, act: pd.DataFrame) -> dict[str, float]:
    """Return {"C1": value, ..., "C10": value}. Provided: it calls the functions above."""
    return {k: f(agents, act) for k, f in CORRECTIONS.items()}
