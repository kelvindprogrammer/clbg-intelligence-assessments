"""Contract tests: pass on the unmodified starter."""
import hashlib

import pytest

from conftest import DATA

pytestmark = pytest.mark.contract
SHA = "feee64181db3b2f96df1577bdf60a61eeb5902e06b157c6c9be7240b024d3392"


def test_dataset_unmodified():
    assert hashlib.sha256(DATA.read_bytes()).hexdigest() == SHA, "daily_sales.csv was modified"


def test_loads_with_expected_columns():
    from crate_planner import load_sales
    df = load_sales(DATA)
    assert list(df.columns) == ["day", "day_type", "crates_stocked", "crates_sold"]
    assert len(df) == 240 and set(df["day_type"]) == {"weekday", "market_day"}
    assert (df["crates_sold"] <= df["crates_stocked"]).all()


def test_api_present():
    import crate_planner as cp
    for n in ["critical_ratio", "expected_profit", "best_quantity", "poisson_quantity", "expected_profit_poisson",
              "censored_flags", "censored_poisson_mle", "plan_by_day_type"]:
        assert callable(getattr(cp, n)), n
