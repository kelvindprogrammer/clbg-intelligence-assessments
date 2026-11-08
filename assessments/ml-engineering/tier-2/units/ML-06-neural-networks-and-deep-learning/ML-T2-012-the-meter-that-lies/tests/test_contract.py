import hashlib

import numpy as np
import pytest

from conftest import DATA

pytestmark = pytest.mark.contract


def test_dataset_unmodified():
    assert hashlib.sha256(DATA.read_bytes()).hexdigest() == "24e4adccd59a4de038554104eb43d15130ebc575f5cea050b8dbbef057b684c3"


def test_dataset_shape(meters):
    assert meters.shape == (2400, 13) and meters["meter_id"].is_unique and 0.06 < meters["tampered"].mean() < 0.11


def test_api_and_provided_mlp_works():
    import meterfault as mf
    for n in ["fit_preprocessor", "diagnose", "fit_model", "FittedModel", "MLP"]:
        assert hasattr(mf, n), n
    net = mf.MLP([2, 8, 1], seed=0)
    X = np.random.default_rng(0).normal(size=(200, 2))
    y = (X[:, 0] * X[:, 1] > 0).astype(int)
    for _ in range(60):
        net.fit_epoch(X, y, lr=0.01)
    assert ((net.predict_proba(X) > 0.5) == y).mean() > 0.85
