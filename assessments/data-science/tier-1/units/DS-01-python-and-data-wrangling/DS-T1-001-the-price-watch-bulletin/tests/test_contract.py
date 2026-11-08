"""Contract tests: these pass on the unmodified starter.

They check that the data is intact and that the public API exists with the required signatures.
"""
import dataclasses
import hashlib
import inspect

import pytest

from conftest import DATA

pytestmark = pytest.mark.contract

EXPECTED_SHA256 = "da5170648d618e8d8f45bb1c1182add1115be821ab37d2e334a69afdcca0ce38"


def test_dataset_is_unmodified():
    digest = hashlib.sha256(DATA.read_bytes()).hexdigest()
    assert digest == EXPECTED_SHA256, "price_watch_bulletin.csv has been modified. Restore the original file."


def test_raw_grid_is_text(raw):
    assert raw.shape == (319, 20)
    assert all(isinstance(v, str) for v in raw.to_numpy().ravel()), "load_raw must keep every cell as str"
    assert raw.iloc[0, 0].startswith("STATE FOOD PRICE WATCH")


def test_reference_data():
    import price_watch as pw
    assert len(pw.STATE_ZONES) == 37
    assert len(pw.ZONES) == 6
    assert pw.STATUSES == {"ok", "revised", "provisional", "not_collected", "not_available"}


def test_schemas_fixed():
    import price_watch as pw
    assert pw.TIDY_COLUMNS == ["item", "unit", "state", "zone", "period", "price", "status",
                               "unit_qty", "unit_base", "price_per_base"]
    assert pw.PUBLISHED_COLUMNS == ["item", "period", "area", "published"]
    assert pw.RECONCILE_COLUMNS[-1] == "match"


def test_public_api_signatures():
    import price_watch as pw
    expected = {
        "parse_price": ["cell"], "parse_periods": ["year_cells", "month_cells"], "classify_label": ["label"],
        "parse_unit": ["unit"], "split_tables": ["raw"], "tidy_bulletin": ["raw"],
        "published_averages": ["raw"], "reconcile_averages": ["tidy", "published"], "month_on_month": ["tidy"],
    }
    for name, params in expected.items():
        fn = getattr(pw, name)
        assert callable(fn), name
        assert list(inspect.signature(fn).parameters) == params, name


def test_rawtable_fields():
    import price_watch as pw
    assert [f.name for f in dataclasses.fields(pw.RawTable)] == ["number", "item", "unit", "periods", "body"]
