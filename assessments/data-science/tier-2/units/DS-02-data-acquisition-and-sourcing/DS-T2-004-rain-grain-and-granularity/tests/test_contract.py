"""Contract tests: these pass on the unmodified starter. They check the real recorded fixtures and the API."""
import hashlib
import inspect
import json

import pytest

from conftest import FAO, POWER

pytestmark = pytest.mark.contract

EXPECTED = {
    FAO: "7fc841d46b5f17972003a4d633e4d80f805c3bfdcee17fd1144b6bab4dcb48e6",
    POWER: "f94a894f070cfe0a45187b9b839583f9004603376120a1cabe63ff02a397d4ca",
}


@pytest.mark.parametrize("path", sorted(EXPECTED, key=str), ids=lambda p: p.name)
def test_fixture_unmodified(path):
    assert hashlib.sha256(path.read_bytes()).hexdigest() == EXPECTED[path]


def test_power_fixture_is_a_real_power_response():
    doc = json.loads(POWER.read_text(encoding="utf-8"))
    assert doc["header"]["fill_value"] == -999.0
    assert set(doc["properties"]["parameter"]) == {"PRECTOTCORR", "T2M_MAX"}
    assert len(doc["properties"]["parameter"]["PRECTOTCORR"]) == 366  # 2020 is a leap year


def test_faostat_fixture_is_wide_format():
    header = FAO.read_text(encoding="utf-8").splitlines()[0]
    assert "Y2024" in header and "Y2024F" in header and "Element" in header


def test_public_api_exists():
    import climfuse as cf
    for name in ["read_power", "season_aggregate", "weighted_mean", "read_faostat_wide", "detrend", "align"]:
        assert callable(getattr(cf, name)), name
    sig = inspect.signature(cf.season_aggregate)
    assert sig.parameters["min_coverage"].default == 0.9 and sig.parameters["how"].default == "sum"
