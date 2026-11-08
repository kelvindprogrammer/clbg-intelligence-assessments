"""Figure-inspection helpers used by the public tests (and by assessors).

These turn the R7 rules in the README into checks on a matplotlib Figure object.
Read them: they tell you exactly how your redraws are inspected.
"""
from __future__ import annotations

import numpy as np
from matplotlib.collections import PathCollection, PolyCollection, QuadMesh
from matplotlib.container import BarContainer
from matplotlib.figure import Figure
from matplotlib.image import AxesImage

GOOD_SEQUENTIAL = {"viridis", "cividis", "magma", "inferno", "plasma", "Blues", "Greens", "Greys", "Oranges",
                   "Purples", "Reds", "YlGnBu", "YlOrRd", "YlOrBr", "BuPu", "GnBu", "PuBu", "OrRd", "cubehelix"}
GOOD_DIVERGING = {"RdBu", "BrBG", "PuOr", "coolwarm", "PiYG", "PRGn", "RdYlBu", "RdGy", "Spectral", "bwr", "seismic"}


def _base(name: str) -> str:
    return name[:-2] if name.endswith("_r") else name


def mappables(ax):
    return [m for m in list(ax.images) + list(ax.collections)
            if isinstance(m, (AxesImage, QuadMesh)) or (hasattr(m, "get_array") and m.get_array() is not None
                                                       and not isinstance(m, (PolyCollection, PathCollection)))]


def data_axes(fig: Figure):
    cbar_axes = set()
    for ax in fig.axes:
        for m in list(ax.images) + list(ax.collections):
            cb = getattr(m, "colorbar", None)
            if cb is not None:
                cbar_axes.add(cb.ax)
    return [ax for ax in fig.axes if ax not in cbar_axes]


def all_texts(fig: Figure):
    out = [t.get_text() for t in fig.texts]
    for ax in fig.axes:
        out += [t.get_text() for t in ax.texts]
    return out


def _close(a, b, rtol=1e-6):
    a, b = np.asarray(a, float), np.asarray(b, float)
    return a.shape == b.shape and np.allclose(a, b, rtol=rtol, atol=1e-9)


def series_shown(fig: Figure, values) -> bool:
    """True if some bar container, line, filled area or colour mesh shows exactly these values."""
    values = np.asarray(values, float)
    for ax in data_axes(fig):
        for c in ax.containers:
            if isinstance(c, BarContainer):
                h = [p.get_height() for p in c.patches]
                if _close(h, values):
                    return True
        for ln in ax.get_lines():
            yd = np.asarray(ln.get_ydata(), float)
            if _close(yd, values):
                return True
        for col in ax.collections:
            if isinstance(col, PolyCollection) and not isinstance(col, QuadMesh):
                ys = np.concatenate([p.vertices[:, 1] for p in col.get_paths()]) if col.get_paths() else np.array([])
                if ys.size and all(np.isclose(ys, v, rtol=1e-6).any() for v in values):
                    return True
        for m in mappables(ax):
            arr = np.ma.masked_invalid(np.asarray(m.get_array(), float)).compressed()
            if arr.size == values.size and _close(np.sort(arr), np.sort(values)):
                return True
    return False


def common_problems(fig) -> list[str]:
    """Rules that apply to every redraw."""
    probs = []
    if not isinstance(fig, Figure):
        return [f"redraw must return a matplotlib Figure, got {type(fig).__name__}"]
    axes = data_axes(fig)
    if not axes:
        return ["figure has no axes"]
    has_title = bool(fig._suptitle and fig._suptitle.get_text().strip()) or any(
        ax.get_title(loc=loc).strip() for ax in axes for loc in ("left", "center", "right"))
    if not has_title:
        probs.append("no title")
    for ax in axes:
        if not ax.get_xlabel().strip() or not ax.get_ylabel().strip():
            probs.append("an axes is missing its x or y label")
    if not any(t.strip().startswith("Source:") for t in all_texts(fig)):
        probs.append("no text starting with 'Source:'")
    return probs


def defect_problems(fig, spec: dict, df, colormap_rule=None) -> list[str]:
    """Rules that check the redraw removed each kind of distortion.

    `colormap_rule(cmap, scale) -> bool` is the full R6 rule. When it is None (public
    tests), an allowlist of well-known perceptually ordered colormaps is used instead.
    """
    probs = []
    axes = data_axes(fig)
    mark = spec["mark"]
    y = spec.get("y") or {}
    # Full record shown (fixes cherry-picked windows) and values unchanged.
    if mark == "bubble":
        field = spec["size"]["field"]
    elif mark == "heatmap":
        field = spec["color"]["field"]
    else:
        field = y["field"]
    if not series_shown(fig, df[field].to_numpy(float)):
        probs.append(f"the full, unaltered '{field}' series is not shown")
    if spec.get("y2") and not series_shown(fig, df[spec["y2"]["field"]].to_numpy(float)):
        probs.append(f"the second series '{spec['y2']['field']}' is not shown")
    # Bars and areas start at zero.
    for ax in axes:
        has_bars = any(isinstance(c, BarContainer) for c in ax.containers)
        has_area = any(isinstance(c, PolyCollection) and not isinstance(c, QuadMesh) for c in ax.collections)
        if (has_bars or has_area) and ax.get_ylim()[0] > 0:
            probs.append("bars/areas do not start at zero")
    # No twin axes.
    pos = [tuple(np.round(ax.get_position().bounds, 4)) for ax in axes]
    if len(pos) != len(set(pos)):
        probs.append("two axes occupy the same position (dual axis)")
    # Sizes proportional to values.
    vals = df[field].to_numpy(float)
    for ax in axes:
        for col in ax.collections:
            if isinstance(col, PathCollection):
                s = np.asarray(col.get_sizes(), float)
                if s.size == vals.size and s.size > 1 and np.ptp(s) > 0:
                    r = s / vals
                    if np.ptp(r) > 0.01 * r.mean():
                        probs.append("marker areas are not proportional to the values")
    # Colormaps.
    if mark == "heatmap":
        scale = spec["color"]["scale"]
        for ax in axes:
            for m in mappables(ax):
                cmap = m.get_cmap()
                if colormap_rule is not None:
                    ok = colormap_rule(cmap, scale)
                else:
                    allowed = GOOD_SEQUENTIAL if scale == "sequential" else GOOD_DIVERGING
                    ok = _base(cmap.name) in allowed
                if not ok:
                    probs.append(f"colormap '{cmap.name}' is not appropriate for a {scale} scale")
    # Quantities are not drawn upside down.
    if y.get("type") != "rank" and mark in ("bar", "area", "line"):
        for ax in axes:
            lo, hi = ax.get_ylim()
            if lo > hi:
                probs.append("a quantity axis is inverted")
    return probs
