"""Contract tests: pass on the unmodified starter."""
import hashlib

import pytest

from conftest import DATA

pytestmark = pytest.mark.contract
SHA = "68bd3191f1b1cb10eaa0e502c66913d30a82de75bfba96f801c50505c9e1f2dc"


def test_dataset_unmodified():
    assert hashlib.sha256(DATA.read_bytes()).hexdigest() == SHA, "applications.csv was modified"


def test_dataset_shape_and_selection_structure():
    from cutoff_lab import load_applications
    df = load_applications(DATA)
    assert list(df.columns) == ["app_id", "score", "approved", "explored", "propensity", "defaulted"]
    assert len(df) == 8000
    assert df.loc[df["defaulted"].notna(), "approved"].sum() > 0
    assert (df.loc[df["score"] >= 600, "approved"] == 1).all() and (df.loc[df["score"] < 600, "approved"] == 0).all()
    assert df.loc[df["explored"] == 1, "score"].max() < 600


def test_curve_object_is_provided():
    from cutoff_lab import DefaultCurve
    assert abs(DefaultCurve([0.0]).predict([700])[0] - 0.5) < 1e-12


def test_api_present():
    import cutoff_lab as cl
    for n in ["default_rate_by_band", "fit_default_curve", "expected_profit", "best_cutoff", "bootstrap_cutoff",
              "scenario_profits", "minimax_regret", "recommend"]:
        assert callable(getattr(cl, n)), n
