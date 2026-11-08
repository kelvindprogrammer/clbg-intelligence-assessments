import hashlib

import pytest

from conftest import DATA

pytestmark = pytest.mark.contract


def test_dataset_unmodified():
    assert hashlib.sha256(DATA.read_bytes()).hexdigest() == "e23974d6ddf00e29b944e2ed4e7c4871ece167820f189f9a193277bb204aac5d"


def test_dataset_shape(coverage):
    Xtr, ytr, Xte, yte = coverage
    assert Xtr.shape == (750, 2) and Xte.shape == (250, 2) and set(ytr) == {0, 1}


def test_api_exists():
    import tinynet
    for n in ["init_params", "forward", "loss", "backward", "gradient_check", "train", "predict", "TrainResult"]:
        assert hasattr(tinynet, n), n
