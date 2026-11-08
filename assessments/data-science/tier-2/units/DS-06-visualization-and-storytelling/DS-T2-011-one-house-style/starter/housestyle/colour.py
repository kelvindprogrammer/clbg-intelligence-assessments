"""Colour science and palette auditing. The function signatures are the contract; the choices are yours.

Set the constants to your house decisions and justify each one in DESIGN_RATIONALE.md.
"""
from __future__ import annotations

from dataclasses import dataclass, field

PALETTE: list[str] = []        # R5: your categorical palette (hex strings, at least 6)
BACKGROUND = "#ffffff"         # report background
MIN_CONTRAST = 3.0             # fixed by the brief: WCAG 2.x SC 1.4.11 non-text contrast
MIN_DELTA_E = 10.0             # fixed by the brief: house distinguishability bar (see README D.1)
DELTA_E_METHOD = ""            # R3: one of "CIE76", "CIE94", "CIEDE2000"
CVD_METHOD = ""                # R2: name and citation of the simulation method you implemented


def contrast_ratio(fg, bg) -> float:
    """R1: WCAG 2.x contrast ratio between two colours (hex strings or RGB in [0, 1])."""
    raise NotImplementedError("R1: implement contrast_ratio")


def simulate_cvd(rgb, kind: str):
    """R2: simulate protan, deutan or tritan dichromacy on sRGB values in [0, 1], shape (..., 3) or a hex string."""
    raise NotImplementedError("R2: implement simulate_cvd")


def delta_e(c1, c2) -> float:
    """R3: colour difference between two colours using DELTA_E_METHOD."""
    raise NotImplementedError("R3: implement delta_e")


@dataclass
class PaletteReport:
    colors: list
    min_delta_e: dict = field(default_factory=dict)      # condition -> smallest pairwise difference
    worst_pair: dict = field(default_factory=dict)       # condition -> (colour, colour)
    min_contrast: float = 0.0                           # smallest contrast against the background
    passes: bool = False


def audit_palette(colors, background: str = BACKGROUND, min_delta_e: float = MIN_DELTA_E,
                  min_contrast: float = MIN_CONTRAST) -> PaletteReport:
    """R4: audit a categorical palette under the conditions "normal", "protan", "deutan" and "tritan"."""
    raise NotImplementedError("R4: implement audit_palette")
