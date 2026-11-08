"""Contract tests: these pass on the unmodified starter."""
import hashlib

import pytest

from conftest import DATA

pytestmark = pytest.mark.contract
EXPECTED_SHA256 = "204aa1210c9a5f6be65b2fe58f9fc9b4948575c53ff9e62999c3fb7c6bccddc8"


def test_dataset_is_unmodified():
    assert hashlib.sha256(DATA.read_bytes()).hexdigest() == EXPECTED_SHA256, "clinic_weekly.csv was modified; restore it"


def test_dataset_shape():
    import hierfc as hf
    df = hf.load_export(DATA)
    assert list(df.columns) == ["zone", "clinic_id", "week", "visits"]
    assert df["clinic_id"].nunique() == 12 and df["week"].nunique() == 260


def test_provided_base_forecaster_and_api():
    import numpy as np
    import hierfc as hf
    f, r = hf.base_fit(np.arange(200.0) % 52 + 10, 8)
    assert f.shape == (8,) and r.shape == (156,)
    for n in ["build_hierarchy", "reconcile", "run_evaluation", "detect_transfers"]:
        assert callable(getattr(hf, n)), n
