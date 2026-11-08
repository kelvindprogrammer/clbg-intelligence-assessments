"""Contract tests: these pass on the unmodified starter."""
import hashlib

import pytest

from conftest import BATCHES

pytestmark = pytest.mark.contract
EXPECTED_SHA256 = "17358aeb3c4c66f83c9364a33155f7c5d97760b6be27af4ac7e6069af543c3ab"   # all batch files in name order


def test_batches_are_unmodified():
    h = hashlib.sha256()
    for p in sorted(BATCHES.glob("*.csv")):
        h.update(p.read_bytes())
    assert h.hexdigest() == EXPECTED_SHA256, "resources/data/batches was modified; restore it"


def test_batches_load():
    import incragg as ia
    b = ia.load_batches(BATCHES)
    assert len(b) == 10 and all(len(x) > 80 for x in b)
    assert set(b[0][0]) == {"event_id", "version", "event_time", "region", "amount_kobo"}


def test_public_api():
    import incragg as ia
    for n in ["apply_batch", "totals", "watermark", "late_rejects", "state_size", "snapshot", "from_snapshot"]:
        assert callable(getattr(ia.Aggregator, n)), n
    assert callable(ia.recompute) and callable(ia.lateness_sweep)
