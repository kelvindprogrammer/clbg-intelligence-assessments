"""Forecast benchmark harness for distribution-feeder load. Implement R1-R6; `Forecast`, `load_export`
and `series_of` are provided."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np
import pandas as pd


@dataclass
class Forecast:
    mean: np.ndarray
    lower: np.ndarray
    upper: np.ndarray


def load_export(path) -> pd.DataFrame:
    """Provided. Columns: feeder_id, date (ISO text), peak_mw (daily peak load in MW)."""
    return pd.read_csv(path, dtype={"feeder_id": str, "date": str})


def series_of(df: pd.DataFrame, feeder_id: str) -> pd.Series:
    """Provided. One feeder's complete daily series with a DatetimeIndex (freq 'D')."""
    d = df[df["feeder_id"] == feeder_id]
    return pd.Series(d["peak_mw"].to_numpy(float), index=pd.DatetimeIndex(pd.to_datetime(d["date"]), freq="D"), name=feeder_id)


def flag_outages(s: pd.Series) -> pd.Series:
    """R1: boolean Series (same index) marking supply-outage days: days on which the recorded peak is
    implausibly low for that feeder because the feeder was off. Choose your own rule and justify it in the report."""
    raise NotImplementedError("R1: flag_outages")


def seasonal_naive_forecast(train: pd.Series, h: int, level: float = 0.8) -> Forecast:
    """R2: mean[i] = train[-7 + (i % 7)]. Interval = mean + the (1-level)/2 and (1+level)/2 quantiles
    (np.quantile, default method) of the in-sample weekly differences d_t = y_t - y_{t-7}."""
    raise NotImplementedError("R2: seasonal_naive_forecast")


def my_forecaster(train: pd.Series, h: int, level: float = 0.8) -> Forecast:
    """R3: YOUR method. Same signature and return type as R2. `train` is the history up to the forecast origin
    and nothing else. Must return finite arrays of length h with lower <= upper."""
    raise NotImplementedError("R3: my_forecaster")


def interval_score(y, lower, upper, level: float) -> float:
    """R4: mean interval score (Gneiting and Raftery) with alpha = 1 - level:
    (u - l) + (2/alpha)(l - y)[y < l] + (2/alpha)(y - u)[y > u]."""
    raise NotImplementedError("R4: interval_score")


def backtest_forecasts(y: pd.Series, forecaster: Callable, h: int, initial: int, step: int, level: float = 0.8) -> list[dict]:
    """R5: rolling-origin loop for k = initial, initial+step, ... while k+h <= len(y). The forecaster receives
    y.iloc[:k] only. Return a list of dicts with keys origin (k), mean, lower, upper, actual (arrays of length h).
    Raise ValueError if a forecaster returns wrong shapes, NaN, or lower > upper."""
    raise NotImplementedError("R5: backtest_forecasts")


def run_benchmark(df: pd.DataFrame, forecasters: dict, h: int = 14, initial: int = 400, step: int = 28, level: float = 0.8) -> pd.DataFrame:
    """R6: DataFrame with columns [feeder_id, method, mase, coverage, interval_score], one row per feeder and
    method, sorted by feeder_id then method. mase = mean over origins of MAE / (mean |y_t - y_{t-7}| over y[:k]);
    coverage = share of ALL test points inside [lower, upper]; interval_score = mean over all test points."""
    raise NotImplementedError("R6: run_benchmark")
