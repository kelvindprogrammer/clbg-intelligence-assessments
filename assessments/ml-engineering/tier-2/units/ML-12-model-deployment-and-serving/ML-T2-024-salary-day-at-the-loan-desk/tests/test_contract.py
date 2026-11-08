"""Contract tests: pass on the unmodified starter."""
import numpy as np
import pytest

import datagen

pytestmark = pytest.mark.contract


def test_api_exists():
    import servesim as ss
    for n in ["calibrate_cost", "simulate", "summarize", "tune_policy"]:
        assert callable(getattr(ss, n)), n
    p = ss.Policy(8, 5.0, 64)
    assert (p.max_batch, p.max_wait_ms, p.queue_cap) == (8, 5.0, 64)


def test_datagen_deterministic_and_shaped():
    a, b = datagen.make_arrivals(4), datagen.make_arrivals(4)
    assert np.array_equal(a, b) and np.all(np.diff(a) >= 0) and 11000 < len(a) < 15000
    s, t, (ta, tb) = datagen.make_timings(4)
    assert len(s) == len(t) == 84 and 9 <= ta <= 15 and 0.6 <= tb <= 1.2
    assert len(datagen.make_arrivals(4, surge=1.25)) > len(a)
