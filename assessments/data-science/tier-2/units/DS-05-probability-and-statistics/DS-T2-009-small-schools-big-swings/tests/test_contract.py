"""Contract tests: these pass on the unmodified starter."""
import hashlib
import inspect

import pytest

from conftest import DATA

pytestmark = pytest.mark.contract

SHA256 = {
    "schools.csv": "e14f7c538a421205952b605872076882e60eabbd01e43cca96ed26bc98854a12",
    "results_2022_2024.csv": "88199af03d88c1ff83d6bff1b45b48421fa551093922c3cbd23ac8f705cd4a99",
}


@pytest.mark.parametrize("name", sorted(SHA256))
def test_data_unmodified(name):
    assert hashlib.sha256((DATA / name).read_bytes()).hexdigest() == SHA256[name], f"{name} was modified"


def test_schema(results, schools):
    assert list(schools.columns) == ["school_id", "lga", "ownership", "location"]
    assert list(results.columns) == ["school_id", "year", "candidates", "credit_passes"]
    assert len(schools) == 600 and schools["school_id"].is_unique
    assert sorted(results["year"].unique()) == [2022, 2023, 2024]
    assert (results["credit_passes"] <= results["candidates"]).all() and (results["candidates"] >= 2).all()
    assert set(results["school_id"]) <= set(schools["school_id"])


def test_contract_signatures():
    import smallarea as sa
    assert sa.OUTPUT_COLUMNS == ["school_id", "estimate", "lower", "upper"]
    p = inspect.signature(sa.estimate_rates).parameters
    assert list(p)[:3] == ["results", "schools", "level"] and p["level"].default == 0.90
    assert list(inspect.signature(sa.select_schools).parameters)[:4] == ["results", "schools", "k", "which"]
