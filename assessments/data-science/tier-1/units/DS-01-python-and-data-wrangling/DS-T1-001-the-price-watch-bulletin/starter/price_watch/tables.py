"""Table-level reshaping (requirements R5-R7)."""
from __future__ import annotations

import pandas as pd

from .parsing import classify_label, parse_periods, parse_price, parse_unit  # noqa: F401
from .schema import PUBLISHED_COLUMNS, STATE_ZONES, TIDY_COLUMNS, RawTable  # noqa: F401


def split_tables(raw: pd.DataFrame) -> list[RawTable]:
    """R5: find every table in the raw grid and return one RawTable per table number.

    raw is the grid returned by load_raw(). Tables appear in bulletin order. A table that
    continues after a page break ("Table N (continued): ...") must be merged into table N,
    so every state and average row of table N ends up in ONE RawTable.body. The body
    keeps only state rows and average rows, in printed order, with the raw cell text.
    Banner lines, blank lines, notes and repeated headers are not body rows.
    """
    raise NotImplementedError("R5: implement split_tables")


def tidy_bulletin(raw: pd.DataFrame) -> pd.DataFrame:
    """R6: return the tidy table: one row per (item, state, period), columns TIDY_COLUMNS.

    Every state cell becomes a row, including missing ones (price NaN, status says why).
    Average rows are NOT included. zone comes from STATE_ZONES. price, unit_qty and
    price_per_base are float64; price_per_base = price / unit_qty.
    Rows are sorted by item, state, period, and the index is 0..n-1.
    """
    raise NotImplementedError("R6: implement tidy_bulletin")


def published_averages(raw: pd.DataFrame) -> pd.DataFrame:
    """R7: return every printed average, columns PUBLISHED_COLUMNS.

    area is the zone name for zone-average rows and "National" for the national row.
    published is float64. Rows are sorted by item, area, period, and the index is 0..n-1.
    """
    raise NotImplementedError("R7: implement published_averages")
