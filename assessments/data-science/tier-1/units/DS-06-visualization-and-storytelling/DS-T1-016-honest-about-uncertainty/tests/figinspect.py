"""Figure-inspection helpers for DS-T1-016. They turn the R6-R8 rules into checks on Figure objects."""
from __future__ import annotations

import numpy as np
from matplotlib.collections import LineCollection, PathCollection, PolyCollection
from matplotlib.colors import to_rgba
from matplotlib.patches import Circle


def texts(fig):
    out = [t.get_text() for t in fig.texts]
    for ax in fig.axes:
        out += [t.get_text() for t in ax.texts]
        if ax.get_legend():
            out += [t.get_text() for t in ax.get_legend().get_texts()]
    return out


def has_source(fig) -> bool:
    return any(t.strip().startswith("Source:") for t in texts(fig))


def horizontal_segments(ax):
    """(x_lo, x_hi, y) for every horizontal segment drawn by LineCollections (hlines, errorbar) or 2-point lines."""
    segs = []
    for col in ax.collections:
        if isinstance(col, LineCollection):
            for s in col.get_segments():
                s = np.asarray(s)
                if len(s) == 2 and np.isclose(s[0, 1], s[1, 1]):
                    segs.append((min(s[:, 0]), max(s[:, 0]), s[0, 1]))
    for ln in ax.get_lines():
        x, y = np.asarray(ln.get_xdata(), float), np.asarray(ln.get_ydata(), float)
        if len(x) == 2 and np.isclose(y[0], y[1]):
            segs.append((x.min(), x.max(), y[0]))
    return segs


def point_positions(ax):
    """(x, y) of every marker drawn by plot(..., 'o') or scatter."""
    pts = []
    for ln in ax.get_lines():
        if ln.get_marker() not in (None, "None", "", " ") and ln.get_linestyle() in ("None", "", " ", "none"):
            pts += list(zip(np.asarray(ln.get_xdata(), float), np.asarray(ln.get_ydata(), float)))
    for col in ax.collections:
        if isinstance(col, PathCollection):
            pts += [tuple(p) for p in col.get_offsets()]
    return pts


def dot_xs(ax):
    """x positions of every dot (scatter offsets or Circle patches)."""
    xs = []
    for col in ax.collections:
        if isinstance(col, PathCollection):
            xs += list(np.asarray(col.get_offsets())[:, 0])
    xs += [p.center[0] for p in ax.patches if isinstance(p, Circle)]
    return np.sort(np.asarray(xs, float))


def bands(ax):
    """Filled polygons (fill_between) as (per-x lower, per-x upper, effective lightness, x positions)."""
    out = []
    for col in ax.collections:
        if isinstance(col, PolyCollection) and col.get_paths():
            v = col.get_paths()[0].vertices
            xs = np.unique(np.round(v[:, 0], 9))
            lo = np.array([v[np.isclose(v[:, 0], x), 1].min() for x in xs])
            hi = np.array([v[np.isclose(v[:, 0], x), 1].max() for x in xs])
            rgba = np.asarray(col.get_facecolor()[0]) if len(col.get_facecolor()) else np.asarray(to_rgba("C0"))
            eff = rgba[:3] * rgba[3] + (1 - rgba[3])          # composite over white
            lum = float(eff @ np.array([0.2126, 0.7152, 0.0722]))
            out.append((lo, hi, lum, xs))
    return out


def vertical_lines_at(ax, x):
    for ln in ax.get_lines():
        xd = np.asarray(ln.get_xdata(), float)
        if xd.size >= 2 and np.allclose(xd, x):
            return True
    return False
