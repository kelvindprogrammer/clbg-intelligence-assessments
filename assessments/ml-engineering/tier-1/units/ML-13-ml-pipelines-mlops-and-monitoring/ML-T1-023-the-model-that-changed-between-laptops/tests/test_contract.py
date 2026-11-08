"""Contract tests: pass on the unmodified starter."""
import numpy as np
import pytest

import gridgen

pytestmark = pytest.mark.contract


def test_api_exists():
    import repropipe as rp
    for n in ["table_fingerprint", "config_fingerprint", "split_indices", "train", "predict_proba",
              "ArtifactStore", "diff_runs", "Run", "CODE_VERSION"]:
        assert hasattr(rp, n), n


def test_datagen_deterministic():
    a, b = gridgen.make_topups(seed=3), gridgen.make_topups(seed=3)
    assert np.array_equal(a[0], b[0]) and np.array_equal(a[1], b[1]) and a[2] == b[2]
    assert a[0].shape == (1500, 6) and 0.2 < a[1].mean() < 0.8


def test_run_record_fields():
    import repropipe as rp
    names = ["run_id", "config", "data_fp", "config_fp", "code_version", "coef", "intercept", "mean", "scale", "metrics"]
    assert list(rp.Run.__dataclass_fields__) == names
