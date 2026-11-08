"""Contract tests: these pass on the unmodified starter.

They check that the data is intact and that the public API exists with the required signatures.
"""
import hashlib
import inspect

import pytest

from conftest import DATA

pytestmark = pytest.mark.contract

EXPECTED_SHA256 = "31021d475b5ee5e2198db17bbfe1c18682e4d9c1fbf4817c5a025c45ab7c0d50"


def test_dataset_is_unmodified():
    assert hashlib.sha256(DATA.read_bytes()).hexdigest() == EXPECTED_SHA256, \
        "admissions.csv has been modified. Restore the original file."


def test_dataset_shape_and_types(admissions):
    from paradox_ward import INPUT_COLUMNS
    assert list(admissions.columns) == INPUT_COLUMNS
    assert len(admissions) == 9600
    assert admissions["admission_id"].is_unique
    assert set(admissions["died_30d"].unique()) <= {0, 1}
    assert set(admissions["triage_category"].unique()) == {1, 2, 3, 4}
    assert admissions["hospital"].nunique() == 4


def test_public_api_signatures():
    import paradox_ward as pw
    for name in ["wilson_interval", "rate_table", "mix_table", "find_reversals", "direct_standardise",
                 "decompose_gap", "screen_stratifiers", "build_findings", "load_admissions"]:
        assert callable(getattr(pw, name)), name
    assert list(inspect.signature(pw.find_reversals).parameters) == ["df", "group_col", "stratum_col", "outcome", "min_n"]
    assert inspect.signature(pw.find_reversals).parameters["min_n"].default == 20
    assert list(inspect.signature(pw.decompose_gap).parameters)[:5] == ["df", "a", "b", "group_col", "stratum_col"]
    assert pw.CANDIDATE_STRATIFIERS == ["age_band", "sex", "triage_category", "referral_source"]
