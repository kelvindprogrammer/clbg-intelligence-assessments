"""Contract tests: pass on the unmodified starter."""
import json

import pytest

import mock_llm as m

pytestmark = pytest.mark.contract


def test_api_exists():
    import promptkit as p
    for n in ["render", "fence", "select_shots", "build_prompt", "build_prompt_within", "extract_json", "validate",
              "triage"]:
        assert callable(getattr(p, n)), n
    assert issubclass(p.ParseError, ValueError) and issubclass(p.PromptError, ValueError)


def test_examples_deterministic_and_labelled():
    a, b = m.make_examples(seed=3), m.make_examples(seed=3)
    assert a == b and len(a) == 40 and set(a[0]) == {"text", "label"}
    assert a[0]["label"] == m.rule_label(a[0]["text"])


def test_mock_modes_format_replies():
    prompt = "x\nMessage:\n<<<FARMER\nmy maize has worms\nFARMER>>>\nAnswer:"
    good = json.loads(m.MockLLM("good").complete(prompt))
    assert good == {"crop": "maize", "issue": "pest", "urgency": 1}
    assert m.MockLLM("fenced").complete(prompt).startswith("```json")
    with pytest.raises(ValueError):
        json.loads(m.MockLLM("truncated").complete(prompt))
