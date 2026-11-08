"""Table builder for the regional report (R4)."""
import pandas as pd


def load_transactions(path):
    """Provided. Reads the export with explicit dtypes."""
    return pd.read_csv(path, dtype={"txn_id": str, "region": str, "agent_id": str, "amount_ngn": float})


def summarise_regions(df, n_boot=2000, seed=0):
    """R4: one row per region with mean/median, their intervals and a reliability flag."""
    raise NotImplementedError("R4: summarise_regions")
