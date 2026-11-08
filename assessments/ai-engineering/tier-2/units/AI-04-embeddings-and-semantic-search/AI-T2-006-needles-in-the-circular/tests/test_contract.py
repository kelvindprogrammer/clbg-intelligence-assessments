"""Contract tests: pass on the unmodified starter."""
import numpy as np
import pytest

import circulars

pytestmark = pytest.mark.contract


def test_api_exists():
    import hybridsearch as h
    for n in ["chunk_text", "rrf", "evaluate", "build_searcher"]:
        assert callable(getattr(h, n)), n
    assert isinstance(h.BM25, type)


def test_world_deterministic_and_shaped():
    a, b = circulars.make_circular_world(3), circulars.make_circular_world(3)
    assert a["docs"] == b["docs"] and a["test"] == b["test"] and len(a["docs"]) == 60
    assert len(a["dev"][0]) == 80 and len(a["test"][0]) == 120
    assert 250 < np.mean([len(d.split()) for d in a["docs"]]) < 330
    assert set(a["test"][2]) == {"id", "topic"}


def test_each_id_query_has_exactly_one_relevant_document_that_contains_the_code():
    w = circulars.make_circular_world(3)
    qs, rel, kinds = w["test"]
    for q, r, k in zip(qs, rel, kinds):
        if k == "id":
            code = q.split()[0]
            assert len(r) == 1 and code in w["docs"][r[0]] and sum(code in d for d in w["docs"]) == 1
        else:
            assert len(r) == 5
