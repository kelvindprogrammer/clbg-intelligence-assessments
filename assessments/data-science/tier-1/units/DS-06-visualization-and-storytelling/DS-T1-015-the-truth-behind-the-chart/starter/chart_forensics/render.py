"""Provided plumbing: draw a spec EXACTLY as the original publisher did, distortions included.

Use it to look at the gallery (python -m chart_forensics render --out gallery_png).
Do not "fix" this file. Your honest versions belong in redraw.py.
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402


def _window(spec, df):
    flt = spec.get("filter")
    if not flt:
        return df
    col = df[flt["field"]].astype(str).tolist()
    i, j = col.index(str(flt["from"])), col.index(str(flt["to"]))
    return df.iloc[i:j + 1]


def render(spec: dict, df: pd.DataFrame):
    """Return a matplotlib Figure that reproduces the published (possibly misleading) chart."""
    d = _window(spec, df)
    fig, ax = plt.subplots(figsize=(7, 4.2))
    mark, xs = spec["mark"], spec["x"]
    xlab = d[xs["field"]].astype(str).tolist()
    pos = np.arange(len(d))
    if mark in ("bar", "area", "line"):
        y = spec["y"]
        vals = d[y["field"]].to_numpy(float)
        if mark == "bar":
            ax.bar(pos, vals, color="#c0392b")
        elif mark == "area":
            ax.fill_between(pos, vals, color="#c0392b", alpha=0.8)
        else:
            ax.plot(pos, vals, color="#c0392b", lw=2.5, marker="o")
        if y.get("scale") == "log":
            ax.set_yscale("log")
        if y.get("domain"):
            ax.set_ylim(*y["domain"])
        if y.get("reverse"):
            ax.invert_yaxis()
        ax.set_ylabel(y.get("label", ""))
        if spec.get("y2"):
            ax2 = ax.twinx()
            ax2.plot(pos, d[spec["y2"]["field"]].to_numpy(float), color="#2980b9", lw=2.5, marker="s")
            if spec["y2"].get("domain"):
                ax2.set_ylim(*spec["y2"]["domain"])
            ax2.set_ylabel(spec["y2"].get("label", ""))
        step = max(1, len(pos) // 10)
        ax.set_xticks(pos[::step], xlab[::step], rotation=45, ha="right")
    elif mark == "bubble":
        s = spec["size"]
        vals = d[s["field"]].to_numpy(float)
        if s["scale"] == "radius":
            sizes = (60.0 * vals / vals.max()) ** 2
        else:
            sizes = (60.0 ** 2) * vals / vals.max()
        ax.scatter(pos, np.zeros_like(pos), s=sizes, color="#c0392b", alpha=0.7)
        ax.set_xticks(pos, xlab)
        ax.set_yticks([])
        ax.set_xlim(-0.8, len(pos) - 0.2)
    elif mark == "heatmap":
        c = spec["color"]
        grid = d.pivot_table(index=spec["y"]["field"], columns=xs["field"], values=c["field"], sort=False)
        mesh = ax.pcolormesh(grid.to_numpy(), cmap=c["scheme"])
        fig.colorbar(mesh, ax=ax, label=c.get("label", ""))
        ax.set_xticks(np.arange(grid.shape[1]) + 0.5, [str(v) for v in grid.columns])
        ax.set_yticks(np.arange(grid.shape[0]) + 0.5, [str(v) for v in grid.index])
        ax.set_ylabel(spec["y"].get("label", ""))
    ax.set_xlabel(xs.get("label", ""))
    ax.set_title(spec.get("title", ""), fontweight="bold")
    if spec.get("source") and str(spec["source"]).strip():
        fig.text(0.01, 0.01, f"Source: {spec['source']}", fontsize=7, color="#555555")
    fig.tight_layout()
    return fig
