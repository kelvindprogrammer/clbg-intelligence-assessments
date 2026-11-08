"""Contract tests: pass on the unmodified starter."""
import numpy as np
import pytest

import datagen

pytestmark = pytest.mark.contract


def test_api_exists():
    import modelpack as mp
    for n in ["validate_record", "fit_bundle", "encode", "save_bundle", "load_bundle", "predict"]:
        assert callable(getattr(mp, n)), n
    assert issubclass(mp.ValidationError, ValueError) and issubclass(mp.IntegrityError, Exception)


def test_validation_error_sorts_its_errors():
    import modelpack as mp
    assert mp.ValidationError([("b", "type"), ("a", "range")]).errors == [("a", "range"), ("b", "type")]


def test_datagen_deterministic_and_matches_schema():
    (r1, y1), (r2, y2) = datagen.make_vends(200, 5), datagen.make_vends(200, 5)
    assert r1 == r2 and np.array_equal(y1, y2) and 0.15 < y1.mean() < 0.7
    assert set(r1[0]) == set(datagen.SCHEMA)
