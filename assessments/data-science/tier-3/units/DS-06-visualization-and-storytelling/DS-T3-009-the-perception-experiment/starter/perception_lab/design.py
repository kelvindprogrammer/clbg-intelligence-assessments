"""Experimental design. Signature is fixed; internals are yours."""
from __future__ import annotations

from .observer import ENCODINGS


def make_design(n_participants, ratios, repeats, seed, encodings=ENCODINGS):
    """Return a pandas DataFrame with columns
    participant, trial, encoding, ratio, a, b, larger_side, true_pct  (R3).

    `ratio` is smaller/larger. Every participant sees every (encoding, ratio) cell exactly `repeats` times, in a random order
    (not blocked by encoding); within each cell the larger value is on the left in half of the trials (+/- 1);
    `a` is the left value, `b` the right value; `true_pct = 100 * min(a, b) / max(a, b)`. Deterministic given `seed`.
    """
    raise NotImplementedError("R3: balanced, randomised, seeded design")
