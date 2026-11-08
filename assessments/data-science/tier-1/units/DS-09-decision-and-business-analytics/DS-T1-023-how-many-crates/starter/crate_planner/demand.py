"""Demand estimation from sales (R4-R5)."""
import pandas as pd


def load_sales(path):
    """Provided."""
    return pd.read_csv(path, dtype={"day_type": str})


def censored_flags(df):
    """R4: boolean Series, True where sales hit the stocking level (demand was at least that high)."""
    raise NotImplementedError("R4: censored_flags")


def censored_poisson_mle(sold, stocked):
    """R5: maximum-likelihood Poisson mean when sales are capped at stock (censored at `stocked`)."""
    raise NotImplementedError("R5: censored_poisson_mle")
