"""Incremental daily revenue aggregation with late, duplicate and corrected events.
Provided: BatchReport, load_batches. Implement the rest (R1-R6)."""
from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass
class BatchReport:
    applied: int       # new events added to the totals
    duplicates: int    # redeliveries (same id, version <= the version held): ignored
    corrections: int   # same id, higher version: the totals were adjusted
    too_late: int      # event_time earlier than the watermark at the start of the batch


def load_batches(folder) -> list:
    """Provided. One list of event dicts per `*.csv` file in sorted order (= arrival order). Event keys:
    event_id, version (int), event_time (ISO 'YYYY-MM-DDTHH:MM:SS'), region, amount_kobo (int)."""
    out = []
    for p in sorted(Path(folder).glob("*.csv")):
        with open(p, encoding="utf-8", newline="") as f:
            out.append([{"event_id": r["event_id"], "version": int(r["version"]), "event_time": r["event_time"],
                         "region": r["region"], "amount_kobo": int(r["amount_kobo"])} for r in csv.DictReader(f)])
    return out


class Aggregator:
    """Maintains daily revenue per region, updated batch by batch, without ever re-reading old batches.

    Semantics (all of them are tested):
    - Batches are applied in order; events within a batch are processed in list order.
    - watermark = (max event_time over all non-too-late events accepted so far) - lateness; None before any event.
    - An event is TOO LATE if event_time < the watermark as it stood BEFORE the batch started. Too-late events
      change nothing in the totals; keep them in `late_rejects()`.
    - Otherwise: unseen event_id -> add to totals[(event_date, region)]; same id with a HIGHER version -> a
      correction: remove the old amount (and count) from the old key, add the new one to the new key (region may
      change; event_time never does); same id with version <= the one held -> duplicate, ignored.
    - totals() maps (event_date 'YYYY-MM-DD', region) -> (n_events, amount_kobo); keys whose n_events is 0 disappear.
    - MEMORY MUST BE BOUNDED: after each batch you may only retain per-event state for events that could still
      matter (i.e. whose event_time is not below the new watermark). state_size() reports the number retained.
    """

    def __init__(self, lateness_hours: int = 48):
        raise NotImplementedError("R1: Aggregator.__init__")

    def apply_batch(self, events: list) -> BatchReport:
        """R1: apply one batch under the semantics above."""
        raise NotImplementedError("R1: apply_batch")

    def watermark(self):
        """R2a: the current watermark as a datetime, or None."""
        raise NotImplementedError("R2: watermark")

    def totals(self) -> dict:
        """R2b: {(date, region): (n_events, amount_kobo)}."""
        raise NotImplementedError("R2: totals")

    def late_rejects(self) -> list:
        """R2c: the too-late event dicts, in the order rejected."""
        raise NotImplementedError("R2: late_rejects")

    def state_size(self) -> int:
        """R3: number of per-event records currently retained for duplicate/correction detection."""
        raise NotImplementedError("R3: state_size")

    def snapshot(self) -> dict:
        """R4a: a JSON-serialisable dict (survives json.dumps/json.loads) holding everything needed to continue."""
        raise NotImplementedError("R4: snapshot")

    @classmethod
    def from_snapshot(cls, snap: dict) -> "Aggregator":
        """R4b: rebuild an Aggregator from `snapshot()` (after a JSON round trip). Continuing from it must give
        exactly the same totals as an uninterrupted run."""
        raise NotImplementedError("R4: from_snapshot")


def recompute(batches: list, lateness_hours: int = 48) -> dict:
    """R5: totals from scratch for the same batches and lateness. Use it as your test oracle, and decide how to
    make it genuinely independent of Aggregator (a simple, obviously-correct, unoptimised implementation)."""
    raise NotImplementedError("R5: recompute")


def lateness_sweep(batches: list, hours_list: list) -> pd.DataFrame:
    """R6: for each lateness value return a row [lateness_hours, too_late (count), state_size_end,
    accepted_share]. accepted_share = total kobo in totals() / total kobo with an effectively unlimited lateness
    (10**6 hours). Use it to choose and defend a lateness for the business."""
    raise NotImplementedError("R6: lateness_sweep")
