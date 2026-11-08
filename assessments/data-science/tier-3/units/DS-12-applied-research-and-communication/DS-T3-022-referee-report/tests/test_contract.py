"""Contract tests: these pass on the unmodified starter."""
import hashlib

import pytest

from conftest import DATA, ROOT

pytestmark = pytest.mark.contract
EXPECTED_SHA256 = "9a878afe80230fb3906d44f55deee2b0d38e7f6695618e164d3c478930531e35"


def test_dataset_is_unmodified():
    assert hashlib.sha256(DATA.read_bytes()).hexdigest() == EXPECTED_SHA256, "loans.csv was modified; restore it"


def test_dataset_shape_and_whitepaper_present():
    import refereekit as rk
    df = rk.load_export(DATA)
    assert len(df) == 2400 and df["cohort"].value_counts().to_dict() == {"control": 1200, "treated": 1200}
    assert {"treated", "risk_band"} <= set(df.columns) and df["defaulted"].isna().sum() == (df["matured"] == 0).sum()
    assert (ROOT / "resources" / "whitepaper.md").is_file()


def test_public_api():
    import refereekit as rk
    for n in ["simpson_check", "bh_adjust", "subgroup_scan", "censoring_check", "max_stat_permutation_p", "corrected_effect"]:
        assert callable(getattr(rk, n)), n
