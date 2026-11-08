"""Analysis on the tidy table (requirements R8-R9)."""
from __future__ import annotations

import pandas as pd

from .schema import RECONCILE_COLUMNS, TOLERANCE  # noqa: F401


def reconcile_averages(tidy: pd.DataFrame, published: pd.DataFrame) -> pd.DataFrame:
    """R8: recompute every published average from the state rows and compare.

    Return one row per row of `published`, columns RECONCILE_COLUMNS:
      state_mean          mean of the reported (non-missing) state prices in that area
                          (the zone's states, or all states for "National")
      mean_of_zone_means  for "National" rows only: the mean of the recomputed zone
                          state_means; NaN for zone rows
      match               "state_mean", "mean_of_zone_means", "both" or "neither",
                          according to which recomputed value is within TOLERANCE
                          of the published figure
    Rows are sorted by item, area, period, and the index is 0..n-1.
    """
    raise NotImplementedError("R8: implement reconcile_averages")


def month_on_month(tidy: pd.DataFrame) -> pd.DataFrame:
    """R9: return a copy of `tidy` with one extra column, mom_pct.

    mom_pct = 100 * (price / previous_price - 1), where previous_price is the price of
    the same item in the same state in the immediately preceding CALENDAR month.
    It is NaN when either price is missing or the previous month is not in the bulletin.
    Row order and the other columns are unchanged, and the input is not modified.
    """
    raise NotImplementedError("R9: implement month_on_month")
