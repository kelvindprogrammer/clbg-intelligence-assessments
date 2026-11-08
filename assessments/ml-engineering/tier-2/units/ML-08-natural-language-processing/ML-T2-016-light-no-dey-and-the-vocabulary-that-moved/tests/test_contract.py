"""Contract tests: pass on the unmodified starter."""
import pytest

import datagen

pytestmark = pytest.mark.contract


def test_api_exists():
    import discotriage as dt
    for n in ["typo_corrupt", "macro_f1", "route_with_budget", "build_triage"]:
        assert callable(getattr(dt, n)), n


def test_datagen_deterministic_and_imbalanced():
    a, b = datagen.make_complaints(400, seed=3), datagen.make_complaints(400, seed=3)
    assert a == b
    counts = {c: a[1].count(c) for c in datagen.CLASSES}
    assert counts["outage"] > 3 * counts["tariff"] > 0


def test_late_period_has_new_vocabulary():
    early = {w for t in datagen.make_complaints(1500, 1, "early")[0] for w in t.lower().split()}
    late = [w for t in datagen.make_complaints(600, 2, "late")[0] for w in t.lower().split()]
    assert sum(w not in early for w in late) / len(late) > 0.15
