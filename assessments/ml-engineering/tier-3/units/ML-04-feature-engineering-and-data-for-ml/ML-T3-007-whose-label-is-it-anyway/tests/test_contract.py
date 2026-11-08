"""Contract tests: pass on the unmodified starter."""
import hashlib

import pytest

from conftest import DATA, GOLD

pytestmark = pytest.mark.contract
EXPECTED_SHA256 = "c70c84182f247ed37e3703765e0a428ff16427df3a3e45de0ffce6a465937522"


def test_dataset_is_unmodified():
    assert hashlib.sha256(DATA.read_bytes()).hexdigest() == EXPECTED_SHA256, "leaf_labels.csv was modified"


def test_loader():
    from label_lab import load_labels
    d = load_labels(DATA, GOLD)
    assert d.X.shape == (1200, 12) and set(d.y) == {0, 1, 2} and set(d.annotator) == {0, 1, 2, 3}
    assert len(d.gold_idx) == len(d.gold_y) == 60


def test_public_api():
    import label_lab as ll
    for n in ["oof_proba", "estimate_noise", "select_for_relabel", "fit_robust"]:
        assert callable(getattr(ll, n)), n
