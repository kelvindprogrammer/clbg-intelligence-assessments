"""Contract tests: pass on the unmodified starter."""
import numpy as np
import pytest

import datagen

pytestmark = pytest.mark.contract


def test_api_exists():
    import meterlens as ml
    for n in ["conv2d", "conv_output_size", "maxpool2d", "sobel_gradients", "hog_features", "DigitReader"]:
        assert hasattr(ml, n), n


def test_datagen_deterministic_and_shaped():
    a, b = datagen.make_digits(50, seed=3), datagen.make_digits(50, seed=3)
    assert np.array_equal(a[0], b[0]) and np.array_equal(a[1], b[1]) and a[0].shape == (50, 16, 12)


def test_glyphs_are_distinct():
    gs = [datagen.glyph(d).tobytes() for d in range(10)]
    assert len(set(gs)) == 10
