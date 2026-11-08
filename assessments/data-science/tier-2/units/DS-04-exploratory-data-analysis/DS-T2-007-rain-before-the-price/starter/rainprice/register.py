"""Your hypothesis register (R1). The method is yours to choose, justify and compare with the baseline.

The only fixed contract is the signature and the output schema (REGISTER_COLUMNS, STATUSES):
validate_register() in io.py must accept what you return, and the hidden suite will call
build_register(panel) with no other arguments on panels it generates itself.
"""
from __future__ import annotations

import pandas as pd

from .io import Panel


def build_register(panel: Panel, **kwargs) -> pd.DataFrame:
    """R1: return a hypothesis register for `panel`.

    One or more rows per (state, commodity) pair you examined. A pair counts as a claimed link if
    any of its rows has status "supported". Must be deterministic for a fixed panel and finish in
    under 5 minutes on a laptop.
    """
    raise NotImplementedError("R1: implement build_register")
