"""Contract tests: these pass on the unmodified starter."""
import hashlib

import pytest

from conftest import DATA

pytestmark = pytest.mark.contract
EXPECTED_SHA256 = "eaef1e1a0559b78d8aa2cc4ea563f7b4a0fac5417e24dcdf646aeab3e1d99bfb"


def test_dataset_is_unmodified():
    assert hashlib.sha256(DATA.read_bytes()).hexdigest() == EXPECTED_SHA256, "attendance.csv was modified; restore it"


def test_dataset_shape():
    import claimcheck as cc
    df = cc.load_export(DATA)
    assert list(df.columns) == ["school_id", "group", "period", "pupil_id", "regular"]
    assert df["school_id"].nunique() == 24 and len(df) == 2880 and set(df["regular"]) == {0, 1}


def test_public_api():
    import claimcheck as cc
    for n in ["wilson_ci", "diff_in_proportions", "bootstrap_ci", "cluster_did", "verdict", "write_manifest"]:
        assert callable(getattr(cc, n)), n
