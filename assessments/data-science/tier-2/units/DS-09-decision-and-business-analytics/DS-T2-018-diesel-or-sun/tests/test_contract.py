"""Contract tests: pass on the unmodified starter."""
import hashlib
import json

import pytest

from conftest import DATA, ROOT

pytestmark = pytest.mark.contract
SHA = "2a9aff2a4a4f080a2cbc454715a49bf3731d2e05d6547e0dba4d9cae21c16488"
SHA_OPT = "b9d2c64f82673cc79a58e74a66ff8a5c58e3b0a30af0adfab2ec83027e8e7c5d"


def test_prices_unmodified():
    assert hashlib.sha256(DATA.read_bytes()).hexdigest() == SHA, "diesel_prices.csv was modified"


def test_options_unmodified_and_shaped():
    p = ROOT / "resources" / "data" / "options.json"
    assert hashlib.sha256(p.read_bytes()).hexdigest() == SHA_OPT
    opts = json.loads(p.read_text())
    assert set(opts) == {"diesel", "solar_battery", "hybrid"}
    for o in opts.values():
        assert {"capex", "monthly_fixed", "litres_per_month", "replacement_month", "replacement_cost"} <= set(o)


def test_prices_shape():
    from powercost import load_prices
    df = load_prices(DATA)
    assert list(df.columns) == ["month", "price_ngn_per_litre"] and len(df) == 96


def test_api_present():
    import powercost as pc
    for n in ["fit_price_process", "simulate_paths", "simulate_paths_param_uncertainty", "pv_cost", "compare", "breakeven_price", "tornado"]:
        assert callable(getattr(pc, n)), n
