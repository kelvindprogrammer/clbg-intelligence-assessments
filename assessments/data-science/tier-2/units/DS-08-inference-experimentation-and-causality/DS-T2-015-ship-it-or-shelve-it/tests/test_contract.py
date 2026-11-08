"""Contract tests: pass on the unmodified starter."""
import hashlib

import pytest

from conftest import DATA

pytestmark = pytest.mark.contract
SHA = "c3f64f51a6721655a939bbbcffab6450b8aee942c7fb149cb39c651107545803"


def test_dataset_unmodified():
    assert hashlib.sha256(DATA.read_bytes()).hexdigest() == SHA, "experiment.csv was modified"


def test_loads_with_expected_columns():
    from abtest_audit import load_experiment
    df = load_experiment(DATA)
    assert list(df.columns) == ["user_id", "arm", "assign_day", "device", "converted", "revenue_ngn"]
    assert set(df["arm"]) == {"A", "B"} and len(df) > 7000


def test_api_present():
    import abtest_audit as ab
    for n in ["srm_check", "find_contaminated", "conversion_effect", "revenue_effect", "holm_adjust",
              "peeking_inflation", "analyze_experiment"]:
        assert callable(getattr(ab, n)), n
