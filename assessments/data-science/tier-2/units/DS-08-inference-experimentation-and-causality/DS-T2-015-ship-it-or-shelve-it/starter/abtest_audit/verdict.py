"""End-to-end verdict (R7)."""
import pandas as pd


def load_experiment(path):
    """Provided."""
    return pd.read_csv(path, dtype={"user_id": str, "arm": str, "device": str})


def analyze_experiment(df, seed=0):
    """R7: return the structured verdict described in the README."""
    raise NotImplementedError("R7: analyze_experiment")
