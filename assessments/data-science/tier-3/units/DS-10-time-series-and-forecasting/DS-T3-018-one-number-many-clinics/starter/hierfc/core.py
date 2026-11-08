"""Hierarchical forecast reconciliation toolkit. Provided: Hierarchy, METHODS, load_export, base_fit,
base_forecasts. Implement R1-R4."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

METHODS = ["bottom_up", "top_down", "ols", "wls_struct", "mint_shrink"]


@dataclass
class Hierarchy:
    names: list          # ["TOTAL", zones (sorted)..., clinics (sorted by zone, then clinic_id)...]
    S: np.ndarray        # summing matrix, shape (n_all, n_bottom): y_all = S @ y_bottom
    Y: np.ndarray        # (T, n_all) weekly visits, columns in `names` order, rows in week order
    n_bottom: int


def load_export(path) -> pd.DataFrame:
    """Provided. Columns: zone, clinic_id, week (ISO Monday), visits."""
    return pd.read_csv(path, dtype={"zone": str, "clinic_id": str, "week": str})


def base_fit(y: np.ndarray, h: int):
    """Provided. The univariate base forecaster used for every node: log1p regression on trend and two annual
    harmonics over the last 156 weeks, plus the mean of the last 8 log-residuals. Returns (forecast >= 0 of
    length h, in-sample residuals on the original scale for the last 156 weeks)."""
    y = np.asarray(y, float)[-156:]
    ly = np.log1p(y)
    n = len(y)
    t = np.arange(n + h, dtype=float)
    w = 2 * np.pi * t / 52.18
    X = np.column_stack([np.ones_like(t), t, np.sin(w), np.cos(w), np.sin(2 * w), np.cos(2 * w)])
    beta, *_ = np.linalg.lstsq(X[:n], ly, rcond=None)
    fit = X @ beta
    adj = float(np.mean((ly - fit[:n])[-8:]))
    return np.expm1(fit[n:] + adj), y - np.expm1(fit[:n])


def base_forecasts(Y: np.ndarray, h: int):
    """Provided. Apply base_fit to every column. Returns (forecasts (h, n_all), residuals (<=156, n_all))."""
    fcs, res = [], []
    for j in range(Y.shape[1]):
        f, r = base_fit(Y[:, j], h)
        fcs.append(f)
        res.append(r)
    return np.column_stack(fcs), np.column_stack(res)


def build_hierarchy(df: pd.DataFrame) -> Hierarchy:
    """R1: build the three-level hierarchy TOTAL > zone > clinic from the long table, with the ordering
    described in `Hierarchy`. S has a first row of ones, one row per zone, then the identity."""
    raise NotImplementedError("R1: build_hierarchy")


def reconcile(base_fc: np.ndarray, S: np.ndarray, method: str, resid=None, Y=None, prop_window=None) -> np.ndarray:
    """R2: map base forecasts (h, n_all) to coherent forecasts (h, n_all) = (S P base^T)^T.
    bottom_up: P = [0 | I].
    top_down: all forecast mass comes from the TOTAL base forecast, split by the AVERAGE historical clinic share
        of the total over Y (all rows, or only the last `prop_window` rows if given).
    ols: P = (S'S)^-1 S'.   wls_struct: W = diag(S @ 1), P = (S'W^-1 S)^-1 S'W^-1.
    mint_shrink: the same with W = shrunk covariance of `resid`: Sigma = R'R/T over rows without NaN,
        lam = sum_{i!=j} Var(r_ij) / sum_{i!=j} r_ij^2 clipped to [0, 1] (Schaefer-Strimmer, on the correlation
        scale, Var(r_ij) = T/(T-1)^3 * sum_t (w_tij - mean_t w_tij)^2 with w_tij = x_ti x_tj, x = R / sqrt(diag Sigma)),
        W = lam*diag(Sigma) + (1-lam)*Sigma.
    Raise ValueError for an unknown method."""
    raise NotImplementedError("R2: reconcile")


def run_evaluation(df: pd.DataFrame, h: int = 8, initial: int = 156, step: int = 13, prop_window=None) -> pd.DataFrame:
    """R3: rolling-origin evaluation. For k = initial, initial+step, ... with k+h <= T: base forecasts from
    Y[:k] only, then 'base' plus every method in METHODS reconciled. Per node, RMSSE = sqrt(mean((y-f)^2) /
    mean(diff(Y[:k, j])^2)), averaged over origins; then averaged over the nodes of each level. Return a DataFrame
    [method, level, rmsse] with levels 'total', 'zone', 'clinic', 'all' ('all' = mean over ALL nodes) for the
    methods 'base' + METHODS."""
    raise NotImplementedError("R3: run_evaluation")


def detect_transfers(df: pd.DataFrame) -> list:
    """R4 (open method): find clinics whose share of their zone total changes level persistently (a closure or a
    catchment change). Return a list of {'clinic_id': str, 'week_index': int, 'direction': 'up' | 'down'} with
    week_index the 0-based week at which the new level begins. Return [] when you find no credible shift. You must
    justify your decision rule and its false-alarm behaviour in the report."""
    raise NotImplementedError("R4: detect_transfers")
