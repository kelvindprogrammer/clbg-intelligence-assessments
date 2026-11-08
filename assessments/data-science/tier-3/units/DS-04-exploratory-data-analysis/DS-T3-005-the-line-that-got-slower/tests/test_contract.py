"""Contract tests: pass on the unmodified starter."""
import hashlib
import inspect

import pytest

from conftest import DATA

pytestmark = pytest.mark.contract
SHA256 = "ffaf845353e635f7f614b45801f399923c66d496cfe251b6a8d2a4f157cb3941"


def test_dataset_unmodified():
    assert hashlib.sha256(DATA.read_bytes()).hexdigest() == SHA256, "route_day.csv was modified"


def test_dataset_shape(df):
    assert list(df.columns) == ["date", "route", "operator", "trips", "mean_delay_min"]
    assert len(df) == 2880 and df["operator"].nunique() == 3 and df["route"].nunique() == 8


def test_public_api():
    import eda_lab
    for name in ["load_route_day", "headline_change", "kitagawa", "reversal_segments", "locate_instrument_break",
                 "adjusted_headline_change", "validate_ledger"]:
        assert callable(getattr(eda_lab, name)), name
    assert list(inspect.signature(eda_lab.kitagawa).parameters) == ["df", "split_date", "by"]
