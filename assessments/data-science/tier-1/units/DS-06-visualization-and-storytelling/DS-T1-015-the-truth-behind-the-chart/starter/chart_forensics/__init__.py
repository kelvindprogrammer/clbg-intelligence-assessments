"""chart_forensics: diagnose and honestly redraw misleading charts (DS-T1-015).

The public API is fixed because the tests import it. io.py, render.py and
__main__.py are provided plumbing; colour.py, audit.py and redraw.py are yours.
"""
from .io import load_data, load_gallery, load_spec
from .render import render
from .colour import colormap_ok, srgb_to_lab
from .audit import CODES, audit, displayed_rows, lie_factor, trend_slope
from .redraw import redraw

__all__ = ["CODES", "audit", "colormap_ok", "displayed_rows", "lie_factor", "load_data", "load_gallery",
           "load_spec", "redraw", "render", "srgb_to_lab", "trend_slope"]
