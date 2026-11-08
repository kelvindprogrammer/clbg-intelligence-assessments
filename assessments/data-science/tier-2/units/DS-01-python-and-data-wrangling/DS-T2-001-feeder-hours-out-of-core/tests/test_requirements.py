"""Public requirement tests. These FAIL on the starter until you implement meterflow.

They check correctness on the small sample and on hand-built edge cases. Performance is
assessed with your benchmark and the assessors' rerun of it, not here.
"""
import pandas as pd
import pytest

from conftest import EXPECTED, SAMPLE

import meterflow as mf


def _expected():
    return pd.read_csv(EXPECTED / "feeder_daily.csv", dtype={"feeder_id": str, "date": str})


def _assert_same(got: pd.DataFrame, exp: pd.DataFrame):
    assert list(got.columns) == list(exp.columns)
    for c, t in mf.FEEDER_DAILY_DTYPES.items():
        assert str(got[c].dtype) == t, (c, got[c].dtype)
    got = got.reset_index(drop=True)
    exp = exp.reset_index(drop=True).astype(got.dtypes.to_dict())
    pd.testing.assert_frame_equal(got, exp, check_exact=False, rtol=0, atol=1e-6)


@pytest.mark.parametrize("engine", ["pandas_inmemory", "pandas_chunked", "polars", "duckdb"])
def test_engine_matches_expected_on_sample(engine):
    _assert_same(mf.compute_feeder_daily(SAMPLE, engine, memory_limit_mb=512), _expected())


def test_compliance_matches_expected_on_sample():
    feeders = pd.read_csv(SAMPLE / "feeders.csv", dtype=str)
    got = mf.compute_compliance(_expected(), feeders)
    exp = pd.read_csv(EXPECTED / "compliance.csv", dtype={"feeder_id": str, "band": str})
    assert list(got.columns) == mf.COMPLIANCE_COLUMNS
    pd.testing.assert_frame_equal(got.reset_index(drop=True), exp.astype(got.dtypes.to_dict()),
                                  check_exact=False, rtol=0, atol=1e-6)


def _write(tmp, files: dict[str, list[tuple[str, str, float]]], meters: list[tuple[str, str]]):
    (tmp / "readings").mkdir()
    for name, rows in files.items():
        pd.DataFrame(rows, columns=["meter_id", "interval_start", "kwh"]).to_csv(tmp / "readings" / name, index=False)
    pd.DataFrame(meters, columns=["meter_id", "feeder_id"]).assign(customer_class="R2").to_csv(tmp / "meters.csv", index=False)
    pd.DataFrame({"feeder_id": sorted({f for _, f in meters}), "disco": "X", "band": "A"}).to_csv(tmp / "feeders.csv", index=False)


@pytest.mark.parametrize("engine", ["pandas_inmemory", "pandas_chunked", "polars", "duckdb"])
def test_resend_in_next_days_file_is_not_double_counted(tmp_path, engine):
    t = "2026-07-01T23:30:00+01:00"
    _write(tmp_path, {
        "2026-07-01.csv": [("M1", t, 0.5), ("M2", t, 0.0)],
        "2026-07-02.csv": [("M1", t, 0.5), ("M1", "2026-07-02T00:00:00+01:00", 0.25)],   # resend + a new reading
    }, [("M1", "F1"), ("M2", "F1")])
    out = mf.compute_feeder_daily(tmp_path, engine)
    day1 = out[out["date"] == "2026-07-01"].iloc[0]
    assert day1["energy_kwh"] == pytest.approx(0.5)
    assert day1["reporting_meters"] == 2
    assert day1["supplied_intervals"] == 1            # 1 of 2 reporting meters positive: half counts
    day2 = out[out["date"] == "2026-07-02"].iloc[0]
    assert day2["energy_kwh"] == pytest.approx(0.25) and day2["supply_hours"] == 0.5


@pytest.mark.parametrize("engine", ["pandas_inmemory", "pandas_chunked", "polars", "duckdb"])
def test_minority_positive_interval_is_not_supplied(tmp_path, engine):
    t = "2026-07-01T10:00:00+01:00"
    _write(tmp_path, {"2026-07-01.csv": [("M1", t, 0.4), ("M2", t, 0.0), ("M3", t, 0.0)]},
           [("M1", "F1"), ("M2", "F1"), ("M3", "F1"), ("M4", "F1")])
    out = mf.compute_feeder_daily(tmp_path, engine)
    assert out["supplied_intervals"].tolist() == [0]
    assert out["reporting_meters"].tolist() == [3]     # M4 never reported: not counted


def test_unknown_engine_raises():
    with pytest.raises(ValueError):
        mf.compute_feeder_daily(SAMPLE, "spark")
