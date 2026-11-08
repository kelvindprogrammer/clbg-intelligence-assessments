"""Provided plumbing: load the four DS-T1-016 data files. You do not need to change this file."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

FILES = ("seed_adoption_survey", "maize_price_history", "maize_price_forecast", "march_price_samples")


def load(folder) -> dict[str, pd.DataFrame]:
    """Return {name: DataFrame} for every data file in `folder`."""
    folder = Path(folder)
    return {name: pd.read_csv(folder / f"{name}.csv") for name in FILES}
