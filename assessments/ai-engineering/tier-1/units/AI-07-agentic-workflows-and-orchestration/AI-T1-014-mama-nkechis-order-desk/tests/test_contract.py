"""Contract tests: pass on the unmodified starter."""
import pytest

import desk_model as dm

pytestmark = pytest.mark.contract


def test_api_exists():
    import orderdesk as o
    for n in ["run_workflow", "resume", "validate_graph", "build_order_desk"]:
        assert callable(getattr(o, n)), n
    assert o.END == "END"


def test_mock_classifies_and_extracts():
    m = dm.DeskModel()
    assert m.classify("I want 2 bags of rice and 1 tin of palm oil")["intent"] == "order"
    assert m.classify("the beans was spoilt")["intent"] == "complaint"
    assert m.classify("good morning")["intent"] == "other"
    assert m.extract("2 bags of rice and 1 tin of palm oil") == [{"item": "rice", "qty": 2}, {"item": "palm oil", "qty": 1}]


def test_mock_transient_failures_are_scripted():
    m = dm.DeskModel(fail_first=2)
    for _ in range(2):
        with pytest.raises(dm.TransientError):
            m.classify("x")
    assert m.classify("x")["intent"] == "other" and m.calls == 3
