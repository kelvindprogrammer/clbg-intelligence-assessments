"""Contract tests: these pass on the unmodified starter."""
import hashlib
import inspect

import pytest

from conftest import DATA

pytestmark = pytest.mark.contract

EXPECTED_SHA256 = "09e0e2ce3fa3e89c057b48742bfeb224908d81b105ab0ca04cb97bb919b098ae"


def test_dataset_is_unmodified():
    assert hashlib.sha256(DATA.read_bytes()).hexdigest() == EXPECTED_SHA256, "daily_rainfall.csv was modified"


def test_daily_schema(daily):
    assert list(daily.columns) == ["date", "rain_mm"]
    assert len(daily) == 16071
    assert daily["date"].min().year == 1981 and daily["date"].max().year == 2024
    assert daily["date"].is_monotonic_increasing and daily["date"].is_unique
    assert (daily["rain_mm"].dropna() >= 0).all()
    assert daily["rain_mm"].isna().sum() > 0, "the gauge record contains outages"


def test_contract_signatures():
    import eva
    for name in ["annual_maxima", "fit_gev", "gev_return_level", "return_level_ci", "decluster_runs", "fit_gpd",
                 "gpd_return_level"]:
        assert callable(getattr(eva, name)), name
    assert list(inspect.signature(eva.gpd_return_level).parameters) == ["threshold", "scale", "shape",
                                                                        "rate_per_year", "T"]
    assert eva.GEVParams(1.0, 2.0, 0.1).shape == 0.1
