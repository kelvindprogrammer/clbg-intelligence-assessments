"""Exploratory analysis toolkit for the BRT delay data. Signatures are fixed; internals are yours."""
from __future__ import annotations

import pandas as pd

REQUIRED = {"date", "route", "operator", "trips", "mean_delay_min"}
LEDGER_COLUMNS = ["id", "hypothesis", "test", "evidence", "verdict", "confidence"]


def load_route_day(path) -> pd.DataFrame:
    """Read route_day.csv with `date` parsed as datetime; raise ValueError on missing columns (R0)."""
    raise NotImplementedError("R0: load and validate route_day.csv")


def headline_change(df: pd.DataFrame, split_date: str) -> float:
    """Relative change in the trip-weighted mean delay: days >= split_date versus days before (R1)."""
    raise NotImplementedError("R1: headline relative change")


def kitagawa(df: pd.DataFrame, split_date: str, by: str = "route") -> dict:
    """Decompose the change in weighted mean delay into {'total','within','mix'}, in minutes (R2)."""
    raise NotImplementedError("R2: exact two-factor decomposition; within + mix must equal total")


def reversal_segments(df: pd.DataFrame, split_date: str, by: str = "route") -> list:
    """Sorted segment labels whose own change has the OPPOSITE sign to the headline change (R3)."""
    raise NotImplementedError("R3: Simpson-style reversal detection")


def locate_instrument_break(df: pd.DataFrame) -> tuple:
    """(operator, 'YYYY-MM-DD'): whose recorded delays changed level, and the first affected date (R4)."""
    raise NotImplementedError("R4: detect the measurement break from the data, not from the operator names")


def adjusted_headline_change(df: pd.DataFrame, split_date: str, operator: str, break_date: str) -> float:
    """Headline relative change after estimating and removing the operator's level shift from `break_date` on (R5)."""
    raise NotImplementedError("R5: estimate the shift from data, remove it, recompute the headline")


def validate_ledger(path) -> list:
    """Return a list of problems with a hypothesis ledger CSV (empty list if valid) (R6)."""
    raise NotImplementedError("R6: enforce the ledger rules in the README")
