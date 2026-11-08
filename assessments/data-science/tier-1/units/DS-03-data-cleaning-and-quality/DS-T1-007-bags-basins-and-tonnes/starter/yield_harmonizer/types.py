"""Result types shared across the package. These are provided, so you don't need to change them."""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class Conversion:
    """The outcome of converting one harvest quantity to kilograms.

    kg:      central estimate, using the table's kg_per_unit
    kg_low:  lower bound, using the table's kg_low
    kg_high: upper bound, using the table's kg_high
    grade:   the factor's reliability grade from the table ('A', 'B' or 'C')
    """
    kg: float
    kg_low: float
    kg_high: float
    grade: str


@dataclass
class HarmoniseResult:
    records: pd.DataFrame  # one row per input record (resources/output_schema.md)
    issues: pd.DataFrame   # one row per detected issue
