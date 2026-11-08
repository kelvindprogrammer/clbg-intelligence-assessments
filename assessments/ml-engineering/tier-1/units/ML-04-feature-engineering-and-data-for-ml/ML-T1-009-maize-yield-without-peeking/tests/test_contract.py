"""Contract tests: pass on the unmodified starter."""
import hashlib

import pytest

from conftest import DATA

pytestmark = pytest.mark.contract
EXPECTED_SHA256 = "0d3f8267f1fcea3a19cb7a875cdae0a6310521541df379e06671b7b6c59e2c1e"


def test_dataset_is_unmodified():
    assert hashlib.sha256(DATA.read_bytes()).hexdigest() == EXPECTED_SHA256, "farms.csv was modified"


def test_loader():
    import numpy as np
    from safeprep import load_farms
    d = load_farms(DATA)
    assert len(d["yield_t_ha"]) == 800 and np.isnan(d["rainfall_mm"]).sum() > 20
    assert len(set(d["seed_supplier"])) > 20


def test_public_api():
    import safeprep as sp
    for n in ["MedianImputer", "StandardScaler", "OneHotEncoder", "SmoothedTargetEncoder", "make_features"]:
        assert hasattr(sp, n), n
    assert hasattr(sp.SmoothedTargetEncoder, "fit_transform")
