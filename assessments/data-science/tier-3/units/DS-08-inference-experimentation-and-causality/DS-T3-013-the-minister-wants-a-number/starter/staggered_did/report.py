"""Assembly (R6)."""
import pandas as pd


def load_panel(path):
    """Provided."""
    return pd.read_csv(path, dtype={"unit_id": str})


def analyze(df, n_boot=200, seed=0):
    """R6: return {"twfe", "cs_simple", "cs_not_yet", "cs_se", "event", "pretrend_p", "twfe_minus_cs"}."""
    raise NotImplementedError("R6: analyze")
