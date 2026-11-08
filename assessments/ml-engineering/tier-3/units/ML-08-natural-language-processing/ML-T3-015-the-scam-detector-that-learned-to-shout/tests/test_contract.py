"""Contract tests: pass on the unmodified starter."""
import numpy as np
import pytest

import datagen

pytestmark = pytest.mark.contract


def test_api_exists():
    import scamguard as sg
    for n in ["subgroup_report", "bootstrap_ci", "flip_rate", "operating_threshold", "fit_detector"]:
        assert callable(getattr(sg, n)), n


def test_datagen_deterministic_three_groups():
    a, b = datagen.make_sms(200, 3, "train"), datagen.make_sms(200, 3, "train")
    assert a[0] == b[0] and np.array_equal(a[1], b[1]) and set(a[2]) == {"en", "pcm", "yo"}


def test_regimes_differ_in_how_style_relates_to_the_label():
    cue = lambda ts: np.array([t.upper() == t or "!" in t for t in ts])
    Xa, ya, _ = datagen.make_sms(1500, 1, "train")
    Xb, yb, _ = datagen.make_sms(1500, 1, "shift")
    ca, cb = cue(Xa), cue(Xb)
    assert ca[ya == 1].mean() > 0.85 > 0.15 > ca[ya == 0].mean()
    assert cb[yb == 1].mean() < 0.15 and cb[yb == 0].mean() > 0.4
