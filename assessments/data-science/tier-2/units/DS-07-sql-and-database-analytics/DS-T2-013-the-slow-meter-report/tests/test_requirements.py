"""Requirements: identical rows to the baseline, and at most MAX_RATIO of the baseline's work."""
import json
import re

import pytest

from conftest import BASELINE, NAMES, SUB, connect, indexes_sql, member_sql, run

# Reference solution reaches 0.5% (s1-s4) to 4.1% (s5) of baseline work on this database.
# 10% leaves slack for correct but less tuned designs; an un-indexed correlated subquery stays near 100%.
MAX_RATIO = 0.10
BASE_STEPS = json.loads((BASELINE.parent.parent / "tests" / "baseline_steps.json").read_text())


@pytest.fixture(scope="session")
def baseline_rows():
    con = connect()
    return {f"s{i}": run(con, (BASELINE / f"b{i}.sql").read_text())[0] for i in range(1, 6)}


@pytest.fixture(scope="session")
def member_con():
    return connect(indexes="" if not indexes_sql() else indexes_sql())


def test_indexes_file_is_only_create_index():
    text = indexes_sql()
    stmts = [s.strip() for s in text.split(";") if s.strip()]
    assert len(stmts) <= 3, "at most 3 indexes"
    assert all(re.match(r"(?is)create\s+(unique\s+)?index\s", s) for s in stmts)


@pytest.mark.parametrize("name", NAMES)
def test_same_rows_as_baseline(name, member_con, baseline_rows):
    rows, _ = run(member_con, member_sql(name))
    assert rows == baseline_rows[name], f"{name}: result differs from the baseline query"


@pytest.mark.parametrize("name", NAMES)
def test_work_is_a_fraction_of_baseline(name, member_con):
    _, steps = run(member_con, member_sql(name))
    limit = MAX_RATIO * BASE_STEPS[name]
    assert steps <= limit, f"{name}: {steps} steps > {limit:.0f} ({MAX_RATIO:.0%} of baseline {BASE_STEPS[name]})"
