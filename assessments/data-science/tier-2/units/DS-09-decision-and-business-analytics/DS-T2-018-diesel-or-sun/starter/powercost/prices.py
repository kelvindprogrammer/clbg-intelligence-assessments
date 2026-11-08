"""Fuel-price model (R1-R3)."""
import pandas as pd


def load_prices(path):
    """Provided."""
    return pd.read_csv(path)


def fit_price_process(prices):
    """R1: (mu, sigma) = mean and sample std (ddof=1) of the monthly log returns."""
    raise NotImplementedError("R1: fit_price_process")


def simulate_paths(p0, mu, sigma, months, n_paths, seed):
    """R2: (n_paths, months) array of simulated prices under a geometric random walk."""
    raise NotImplementedError("R2: simulate_paths")


def simulate_paths_param_uncertainty(prices, months, n_paths, seed):
    """R3: like R2 from the last observed price, but each path also draws its own drift."""
    raise NotImplementedError("R3: simulate_paths_param_uncertainty")
