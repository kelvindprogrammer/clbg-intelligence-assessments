import numpy as np


def make_lag_matrix(series, n_lags):
    raise NotImplementedError("R1: row i = series[i:i+n_lags], target = series[i+n_lags]")


def walk_forward_splits(n, initial, horizon, step):
    raise NotImplementedError("R2: expanding-window (train_idx, test_idx) pairs")


def seasonal_naive(train, h, m):
    raise NotImplementedError("R3: repeat the last full season")


def mase(y_true, y_pred, y_train, m):
    raise NotImplementedError("R4: scaled by the in-sample seasonal-naive MAE")


class ArForecaster:
    def __init__(self, n_lags, alpha=0.0):
        self.n_lags, self.alpha = n_lags, alpha

    def fit(self, series):
        raise NotImplementedError("R5: ridge on lag features, intercept unpenalised, closed form")

    def forecast(self, h):
        raise NotImplementedError("R5: recursive multi-step forecast")


def backtest(series, fit_forecast, initial, horizon, step, m):
    raise NotImplementedError("R6: per-fold MASE array")
