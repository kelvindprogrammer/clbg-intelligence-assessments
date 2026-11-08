"""Baseline forecasting toolkit for mobile-money agent activity. Implement every stub (R1-R8)."""
from __future__ import annotations

from typing import Callable

import numpy as np
import pandas as pd


def load_export(path) -> pd.DataFrame:
    """Provided. Columns: agent_id, date (ISO text), txn_count (int; -1 is a sentinel for 'not recorded')."""
    return pd.read_csv(path, dtype={"agent_id": str, "date": str})


def to_regular(df: pd.DataFrame, agent_id: str) -> pd.Series:
    """R1: one agent's daily series on a complete DatetimeIndex (freq 'D'), named 'txn_count', float dtype.
    Missing days and -1 sentinels become NaN (unknown, NOT zero). If a date appears more than once, keep the
    LAST occurrence in file order."""
    raise NotImplementedError("R1: to_regular")


def fill_gaps(s: pd.Series, period: int = 7) -> pd.Series:
    """R2: fill NaN in time order. Use the (already filled) value `period` steps earlier; else the ORIGINAL
    observed value `period` steps later; else the median of observed values. Do not mutate the input."""
    raise NotImplementedError("R2: fill_gaps")


def seasonal_naive(train: np.ndarray, h: int, period: int = 7) -> np.ndarray:
    """R3: forecast[i] = train[-period + (i % period)]."""
    raise NotImplementedError("R3: seasonal_naive")


def moving_average(train: np.ndarray, h: int, window: int = 7) -> np.ndarray:
    """R4: a flat forecast equal to the mean of the last `window` training values."""
    raise NotImplementedError("R4: moving_average")


def mae(y: np.ndarray, yhat: np.ndarray) -> float:
    """R5a: mean absolute error."""
    raise NotImplementedError("R5: mae")


def mase(y: np.ndarray, yhat: np.ndarray, train: np.ndarray, period: int = 7) -> float:
    """R5b: MAE divided by the in-sample seasonal-naive MAE of `train` (mean |train[t]-train[t-period]|).
    Raise ValueError if that scale is zero."""
    raise NotImplementedError("R5: mase")


def rolling_origin(n: int, initial: int, h: int, step: int) -> list[tuple[int, int]]:
    """R6: list of (k, k+h) for k = initial, initial+step, ... while k+h <= n. Train is y[:k], test is y[k:k+h]."""
    raise NotImplementedError("R6: rolling_origin")


def backtest(y: np.ndarray, method: Callable[[np.ndarray, int], np.ndarray], h: int, initial: int,
             step: int, period: int = 7) -> float:
    """R7: mean MASE over all rolling origins. The MASE scale must use ONLY y[:k] (no future data).
    Raise ValueError if there are no origins."""
    raise NotImplementedError("R7: backtest")


def choose_baseline(df: pd.DataFrame, h: int = 7, initial: int = 84, step: int = 7) -> dict[str, str]:
    """R8: for every agent_id (sorted), run to_regular -> fill_gaps -> backtest of seasonal_naive and
    moving_average (window 7); return {agent_id: 'seasonal_naive' | 'moving_average'}, the lower mean MASE
    winning, ties going to 'seasonal_naive'."""
    raise NotImplementedError("R8: choose_baseline")
