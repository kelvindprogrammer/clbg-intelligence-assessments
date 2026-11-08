"""housestyle: the Naira Ledger Research chart style system (DS-T2-011).

The names in __all__ are the public contract; the tests import them.
"""
from .colour import (BACKGROUND, CVD_METHOD, DELTA_E_METHOD, MIN_CONTRAST, MIN_DELTA_E, PALETTE, PaletteReport,
                     audit_palette, contrast_ratio, delta_e, simulate_cvd)
from .theme import annotate_source, highlight, label_lines, theme
from .regress import TOLERANCE, compare_to_baseline, image_signature, signature_distance
from .report import CHARTS, build_report, make_chart

__all__ = ["BACKGROUND", "CHARTS", "CVD_METHOD", "DELTA_E_METHOD", "MIN_CONTRAST", "MIN_DELTA_E", "PALETTE",
           "PaletteReport", "TOLERANCE", "annotate_source", "audit_palette", "build_report", "compare_to_baseline",
           "contrast_ratio", "delta_e", "highlight", "image_signature", "label_lines", "make_chart",
           "signature_distance", "simulate_cvd", "theme"]
