"""Contract tests: these pass on the unmodified starter."""
import hashlib
import inspect

import pandas as pd
import pytest

from conftest import DATA

pytestmark = pytest.mark.contract

SHA256 = {
    "enterprise_panel.csv": "b6ba3da296f1eec09cf03671efdbdda4e9bb1acfd8f481f1c2fba0b66d017cd4",
    "villages.csv": "65b9aefe54e40a5f711f54173b52fdb889c5de06651ce1170272c1ddfd12327b",
    "cpi_index.csv": "b0ecfda9e9c5536f7a4f045a186960fc9699f9d9a6e7316d16eb5f7159de0288",
}


@pytest.mark.parametrize("name", sorted(SHA256))
def test_data_unmodified(name):
    assert hashlib.sha256((DATA / name).read_bytes()).hexdigest() == SHA256[name], f"{name} has been modified"


def test_schemas():
    p = pd.read_csv(DATA / "enterprise_panel.csv", dtype=str, keep_default_na=False)
    assert list(p.columns) == ["record_id", "enterprise_id", "village_id", "round", "interview_date", "enterprise_type",
                               "owner_sex", "status", "grid_connected", "revenue", "revenue_period",
                               "hours_open_per_day", "employees"]
    assert set(p["round"]) == {"0", "1", "2"}
    v = pd.read_csv(DATA / "villages.csv", dtype=str, keep_default_na=False)
    assert len(v) == 60 and (v["programme_arm"] == "treatment").sum() == 30
    c = pd.read_csv(DATA / "cpi_index.csv")
    assert list(c.columns) == ["month", "index"] and c["index"].is_monotonic_increasing


def test_entry_point_signature():
    import multiverse
    assert list(inspect.signature(multiverse.run_universe).parameters) == ["choices", "data_dir"]
