"""Contract tests: pass on the unmodified starter."""
import pytest

import legalaid as L

pytestmark = pytest.mark.contract


def test_api_exists():
    import ragaudit as r
    for n in ["retrieval_metrics", "answer_metrics", "abstention_metrics", "bootstrap_ci", "paired_compare", "audit"]:
        assert callable(getattr(r, n)), n


def test_kb_items_deterministic_and_small():
    assert L.make_kb(2) == L.make_kb(2) and L.make_items(2) == L.make_items(2) and L.make_kb(2) != L.make_kb(3)
    items = L.make_items(2)
    assert len(items) == 60 and sum(i["answerable"] for i in items) == 40
    assert len({i["id"] for i in items}) == 60 and len(L.make_kb()) == 16


def test_system_zoo_shape_and_determinism():
    sy = L.make_system("unfaithful", seed=1)
    it = L.make_items(1)[0]
    a, b = sy(it["q"]), L.make_system("unfaithful", seed=1)(it["q"])
    assert a == b and set(a) == {"answer", "cited", "retrieved", "abstained"} and len(a["retrieved"]) == 5
    assert set(L.FLAWS) == {"retrieval_miss", "unfaithful", "parametric_leak", "citation_forgery", "position_bias",
                            "over_abstain", "under_abstain"}


def test_clean_system_mostly_correct():
    items = L.make_items(4)
    sy = L.make_system((), seed=4, noise=0.0)
    ok = sum(1 for it in items if it["answerable"] and it["gold"] in (sy(it["q"])["answer"] or ""))
    assert ok == 40
    assert all(sy(it["q"])["abstained"] for it in items if not it["answerable"])
