"""R3–R7: one parser per agency, each returning the canonical long table (see resources/output_schema.md).

Read resources/agency_formats.md first, then open each file and check that it agrees with the documentation.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from .reference import CANONICAL_COLUMNS, Reference  # noqa: F401


def parse_ngm(path, ref: Reference) -> pd.DataFrame:
    """Northern Grain Monitor JSON -> canonical table."""
    raise NotImplementedError("R3: parse_ngm")


def parse_cmb(path, ref: Reference) -> pd.DataFrame:
    """Coastal Markets Bureau XML -> canonical table (current revision only)."""
    raise NotImplementedError("R4: parse_cmb")


def parse_apc(path, ref: Reference) -> pd.DataFrame:
    """AgriPrice Cooperative workbook -> canonical table (every month sheet)."""
    raise NotImplementedError("R5: parse_apc")


def parse_lsa(path, ref: Reference) -> pd.DataFrame:
    """Legacy Statistical Archive fixed-width extract -> canonical table, with the trailer checked."""
    raise NotImplementedError("R6: parse_lsa")


PARSERS = {"ngm_prices.json": parse_ngm, "cmb_bulletin.xml": parse_cmb, "apc_survey.xlsx": parse_apc,
           "lsa_extract.txt": parse_lsa}


def load_all(data_dir, ref: Reference) -> pd.DataFrame:
    """All four sources in one canonical table, sorted by source, market_id, commodity_id and week_start."""
    raise NotImplementedError("R7: load_all")
