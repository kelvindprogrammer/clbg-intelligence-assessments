"""Stimulus rendering and honesty measurement (matplotlib). Signatures are fixed; internals are yours."""
from __future__ import annotations


def render_stimulus(encoding, a, b, honest=True):
    """Return a matplotlib Figure with ONE Axes showing values a (left) and b (right) in the given encoding (R1).

    bar_common    two rectangles on a common baseline (bottom y = 0), heights a and b
    bar_unaligned two rectangles with different baselines (bottoms differ), heights a and b
    pie_angle     two Wedge patches whose angular extent is proportional to the value (same degrees-per-unit for both)
    circle_area   two Circle patches whose AREA is proportional to the value when honest=True; when honest=False the
                  radius (not the area) is made proportional to the value, reproducing a classic chart-junk lie
    Raise ValueError for an unknown encoding. Close nothing: the caller closes figures.
    """
    raise NotImplementedError("R1: draw the stimuli with honest geometry")


def displayed_ratio(fig, encoding):
    """Smaller displayed magnitude divided by the larger, measured from the artists actually drawn on `fig` (R2).
    Bars: heights. Pie: wedge angles (theta2 - theta1). Circles: areas (pi r^2)."""
    raise NotImplementedError("R2: measure the graphic, not the inputs")


def lie_factor(encoding, a, b, honest=True):
    """displayed ratio / data ratio for a freshly rendered stimulus (R2). 1.0 means the graphic is truthful.
    The figure must be closed before returning."""
    raise NotImplementedError("R2: Tufte lie factor for the ratio between two values")
