"""Contract tests: pass on the unmodified starter."""
import hashlib
import inspect

import pytest

from conftest import DATA

pytestmark = pytest.mark.contract

EXPECTED_SHA256 = "39fea8a538dbfa680e0263e1bab49a3aa39d31895cbdbceeb99953d750ba66da"


def test_dataset_is_unmodified():
    assert hashlib.sha256(DATA.read_bytes()).hexdigest() == EXPECTED_SHA256, "triage_scores.csv was modified; restore it."


def test_dataset_shape(scores):
    assert list(scores.columns) == ["patient_id", "household_id", "age", "fever_days", "y_true", "risk_score"]
    assert len(scores) == 733 and scores["patient_id"].is_unique


def test_public_api_exists():
    import evalkit
    for name in ["confusion_counts", "precision_recall_f1", "roc_auc", "average_precision",
                 "stratified_group_kfold", "threshold_for_recall", "expected_calibration_error", "run_report", "main"]:
        assert callable(getattr(evalkit, name)), name


def test_signatures():
    import evalkit
    assert list(inspect.signature(evalkit.stratified_group_kfold).parameters) == ["y", "groups", "k", "seed"]
    assert list(inspect.signature(evalkit.threshold_for_recall).parameters) == ["y_true", "scores", "target_recall"]
