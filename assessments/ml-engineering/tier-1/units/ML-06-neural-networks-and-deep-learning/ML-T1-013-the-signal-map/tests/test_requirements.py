"""Public requirement tests (R1-R7)."""
import numpy as np
import pytest

import tinynet as tn


def test_r1_init_shapes_scale_and_determinism():
    p = tn.init_params([400, 300, 3], seed=1)
    assert [w.shape for w, _ in p] == [(400, 300), (300, 3)] and all((b == 0).all() for _, b in p)
    assert p[0][0].std() == pytest.approx(np.sqrt(2 / 400), rel=0.05)
    px = tn.init_params([400, 300, 3], seed=1, scheme="xavier")
    assert px[0][0].std() == pytest.approx(np.sqrt(2 / 700), rel=0.05)
    assert all((w == 0).all() for w, _ in tn.init_params([4, 5, 2], scheme="zeros"))
    assert np.array_equal(p[0][0], tn.init_params([400, 300, 3], seed=1)[0][0])
    assert not np.array_equal(p[0][0], tn.init_params([400, 300, 3], seed=2)[0][0])


def test_r2_forward_probabilities_and_stability():
    p = tn.init_params([3, 4, 3], seed=0)
    probs, _ = tn.forward(p, np.random.default_rng(0).normal(size=(5, 3)))
    assert probs.shape == (5, 3) and np.allclose(probs.sum(1), 1) and (probs >= 0).all()
    big, _ = tn.forward([(np.eye(2) * 1000.0, np.zeros(2))], np.array([[1.0, 0.0]]))
    assert np.isfinite(big).all() and big[0, 0] == pytest.approx(1.0)


def test_r3_loss_known_value_and_l2():
    probs = np.array([[0.8, 0.2], [0.3, 0.7]])
    y = np.array([0, 1])
    p = [(np.ones((2, 2)), np.ones(2))]
    assert tn.loss(probs, y, p) == pytest.approx(-(np.log(0.8) + np.log(0.7)) / 2)
    assert tn.loss(probs, y, p, l2=0.1) - tn.loss(probs, y, p) == pytest.approx(0.5 * 0.1 * 4)


@pytest.mark.parametrize("sizes,l2", [([3, 5, 4], 0.0), ([2, 6, 6, 3], 0.05)])
def test_r4_backward_matches_finite_differences(sizes, l2):
    rng = np.random.default_rng(1)
    p = tn.init_params(sizes, seed=3)
    p = [(W + rng.normal(0, 0.1, W.shape), b + rng.normal(0, 0.1, b.shape)) for W, b in p]
    X, y = rng.normal(size=(9, sizes[0])), rng.integers(0, sizes[-1], 9)
    probs, cache = tn.forward(p, X)
    grads = tn.backward(p, cache, y, l2)
    eps = 1e-6
    for li, (W, b) in enumerate(p):
        for arr, g in ((W, grads[li][0]), (b, grads[li][1])):
            assert g.shape == arr.shape
            for _ in range(6):
                idx = tuple(int(rng.integers(0, s)) for s in arr.shape)
                old = arr[idx]
                arr[idx] = old + eps
                lp = tn.loss(tn.forward(p, X)[0], y, p, l2)
                arr[idx] = old - eps
                lm = tn.loss(tn.forward(p, X)[0], y, p, l2)
                arr[idx] = old
                assert g[idx] == pytest.approx((lp - lm) / (2 * eps), rel=1e-4, abs=1e-8)


def test_r5_gradient_check_small_and_restores_params():
    rng = np.random.default_rng(2)
    p = tn.init_params([3, 4, 2], seed=0)
    before = [(W.copy(), b.copy()) for W, b in p]
    X, y = rng.normal(size=(6, 3)), rng.integers(0, 2, 6)
    assert tn.gradient_check(p, X, y, l2=0.01) < 1e-6
    assert all(np.array_equal(a[0], c[0]) and np.array_equal(a[1], c[1]) for a, c in zip(before, p))


def test_r6_two_momentum_steps_match_hand_computation():
    rng = np.random.default_rng(5)
    X, y = rng.normal(size=(20, 2)), rng.integers(0, 2, 20)
    sizes, lr, mu = [2, 4, 2], 0.1, 0.9
    p0 = tn.init_params(sizes, seed=7)
    g0 = tn.backward(p0, tn.forward(p0, X)[1], y)
    v1 = [(-lr * gW, -lr * gb) for gW, gb in g0]
    p1 = [(W + vW, b + vb) for (W, b), (vW, vb) in zip(p0, v1)]
    g1 = tn.backward(p1, tn.forward(p1, X)[1], y)
    p2 = [(W + mu * vW - lr * gW, b + mu * vb - lr * gb) for (W, b), (vW, vb), (gW, gb) in zip(p1, v1, g1)]
    res = tn.train(X, y, sizes, epochs=2, lr=lr, batch_size=20, momentum=mu, seed=7)
    for (W, b), (W2, b2) in zip(res.params, p2):
        assert np.allclose(W, W2, atol=1e-10) and np.allclose(b, b2, atol=1e-10)
    assert len(res.history) == 2


def test_r6_training_learns_the_coverage_map(coverage):
    Xtr, ytr, Xte, yte = coverage
    r = tn.train(Xtr, ytr, [2, 16, 16, 2], epochs=150, lr=0.1, batch_size=32, momentum=0.9, seed=0)
    assert r.history[-1] < 0.5 * r.history[0]
    assert (tn.predict(r.params, Xte) == yte).mean() >= 0.90


def test_r6_zero_init_cannot_learn(coverage):
    Xtr, ytr, Xte, yte = coverage
    r = tn.train(Xtr, ytr, [2, 16, 16, 2], epochs=30, lr=0.1, seed=0, init="zeros")
    assert (tn.predict(r.params, Xte) == yte).mean() <= max(yte.mean(), 1 - yte.mean()) + 0.02
    assert all((W == 0).all() for W, _ in r.params[:-1]), "dead ReLUs: hidden weights get zero gradient"


def test_r6_deterministic_and_batch_size_not_dividing_n(coverage):
    Xtr, ytr, _, _ = coverage
    a = tn.train(Xtr, ytr, [2, 8, 2], epochs=3, batch_size=37, seed=4)
    b = tn.train(Xtr, ytr, [2, 8, 2], epochs=3, batch_size=37, seed=4)
    assert all(np.array_equal(x[0], z[0]) for x, z in zip(a.params, b.params))
