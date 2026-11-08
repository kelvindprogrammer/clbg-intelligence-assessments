"""Public requirement tests (FAIL on the starter). Hidden tests use other seeds and noise levels."""
import numpy as np
import pytest

import datagen
import meterlens as ml

RNG = np.random.default_rng(0)


def naive(img, k, s, p):
    w = np.lib.stride_tricks.sliding_window_view(np.pad(img, p), k.shape)[::s, ::s]
    return np.einsum("ijab,ab->ij", w, k)


def test_r1_output_size_formula():
    assert ml.conv_output_size(16, 3) == 14
    assert ml.conv_output_size(16, 3, stride=2, pad=1) == 8
    assert ml.conv_output_size(5, 5) == 1
    with pytest.raises(ValueError):
        ml.conv_output_size(4, 5)


def test_r1_conv_by_hand_and_no_flip():
    img = np.arange(16.0).reshape(4, 4)
    k = np.array([[1.0, 0], [0, 2.0]])          # asymmetric: a flipped kernel gives a different answer
    out = ml.conv2d(img, k)
    assert out.shape == (3, 3) and out[0, 0] == 0 * 1 + 5 * 2 and out[2, 2] == 10 * 1 + 15 * 2


@pytest.mark.parametrize("s,p", [(1, 0), (2, 0), (1, 1), (2, 1), (3, 2)])
def test_r1_conv_matches_reference_loops(s, p):
    img, k = RNG.normal(size=(11, 9)), RNG.normal(size=(3, 3))
    assert np.allclose(ml.conv2d(img, k, stride=s, pad=p), naive(img, k, s, p))


def test_r1_conv_kernel_too_large_raises():
    with pytest.raises(ValueError):
        ml.conv2d(np.ones((2, 2)), np.ones((3, 3)))


def test_r2_maxpool():
    img = np.array([[1, -5, 2, 0], [0, -1, 3, 4], [-9, -8, 1, 1], [-7, -6, 1, 2]], float)
    assert np.array_equal(ml.maxpool2d(img, 2), [[1, 4], [-6, 2]])
    assert ml.maxpool2d(np.ones((5, 5)), 2).shape == (2, 2)            # partial window dropped
    assert ml.maxpool2d(img, 2, stride=1).shape == (3, 3)
    assert ml.maxpool2d(-np.ones((4, 4)), 2).max() == -1                # no zero padding sneaking in


def test_r3_sobel_on_edges():
    img = np.zeros((8, 8)); img[:, 4:] = 1.0                           # vertical edge
    gx, gy = ml.sobel_gradients(img)
    assert gx.shape == img.shape and np.abs(gx[3, 3:5]).min() == 4.0 and np.abs(gy[2:6, 2:6]).max() == 0.0
    gx2, gy2 = ml.sobel_gradients(img.T)
    assert np.abs(gx2[2:6, 2:6]).max() == 0.0 and np.abs(gy2[3:5, 3]).min() == 4.0


def test_r4_hog_shape_norm_and_zero():
    f = ml.hog_features(RNG.normal(size=(16, 12)))
    assert f.shape == (4 * 3 * 8,) and np.linalg.norm(f) == pytest.approx(1.0)
    z = ml.hog_features(np.zeros((16, 12)))
    assert np.all(np.isfinite(z)) and np.all(z == 0)


def test_r4_hog_orientation_and_brightness():
    v = np.tile([0.0, 0.0, 1.0, 1.0] * 3, (16, 1))                                # vertical stripes: horizontal gradient -> bin 0
    h = np.tile(np.array([0.0, 0.0, 1.0, 1.0] * 4)[:, None], (1, 12))             # horizontal stripes: vertical gradient -> bin 4
    fv, fh = (ml.hog_features(a).reshape(4, 3, 8)[1:3, 1].sum(0) for a in (v, h))   # interior cells: zero padding at the border adds spurious edges
    assert fv.argmax() == 0 and fh.argmax() == 4
    d = datagen.make_digits(1, seed=1)[0][0]
    assert np.allclose(ml.hog_features(d), ml.hog_features(3.0 * d))


@pytest.fixture(scope="module")
def reader_data():
    Xt, yt = datagen.make_digits(600, seed=1)
    Xe, ye = datagen.make_digits(800, seed=2)
    return ml.DigitReader().fit(Xt, yt), Xt, yt, Xe, ye


def test_r5_fit_interface(reader_data):
    r, Xt, yt, Xe, ye = reader_data
    assert list(r.classes_) == list(range(10)) and r.centroids_.shape == (10, 96)


def test_r5_beats_raw_pixels(reader_data):
    r, Xt, yt, Xe, ye = reader_data
    acc = (r.predict(Xe) == ye).mean()
    C = np.array([Xt[yt == c].reshape(-1, 192).mean(0) for c in range(10)])
    raw = (np.argmin(((Xe.reshape(-1, 192)[:, None] - C[None]) ** 2).sum(2), 1) == ye).mean()
    assert acc >= 0.80 and acc >= 1.4 * raw, (acc, raw)


def test_r5_reject(reader_data):
    r, Xt, yt, Xe, ye = reader_data
    assert np.array_equal(r.predict_with_reject(Xe[:50], 0.0), r.predict(Xe[:50]))
    assert np.all(r.predict_with_reject(Xe[:50], 10.0) == -1)
    pred = r.predict_with_reject(Xe, 0.05)
    kept = pred != -1
    assert 0.2 < kept.mean() < 1.0 and (pred[kept] == ye[kept]).mean() > (r.predict(Xe) == ye).mean()
