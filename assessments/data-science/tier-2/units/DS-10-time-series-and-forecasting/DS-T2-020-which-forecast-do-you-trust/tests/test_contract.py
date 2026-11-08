"""Contract tests: these pass on the unmodified starter."""
import hashlib

import pytest

from conftest import DATA

pytestmark = pytest.mark.contract
EXPECTED_SHA256 = "c209d135e195e80ebd1ed850777a1c2fd2ae4e3863022bb6a966d0b1df9dd782"


def test_dataset_is_unmodified():
    assert hashlib.sha256(DATA.read_bytes()).hexdigest() == EXPECTED_SHA256, "feeder_daily.csv was modified; restore it"


def test_dataset_shape_and_provided_helpers():
    import fcbench as fb
    df = fb.load_export(DATA)
    assert list(df.columns) == ["feeder_id", "date", "peak_mw"] and df["feeder_id"].nunique() == 8
    s = fb.series_of(df, "FDR01")
    assert len(s) == 700 and s.index.freqstr == "D"


def test_public_api():
    import fcbench as fb
    for n in ["flag_outages", "seasonal_naive_forecast", "my_forecaster", "interval_score",
              "backtest_forecasts", "run_benchmark", "Forecast"]:
        assert callable(getattr(fb, n)), n
