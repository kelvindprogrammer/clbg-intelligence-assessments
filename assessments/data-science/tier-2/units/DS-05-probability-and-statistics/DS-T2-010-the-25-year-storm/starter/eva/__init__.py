"""eva: extreme value analysis of daily rainfall (DS-T2-010).

This is the CONTRACT the automated tests import. Organise the rest of your package as you like.

Sign convention (mandatory): the GEV/GPD shape `xi` is positive for a HEAVY upper tail
(Frechet type), zero for Gumbel/exponential and negative for a bounded tail. Check the
convention of any library you use against this before trusting it.
"""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class GEVParams:
    loc: float
    scale: float
    shape: float  # xi, see the sign convention above


def load_daily(path) -> pd.DataFrame:
    """Read the daily file (provided): columns date (datetime64) and rain_mm (float, NaN when missing)."""
    return pd.read_csv(path, parse_dates=["date"])


def annual_maxima(df: pd.DataFrame, min_coverage: float = 0.9) -> pd.DataFrame:
    """Calendar-year maxima. Returns columns year, max_mm, coverage (share of the year's days with a
    non-missing value), keeping only years with coverage >= min_coverage, sorted by year."""
    raise NotImplementedError("R1: implement annual_maxima")


def fit_gev(x) -> GEVParams:
    """Maximum-likelihood GEV fit to block maxima. Raises ValueError for fewer than 5 values."""
    raise NotImplementedError("R2: implement fit_gev")


def gev_return_level(p: GEVParams, T: float) -> float:
    """The level exceeded with probability 1/T in a year (the 1 - 1/T quantile), including the
    xi -> 0 limit. Raises ValueError for T <= 1."""
    raise NotImplementedError("R2: implement gev_return_level")


def return_level_ci(x, T: float, level: float = 0.95) -> tuple[float, float, float]:
    """(estimate, lower, upper) for the T-year return level of a stationary GEV fitted to the
    maxima x. You choose the method (profile likelihood, bootstrap, delta method...) and justify it.
    The upper limit may be math.inf if your method says so."""
    raise NotImplementedError("R3: implement return_level_ci")


def decluster_runs(values, threshold: float, run_length: int = 2):
    """Runs declustering: return the maximum of each cluster of values above `threshold`, where a
    cluster ends after `run_length` consecutive values at or below the threshold. NaN counts as
    not exceeding. Returns a 1-D numpy array in time order."""
    raise NotImplementedError("R4: implement decluster_runs")


def fit_gpd(excesses) -> tuple[float, float]:
    """Maximum-likelihood generalised Pareto fit (scale, xi) to positive threshold excesses.
    Raises ValueError for fewer than 10 values or any non-positive value."""
    raise NotImplementedError("R4: implement fit_gpd")


def gpd_return_level(threshold: float, scale: float, shape: float, rate_per_year: float, T: float) -> float:
    """The level exceeded on average once every T years, when independent (declustered)
    exceedances of `threshold` occur at `rate_per_year` and their excesses are GPD(scale, shape).
    Raises ValueError if rate_per_year * T <= 1."""
    raise NotImplementedError("R4: implement gpd_return_level")
