"""Contract tests: pass on the unmodified starter."""
import hashlib

import pytest

from conftest import DATA

pytestmark = pytest.mark.contract


def test_datasets_unmodified():
    exp = {"dev.csv": "a166a155dc54df0f63fb75c4687b91a993c523779b7a577697380282a9006513",
           "leaderboard.csv": "e08b51332b332e02134193236ec30d3cde0d067aa04b523036e0fdbf867d7061"}
    for f, h in exp.items():
        assert hashlib.sha256((DATA / f).read_bytes()).hexdigest() == h, f"{f} was modified"


def test_data_shapes(dev, board):
    assert dev.shape == (2000, 9) and 0.06 < dev["is_fraud"].mean() < 0.09
    assert list(board.columns) == ["team_id", "submission_no", "public_auc"] and board["team_id"].nunique() == 41


def test_api_exists():
    import leaderboard_audit as la
    for n in ["auc_se_hanley", "winner_inflation", "nested_cv_auc", "paired_bootstrap_auc_diff", "required_n", "shrink_public_scores"]:
        assert callable(getattr(la, n)), n
