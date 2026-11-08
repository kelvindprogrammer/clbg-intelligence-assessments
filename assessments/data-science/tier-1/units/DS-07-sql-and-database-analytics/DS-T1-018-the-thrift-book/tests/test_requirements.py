"""Requirement tests: one per query, plus read-only discipline. Fail on the starter."""
import json
import re

import pytest

from conftest import NAMES, QUERIES, ROOT, norm, run_query

EXPECTED = json.loads((ROOT / "tests" / "expected_public.json").read_text())


@pytest.mark.parametrize("name", NAMES)
def test_query_matches_expected(name):
    cols, rows = run_query(name)
    exp = EXPECTED[name]
    assert cols == exp["columns"], f"{name}: column names/order must be {exp['columns']}, got {cols}"
    assert norm(rows) == norm([tuple(r) for r in exp["rows"]]), f"{name}: rows differ (check ORDER BY, NULLs and join fan-out)"


def test_queries_are_read_only_selects():
    for n in NAMES:
        text = (QUERIES / f"{n}.sql").read_text(encoding="utf-8")
        body = "\n".join(l for l in text.splitlines() if not l.strip().startswith("--")).strip().lower()
        assert body.startswith(("select", "with")), n
        assert not re.search(r"\b(insert|update|delete|drop|create|alter|pragma|attach)\b", body), n


def test_no_hard_coded_answers():
    """A query that embeds more than 8 numeric literals above 999 is probably pasting results."""
    for n in NAMES:
        body = (QUERIES / f"{n}.sql").read_text(encoding="utf-8")
        assert len(re.findall(r"\b\d{4,}\b", body)) <= 8, n
