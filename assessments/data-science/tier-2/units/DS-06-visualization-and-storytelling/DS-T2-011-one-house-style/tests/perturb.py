"""Benign and meaningful perturbations of a rendered chart, used to test visual regression.

Benign: what a re-render on another machine might plausibly do (pixel noise, a 1-pixel shift).
Meaningful: what a regression check must catch (a bar shortened, a series recoloured, a line rescaled).
"""
from __future__ import annotations

import io

import matplotlib.image as mpimg
import numpy as np
from matplotlib.colors import to_hex


def rgb(fig) -> np.ndarray:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=100)
    buf.seek(0)
    a = mpimg.imread(buf, format="png")
    if a.shape[-1] == 4:
        a = a[..., :3] * a[..., 3:4] + (1 - a[..., 3:4])
    return a


def noisy(a, sigma=0.02, seed=0):
    return np.clip(a + np.random.default_rng(seed).normal(0, sigma, a.shape), 0, 1)


def shifted(a, px=1):
    return np.concatenate([a[:, :px], a[:, :-px]], axis=1)


def _primary_line(ax):
    lines = [ln for ln in ax.get_lines() if not ln.get_label().startswith("_") and len(ln.get_xdata()) > 2]
    return max(lines, key=lambda ln: (ln.get_zorder(), ln.get_linewidth())) if lines else None


def shorten_last_bar(fig, factor=0.7):
    ax = fig.axes[0]
    p = ax.patches[-1]
    if p.get_width() > p.get_height():
        p.set_width(p.get_width() * factor)
    else:
        p.set_height(p.get_height() * factor)
    return fig


def recolour(fig, palette):
    ax = fig.axes[0]
    if ax.patches:
        cur = to_hex(ax.patches[0].get_facecolor())
        new = next(c for c in palette if c.lower() != cur.lower())
        for p in ax.patches:
            p.set_facecolor(new)
    else:
        ln = _primary_line(ax)
        cur = to_hex(ln.get_color())
        ln.set_color(next(c for c in palette if c.lower() != cur.lower()))
    return fig


def rescale_primary_line(fig, factor=1.25):
    ln = _primary_line(fig.axes[0])
    ln.set_ydata(np.asarray(ln.get_ydata(), float) * factor)
    return fig
