"""R7: honest redraws.

Return a matplotlib Figure. The tests inspect the Figure object itself (axes limits,
labels, artists, colormaps), so draw with matplotlib and do not return an image.
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import pandas as pd  # noqa: E402


def redraw(spec: dict, df: pd.DataFrame):
    """R7: return an honest matplotlib Figure for this chart.

    It must satisfy every rule in README section D.1 (R7) for every chart in a
    gallery, including charts you have never seen.
    """
    raise NotImplementedError("R7: implement redraw")
