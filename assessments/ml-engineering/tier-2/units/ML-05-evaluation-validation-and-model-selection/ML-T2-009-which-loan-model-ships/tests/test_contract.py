"""Contract tests: pass on the unmodified starter."""
import dataclasses
import hashlib

import pytest

from conftest import DATA

pytestmark = pytest.mark.contract


def test_dataset_is_unmodified():
    assert hashlib.sha256(DATA.read_bytes()).hexdigest() == "101c7c55776395172ec2a49461743a138795c7b73ad3dcad1d1dad1eda3234af"


def test_dataset_shape(loans):
    assert len(loans) == 2708 and loans["loan_id"].is_unique
    assert loans["defaulted"].isna().sum() == 213, "213 recent loans have not matured; their label is unknown, not 0"
    assert "collection_calls_made" in loans.columns


def test_public_api_and_constants():
    import loanselect as ls
    for n in ["usable_features", "matured", "forward_splits", "expected_cost", "best_threshold", "bootstrap_ci", "select_and_fit"]:
        assert callable(getattr(ls, n)), n
    assert (ls.FN_RATE, ls.FP_RATE) == (0.6, 0.08)
    assert {f.name for f in dataclasses.fields(ls.Recommendation)} >= {"model", "threshold", "features", "model_name", "cv_cost", "cv_ci"}
