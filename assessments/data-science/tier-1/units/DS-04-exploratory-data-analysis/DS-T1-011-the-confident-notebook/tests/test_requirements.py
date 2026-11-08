"""Public requirement tests. These FAIL on the starter until you implement the package
and write outputs/audit.json.

They use tiny hand-built tables, so you can check every expected value on paper. The hidden
suite re-generates the whole dataset with other seeds, compares every corrected value with an
independent implementation, and grades your verdicts and flaw labels.
"""
import pytest
import pandas as pd

from conftest import AUDIT_CANDIDATES

import notebook_audit as na

ACT_COLS = ["agent_id", "month", "txn_count", "txn_value_ngn", "float_balance_avg_ngn", "fraud_flagged", "fraud_confirmed"]
AG_COLS = ["agent_id", "state", "lga_type", "onboard_month", "status", "churn_month", "trained", "q1_bottom_120", "coached_q2"]


def _ag(rows):
    return pd.DataFrame(rows, columns=AG_COLS)


def _act(rows):
    return pd.DataFrame(rows, columns=ACT_COLS)


def test_c1_uses_first_six_months_of_tenure_for_all_agents():
    ag = _ag([("A", "Lagos", "urban", "2023-01", "churned", "2023-04", 0, 0, 0),
              ("B", "Lagos", "urban", "2025-01", "active", "", 0, 0, 0)])
    act = _act([("A", "2023-01", 10, 0, 0, 0, 0), ("A", "2023-02", 20, 0, 0, 0, 0), ("A", "2023-03", 30, 0, 0, 0, 0),
                ("B", "2025-01", 40, 0, 0, 0, 0), ("B", "2025-06", 40, 0, 0, 0, 0), ("B", "2025-07", 999, 0, 0, 0, 0)])
    assert na.c1_cohort_ratio(ag, act) == pytest.approx(20 / 40)


def test_c2_positive_predictive_value():
    ag = _ag([("A", "Kano", "rural", "2024-01", "active", "", 0, 0, 0)])
    act = _act([("A", "2025-01", 1, 0, 0, 1, 1), ("A", "2025-02", 1, 0, 0, 1, 0), ("A", "2025-03", 1, 0, 0, 1, 0),
                ("A", "2025-04", 1, 0, 0, 0, 0), ("A", "2024-12", 1, 0, 0, 1, 1)])
    assert na.c2_ppv(ag, act) == pytest.approx(1 / 3)


def test_c3_and_c7_are_ratios_of_medians():
    ag = _ag([("L", "Lagos", "urban", "2024-01", "active", "", 0, 0, 0),
              ("K", "Kano", "rural", "2024-01", "active", "", 0, 0, 0)])
    act = _act([("L", "2025-01", 1, 100, 50, 0, 0), ("L", "2025-02", 1, 300, 70, 0, 0), ("L", "2025-03", 1, 900, 90, 0, 0),
                ("K", "2025-01", 1, 10, 10, 0, 0), ("K", "2025-02", 1, 30, 30, 0, 0)])
    assert na.c3_value_ratio(ag, act) == pytest.approx(300 / 20)
    assert na.c7_float_ratio(ag, act) == pytest.approx(70 / 20)


def test_c4_weights_by_trained_agents():
    ag = _ag([("U1", "Lagos", "urban", "2024-01", "active", "", 1, 0, 0), ("U2", "Lagos", "urban", "2024-01", "active", "", 1, 0, 0),
              ("U3", "Lagos", "urban", "2024-01", "active", "", 0, 0, 0), ("R1", "Kano", "rural", "2024-01", "active", "", 1, 0, 0),
              ("R2", "Kano", "rural", "2024-01", "active", "", 0, 0, 0)])
    act = _act([("U1", "2025-01", 220, 0, 0, 0, 0), ("U2", "2025-01", 220, 0, 0, 0, 0), ("U3", "2025-01", 200, 0, 0, 0, 0),
                ("R1", "2025-01", 120, 0, 0, 0, 0), ("R2", "2025-01", 100, 0, 0, 0, 0)])
    assert na.c4_stratified_training_ratio(ag, act) == pytest.approx((2 * 1.1 + 1 * 1.2) / 3)


def test_c5_mantel_haenszel():
    ag = _ag([("R", "S1", "rural", "2024-01", "active", "", 0, 0, 0), ("U", "S1", "urban", "2024-01", "active", "", 0, 0, 0),
              ("R2", "S2", "rural", "2024-01", "active", "", 0, 0, 0), ("U2", "S2", "urban", "2024-01", "active", "", 0, 0, 0)])
    rows = []
    for m in range(1, 5):  # S1: rural 2/4 frauds, urban 1/4
        rows += [("R", f"2025-0{m}", 1, 0, 0, 0, int(m <= 2)), ("U", f"2025-0{m}", 1, 0, 0, 0, int(m == 1))]
    for m in range(1, 3):  # S2: rural 0/2, urban 1/2
        rows += [("R2", f"2025-0{m}", 1, 0, 0, 0, 0), ("U2", f"2025-0{m}", 1, 0, 0, 0, int(m == 1))]
    expected = (2 * 4 / 8 + 0 * 2 / 4) / (1 * 4 / 8 + 1 * 2 / 4)
    assert na.c5_mh_rate_ratio(ag, _act(rows)) == pytest.approx(expected)


def test_c6_and_c8():
    ag = _ag([("C", "Oyo", "urban", "2024-01", "active", "", 0, 1, 1), ("N", "Oyo", "urban", "2024-01", "active", "", 0, 1, 0),
              ("X", "Oyo", "urban", "2024-01", "active", "", 0, 0, 0)])
    rows = []
    for m in range(1, 13):
        q2 = 4 <= m <= 6
        rows.append(("C", f"2025-{m:02d}", 130 if q2 else 100, 0, 0, int(m == 8), 0))
        rows.append(("N", f"2025-{m:02d}", 125 if q2 else 100, 0, 0, int(m in (2, 9, 10)), 0))
        rows.append(("X", f"2025-{m:02d}", 500, 0, 0, 0, 0))
    act = _act(rows)
    assert na.c6_coaching_difference(ag, act) == pytest.approx(0.30 - 0.25)
    assert na.c8_relative_flag_rate_change(ag, act) == pytest.approx((3 / 18) / (1 / 18) - 1)


def test_c9_december_ratio():
    ag = _ag([("A", "Oyo", "urban", "2024-01", "active", "", 0, 0, 0)])
    act = _act([("A", f"2025-{m:02d}", 1, 100 * m, 0, 0, 0) for m in range(1, 13)])
    assert na.c9_december_ratio(ag, act) == pytest.approx(1200 / 1100)


def test_c10_bonferroni_caps_at_one(data):
    agents, act = data
    p = na.state_churn_pvalues(agents, act)
    assert len(p) == 24 and p.between(0, 1).all()
    assert na.c10_bonferroni_min_p(agents, act) == pytest.approx(min(1.0, p.min() * 24))


def _audit_path():
    for p in AUDIT_CANDIDATES:
        if p.is_file():
            return p
    pytest.fail("outputs/audit.json not found (write it with your corrected values, see README R11)")


def test_audit_file_is_valid_and_consistent(data):
    entries = na.validate_audit(_audit_path())
    values = na.corrected_values(*data)
    for e in entries:
        assert e["corrected_value"] == pytest.approx(values[e["claim_id"]], rel=1e-4, abs=1e-6), \
            f"{e['claim_id']}: audit.json value differs from what your function computes"
    assert sum(e["verdict"] == "supported" for e in entries) not in (0, 10), "a uniform verdict is not an audit"
