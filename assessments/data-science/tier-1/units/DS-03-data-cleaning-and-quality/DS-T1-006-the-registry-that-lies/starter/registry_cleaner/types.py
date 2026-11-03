"""Result types shared across the package. These are provided, so you don't need to change them."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Literal, Optional

import pandas as pd

DateStatus = Literal["ok", "missing", "ambiguous", "invalid"]


@dataclass(frozen=True)
class ParsedDate:
    """The outcome of parsing one date string.

    value:  the parsed date, or None. For status 'ambiguous' this holds the DD/MM reading.
    status: 'ok' | 'missing' | 'ambiguous' | 'invalid'
    """
    value: Optional[date]
    status: DateStatus


@dataclass
class CleanResult:
    clean: pd.DataFrame   # one row per inferred student (resources/output_schema.md)
    issues: pd.DataFrame  # one row per detected defect
