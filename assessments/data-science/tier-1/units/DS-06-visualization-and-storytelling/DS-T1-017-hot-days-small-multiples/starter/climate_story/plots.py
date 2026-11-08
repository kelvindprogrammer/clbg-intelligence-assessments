"""R6: small multiples. Return a matplotlib Figure; the tests inspect it."""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import pandas as pd  # noqa: E402


def small_multiples(series_by_city: dict[str, pd.Series], latitudes: dict[str, float], *, title: str,
                    ylabel: str, xlabel: str = "", source: str = "NASA POWER", ncols: int = 3, sharey: bool = True,
                    kind: str = "line"):
    """R6: one panel per city, ordered north to south in reading order.

    README section D.1 (R6) lists every property the tests check.
    """
    raise NotImplementedError("R6: implement small_multiples")
