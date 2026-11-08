"""Reconciliation against the switch's control totals (requirement R3). Not written yet."""
from __future__ import annotations

import pandas as pd

from .rules import RECONCILE_COLUMNS  # noqa: F401


def reconcile_with_switch(settlement: pd.DataFrame, control: pd.DataFrame) -> pd.DataFrame:
    """R3: compare the settlement's daily totals with the switch's control totals.

    Return one row per business_date that appears in EITHER input, columns RECONCILE_COLUMNS:
      settled_count, settled_value_ngn   totals over all agents from `settlement`
      switch_count, switch_value_ngn     from `control` (successful_count, successful_value_ngn)
      count_diff, value_diff_ngn         settled minus switch
      matches                            True only if count_diff == 0 and |value_diff_ngn| < 0.005
    A date missing from one side counts as zero on that side. Counts are int64.
    Rows are sorted by business_date and the index is 0..n-1.
    """
    raise NotImplementedError("R3: implement reconcile_with_switch")
