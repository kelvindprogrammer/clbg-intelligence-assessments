"""Simulated observers (PROVIDED; do not edit).

A participant judges "what percent is the smaller of the larger?" from a graphic. Judged ratio =
true_ratio ** exponent * exp(participant_effect + noise), with an encoding-specific exponent (Stevens-style
compression) and noise level. Parameters are defaults; callers may pass their own `params` for other worlds.
"""
from __future__ import annotations

import numpy as np

ENCODINGS = ("bar_common", "bar_unaligned", "pie_angle", "circle_area")
DEFAULT_PARAMS = {
    "sd": {"bar_common": 0.04, "bar_unaligned": 0.07, "pie_angle": 0.10, "circle_area": 0.18},
    "exponent": {"bar_common": 1.0, "bar_unaligned": 1.0, "pie_angle": 0.95, "circle_area": 0.70},
    "participant_sd": 0.03,
}


def simulate_responses(design, seed, params=None):
    """Return a copy of `design` (needs columns participant, encoding, true_pct) with a `judged_pct` column added."""
    p = params or DEFAULT_PARAMS
    rng = np.random.default_rng(seed)
    out = design.copy()
    effects = {pid: rng.normal(0.0, p["participant_sd"]) for pid in sorted(out["participant"].unique())}
    judged = []
    for pid, enc, true_pct in zip(out["participant"], out["encoding"], out["true_pct"]):
        ratio = (true_pct / 100.0) ** p["exponent"][enc] * np.exp(effects[pid] + rng.normal(0.0, p["sd"][enc]))
        judged.append(100.0 * min(max(ratio, 0.01), 1.0))
    out["judged_pct"] = judged
    return out
