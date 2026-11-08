"""Contract tests: pass on the unmodified starter."""
import inspect
import json

import pytest
from jsonschema import Draft202012Validator

from conftest import SCHEMA

pytestmark = pytest.mark.contract


def test_view_spec_schema_is_valid():
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    assert {"question", "data_sources", "alt_text", "uncertainty"} <= set(schema["required"])


def test_model_contract():
    from model import tariff_model as tm
    assert tm.RETURN_KEYS == ("grid_kwh", "grid_cost_ngn", "backup_kwh", "backup_cost_ngn", "unserved_kwh",
                              "total_cost_ngn", "effective_ngn_per_kwh")
    assert list(inspect.signature(tm.monthly_cost).parameters) == ["household", "scenario"]


def test_usability_contract():
    from usability import analysis
    assert list(inspect.signature(analysis.sus_score).parameters) == ["responses"]
    assert callable(analysis.summarise_sessions)
