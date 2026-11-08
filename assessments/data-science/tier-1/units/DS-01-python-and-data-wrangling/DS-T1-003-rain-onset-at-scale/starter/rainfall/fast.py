"""Fast, vectorised versions of the legacy indices (requirements R1-R4).

Each function must return a DataFrame that is equivalent to its legacy counterpart on
ANY valid input (README section D.1 defines "equivalent"). Use pandas and NumPy only.
No Python-level loop over days or rows: loops over a handful of constants are fine.
Read the legacy docstrings and code carefully: they are the specification.
"""
from __future__ import annotations

import numpy as np  # noqa: F401
import pandas as pd

from .legacy import (DRY_SPELL_WINDOW, MIN_CLIM_YEARS, ONSET_3DAY_MM, ONSET_DRY_SPELL,  # noqa: F401
                     ONSET_LOOKAHEAD, ONSET_SEARCH, WET_DAY_MM)


def monthly_totals(df: pd.DataFrame) -> pd.DataFrame:
    """R1: equivalent to legacy.monthly_totals."""
    raise NotImplementedError("R1: implement fast.monthly_totals")


def longest_dry_spell(df: pd.DataFrame) -> pd.DataFrame:
    """R2: equivalent to legacy.longest_dry_spell."""
    raise NotImplementedError("R2: implement fast.longest_dry_spell")


def onset_dates(df: pd.DataFrame) -> pd.DataFrame:
    """R3: equivalent to legacy.onset_dates."""
    raise NotImplementedError("R3: implement fast.onset_dates")


def standardised_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    """R4: equivalent to legacy.standardised_anomalies."""
    raise NotImplementedError("R4: implement fast.standardised_anomalies")
