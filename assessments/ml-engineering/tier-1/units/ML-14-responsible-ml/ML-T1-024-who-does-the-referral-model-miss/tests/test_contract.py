"""Contract tests: pass on the unmodified starter."""
import numpy as np
import pytest

import referralgen

pytestmark = pytest.mark.contract


def test_api_exists():
    import auditkit as ak
    for n in ["group_metrics", "disparity", "bootstrap_gap_ci", "calibration_by_group", "model_card"]:
        assert callable(getattr(ak, n)), n


def test_data_deterministic_and_shaped():
    a, b = referralgen.make_audit_data(seed=3), referralgen.make_audit_data(seed=3)
    assert all(np.array_equal(x, y) for x, y in zip(a, b))
    y, p, s, g = a
    assert len(y) == len(p) == len(s) == len(g) == 2000 and set(np.unique(y)) == {0, 1}
    assert np.all((s >= 0) & (s <= 1)) and np.array_equal(p, (s >= 0.5).astype(int))


def test_one_zone_is_small():
    _, _, _, g = referralgen.make_audit_data(seed=5)
    counts = {z: int(np.sum(g == z)) for z in np.unique(g)}
    assert len(counts) == 6 and min(counts.values()) < 30 and max(counts.values()) > 400
