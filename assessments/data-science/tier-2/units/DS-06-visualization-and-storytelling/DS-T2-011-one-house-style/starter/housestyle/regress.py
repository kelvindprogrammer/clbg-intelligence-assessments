"""Visual regression. Signatures are the contract; the method and the tolerance are yours."""
from __future__ import annotations

TOLERANCE = None   # R8: your calibrated tolerance, in the units of signature_distance


def image_signature(img):
    """R8: a perceptual signature of a Figure, a PNG path or an RGB(A) array."""
    raise NotImplementedError("R8: implement image_signature")


def signature_distance(a, b) -> int:
    """R8: a non-negative integer distance between two signatures (0 for identical images)."""
    raise NotImplementedError("R8: implement signature_distance")


def compare_to_baseline(img, baseline_png, tolerance=TOLERANCE) -> tuple[bool, int]:
    """R8: (distance <= tolerance, distance) between an image and a committed baseline PNG."""
    raise NotImplementedError("R8: implement compare_to_baseline")
