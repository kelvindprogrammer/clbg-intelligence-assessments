"""R6-R8: honest displays of uncertainty, returned as matplotlib Figures.

The tests inspect the Figure objects (artists, limits, labels and texts), so draw
with matplotlib and return the Figure. README section D.1 lists exactly what is checked.
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import pandas as pd  # noqa: E402


def interval_plot(survey: pd.DataFrame, level: float = 0.95, *, title: str = "", source: str = ""):
    """R6: one row per group (columns state, farmers_surveyed, adopted): point estimate and Wilson interval."""
    raise NotImplementedError("R6: implement interval_plot")


def quantile_dotplot(samples, n_dots: int = 20, *, threshold: float | None = None, bin_width: float | None = None,
                     title: str = "", xlabel: str = "Value", source: str = ""):
    """R7: a quantile dotplot of n_dots dots, with an optional decision threshold."""
    raise NotImplementedError("R7: implement quantile_dotplot")


def fan_chart(history: pd.DataFrame, forecast: pd.DataFrame, levels=(0.5, 0.8, 0.95), *,
              time_col: str = "month", value_col: str = "price_ngn_per_100kg", title: str = "",
              ylabel: str = "Value", source: str = ""):
    """R8: observed history, nested central prediction bands and the median forecast."""
    raise NotImplementedError("R8: implement fan_chart")
