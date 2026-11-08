"""Contract tests: pass on the unmodified starter."""
import hashlib
import inspect

import numpy as np
import pytest

from conftest import DATA

pytestmark = pytest.mark.contract
EXPECTED = "a7120abfcdc72cdb810245275b93d1985b6a5202567171006ed74e369227513a"


def test_dataset_is_unmodified():
    z = np.load(DATA)
    assert hashlib.sha256(z["readings"].astype("float32").tobytes()).hexdigest() == EXPECTED, "meters.npz was modified"


def test_loader_shapes():
    from meter_audit import load_meters
    d = load_meters(DATA)
    assert d.readings.shape == (360, 28, 4) and len(d.audit_idx) == len(d.audit_y) == 100
    assert set(np.unique(d.tariff)) <= {0, 1, 2}


def test_public_api():
    import meter_audit as ma
    assert ma.METHODS == ("baseline", "iforest", "lof", "pca")
    for name in ["build_features", "score_meters", "precision_at_k", "average_precision", "evaluate_methods", "recommend"]:
        assert callable(getattr(ma, name)), name
    assert list(inspect.signature(ma.recommend).parameters)[:2] == ["data", "budget_k"]
