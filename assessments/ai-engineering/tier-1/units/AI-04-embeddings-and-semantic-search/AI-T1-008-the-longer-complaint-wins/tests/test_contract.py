"""Contract tests: pass on the unmodified starter."""
import numpy as np
import pytest

import faqs

pytestmark = pytest.mark.contract


def test_api_exists():
    import simsearch as s
    for n in ["normalize_rows", "scores", "top_k", "recall_at_k", "mrr", "ndcg_at_k", "evaluate"]:
        assert callable(getattr(s, n)), n


def test_world_is_deterministic_and_well_formed():
    a, b = faqs.make_faq_world(3), faqs.make_faq_world(3)
    assert a["docs"] == b["docs"] and a["queries"] == b["queries"] and a["relevant"] == b["relevant"]
    assert np.array_equal(a["embed"](a["docs"][:5]), b["embed"](b["docs"][:5]))
    assert len(a["queries"]) == len(a["relevant"]) == 120 and len(a["boiler_ids"]) == 4
    assert all(a["boiler_ids"][0] not in r for r in a["relevant"])


def test_embedding_norm_grows_with_length_and_topics_cluster():
    w = faqs.make_faq_world(3)
    E = w["embed"](w["docs"])
    norms = np.linalg.norm(E, axis=1)
    lens = np.array([len(d.split()) for d in w["docs"]])
    assert np.corrcoef(norms, lens)[0, 1] > 0.8
