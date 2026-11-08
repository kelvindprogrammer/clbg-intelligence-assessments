"""R5-R6: colour science for colormap auditing.

The constants below are part of the specification (see README section D). Do not change them.
"""
from __future__ import annotations

import numpy as np  # noqa: F401  (you will need it)

LIGHTNESS_TOL = 1.0        # L* units of reversal tolerated before a profile counts as non-monotone
CENTRE_CHROMA_MAX = 40.0   # maximum C*ab at the centre sample of an acceptable diverging map
N_SAMPLES = 65             # sample the colormap at np.linspace(0, 1, N_SAMPLES)


def srgb_to_lab(rgb) -> np.ndarray:
    """R5: convert sRGB values in [0, 1] to CIELAB under the D65 white point.

    Accepts an array of shape (..., 3) or (..., 4) (an alpha channel is ignored) and
    returns an array of shape (..., 3) holding L*, a*, b*.
    """
    raise NotImplementedError("R5: implement srgb_to_lab")


def colormap_ok(cmap, scale: str) -> bool:
    """R6: True if the colormap is perceptually appropriate for the given scale.

    `cmap` is a matplotlib colormap name or a Colormap object. `scale` is
    "sequential" or "diverging"; anything else raises ValueError.
    The exact rule is in README section D.1 (R6).
    """
    raise NotImplementedError("R6: implement colormap_ok")
