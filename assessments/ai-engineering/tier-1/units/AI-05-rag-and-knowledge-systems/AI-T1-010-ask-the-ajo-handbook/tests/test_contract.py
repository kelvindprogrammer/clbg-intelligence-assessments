"""Contract tests: pass on the unmodified starter."""
import pytest

import handbook as h

pytestmark = pytest.mark.contract


def test_api_exists():
    import ragkit as r
    for n in ["tokenize", "chunk_text", "BM25Index", "build_context", "extract_citations", "check_answer",
              "answer_question", "evaluate"]:
        assert callable(getattr(r, n)), n


def test_handbook_deterministic_and_small():
    a, b = h.make_handbook(3), h.make_handbook(3)
    assert a == b and len(a) == 10 and set(a[0]) == {"id", "title", "text"}
    assert h.make_handbook(3) != h.make_handbook(4)
    assert sum(len(d["text"]) for d in a) < 20_000


def test_questions_point_at_existing_sections():
    ids = {d["id"] for d in h.make_handbook()}
    qs = h.make_questions()
    assert len(qs) == 20 and all(q["gold"] in ids for q in qs)


def test_mock_model_modes():
    ctx = "[S01#0] Members pay monthly. Other text."
    assert h.make_model("faithful")("q", ctx) == "Members pay monthly [S01#0]."
    assert "[S99#0]" in h.make_model("forger")("q", ctx)
    assert "[" not in h.make_model("uncited")("q", ctx)
    assert h.make_model("faithful")("q", "") == "I don't know."
