"""Public requirement tests (a sample; assessors run a hidden suite on freshly generated event streams)."""
import json
import random
from datetime import datetime

import pytest

from conftest import BATCHES

import incragg as ia


def ev(i, t, region="Lagos", amount=1000, version=1):
    return {"event_id": f"E{i}", "version": version, "event_time": t, "region": region, "amount_kobo": amount}


@pytest.fixture(scope="module")
def batches():
    return ia.load_batches(BATCHES)


def test_r1_new_duplicate_correction():
    a = ia.Aggregator(48)
    r = a.apply_batch([ev(1, "2026-04-06T10:00:00"), ev(2, "2026-04-06T11:00:00", "Kano", 500), ev(1, "2026-04-06T10:00:00")])
    assert (r.applied, r.duplicates, r.corrections, r.too_late) == (2, 1, 0, 0)
    assert a.totals() == {("2026-04-06", "Lagos"): (1, 1000), ("2026-04-06", "Kano"): (1, 500)}
    r = a.apply_batch([ev(1, "2026-04-06T10:00:00", "Kano", 1500, version=2), ev(2, "2026-04-06T11:00:00", "Kano", 500, version=1)])
    assert (r.applied, r.duplicates, r.corrections) == (0, 1, 1)
    assert a.totals() == {("2026-04-06", "Kano"): (2, 2000)}      # the emptied Lagos key disappears


def test_r1_too_late_uses_the_watermark_before_the_batch():
    a = ia.Aggregator(24)
    a.apply_batch([ev(1, "2026-04-10T12:00:00")])
    assert a.watermark() == datetime(2026, 4, 9, 12, 0, 0)
    r = a.apply_batch([ev(2, "2026-04-11T12:00:00"), ev(3, "2026-04-09T11:59:59"), ev(4, "2026-04-09T12:00:00")])
    # event 2 raises the max inside this batch, but event 3 is judged against the OLD watermark (apr 9 12:00)
    assert (r.applied, r.too_late) == (2, 1)
    assert [e["event_id"] for e in a.late_rejects()] == ["E3"]
    assert a.watermark() == datetime(2026, 4, 10, 12, 0, 0)


def test_r1_too_late_correction_is_ignored():
    a = ia.Aggregator(24)
    a.apply_batch([ev(1, "2026-04-06T10:00:00"), ev(2, "2026-04-08T10:00:00")])
    r = a.apply_batch([ev(1, "2026-04-06T10:00:00", amount=9999, version=2)])
    assert r.too_late == 1 and a.totals()[("2026-04-06", "Lagos")] == (1, 1000)


def test_r2_totals_on_public_batches(batches):
    a = ia.Aggregator(48)
    for b in batches:
        a.apply_batch(b)
    t = a.totals()
    assert len(t) >= 30 and all(n > 0 and amt > 0 for n, amt in t.values())
    assert sum(n for n, _ in t.values()) > 1000


def test_r3_state_is_bounded(batches):
    a = ia.Aggregator(48)
    sizes = []
    for b in batches:
        a.apply_batch(b)
        sizes.append(a.state_size())
    assert max(sizes) < sum(len(b) for b in batches) * 0.6
    assert a.state_size() < 0.4 * sum(len(b) for b in batches)


def test_r4_snapshot_round_trip_continues_exactly(batches):
    full = ia.Aggregator(48)
    for b in batches:
        full.apply_batch(b)
    part = ia.Aggregator(48)
    for b in batches[:5]:
        part.apply_batch(b)
    restored = ia.Aggregator.from_snapshot(json.loads(json.dumps(part.snapshot())))
    for b in batches[5:]:
        restored.apply_batch(b)
    assert restored.totals() == full.totals() and restored.state_size() == full.state_size()
    assert len(restored.late_rejects()) == len(full.late_rejects())


def test_r5_recompute_agrees_with_incremental(batches):
    for L in (12, 48, 96):
        a = ia.Aggregator(L)
        for b in batches:
            a.apply_batch(b)
        assert a.totals() == ia.recompute(batches, L)


def test_r5_when_nothing_is_late_batch_order_does_not_matter(batches):
    idx = list(range(len(batches)))
    random.Random(3).shuffle(idx)
    assert ia.recompute([batches[i] for i in idx], 10 ** 6) == ia.recompute(batches, 10 ** 6)


def test_r6_lateness_sweep_is_monotone(batches):
    df = ia.lateness_sweep(batches, [0, 24, 48, 96, 10 ** 6])
    assert list(df.columns) == ["lateness_hours", "too_late", "state_size_end", "accepted_share"]
    assert df["accepted_share"].is_monotonic_increasing and df["too_late"].is_monotonic_decreasing
    assert df["accepted_share"].iloc[-1] == pytest.approx(1.0) and df["too_late"].iloc[-1] == 0
