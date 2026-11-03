"""Contract tests: these pass on the unmodified starter.

They check that the data is intact and the public API exists with the required signatures.
"""
import hashlib
import inspect

import pytest

from conftest import DATA, ROOT

pytestmark = pytest.mark.contract

EXPECTED_SHA256 = "2ab65751f0f228df66c0f0ad7575777ddd133aeb3ed643206c6c0ca38f289b5f"


def test_dataset_is_unmodified():
    digest = hashlib.sha256(DATA.read_bytes()).hexdigest()
    assert digest == EXPECTED_SHA256, "registry_export.csv has been modified. Restore the original file."


def test_dataset_shape_and_columns(raw):
    from registry_cleaner.pipeline import INPUT_COLUMNS
    assert list(raw.columns) == INPUT_COLUMNS
    assert len(raw) == 1245
    assert raw["record_id"].is_unique
    import pandas as pd
    assert all(pd.api.types.is_string_dtype(t) or t == object for t in raw.dtypes), "load_export must keep every column as text"


def test_reference_lists():
    states = (ROOT / "resources" / "reference" / "nigerian_states.txt").read_text(encoding="utf-8").split("\n")
    assert len([s for s in states if s.strip()]) == 37


def test_public_api_signatures():
    import registry_cleaner as rc
    sig = inspect.signature(rc.parse_date)
    assert "field" in sig.parameters and sig.parameters["field"].kind is inspect.Parameter.KEYWORD_ONLY
    for name in ["is_missing", "normalize_state", "normalize_department", "normalize_phone", "parse_name",
                 "parse_score", "find_duplicate_groups", "clean_registry", "load_export"]:
        assert callable(getattr(rc, name)), name


def test_parsed_date_type():
    from registry_cleaner import ParsedDate
    p = ParsedDate(None, "missing")
    assert p.status == "missing" and p.value is None
