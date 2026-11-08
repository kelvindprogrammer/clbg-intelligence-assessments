"""Public requirement tests (FAIL on the starter). Hidden tests use other tables, layouts and processes."""
import numpy as np
import pytest

import gridgen
import repropipe as rp

CFG = {"seed": 7, "test_frac": 0.25, "C": 1.0}


@pytest.fixture(scope="module")
def data():
    return gridgen.make_topups(seed=11)


def test_r1_representation_changes_are_ignored(data):
    X, y, names = data
    base = rp.table_fingerprint(X, y, names)
    assert len(base) == 64 and base == base.lower()
    assert rp.table_fingerprint(np.asfortranarray(X), y, names) == base
    assert rp.table_fingerprint(X.astype(np.float64).copy(), y.astype(np.int32), names) == base
    Xz = X.copy(); Xz[0, 0] = 0.0
    Xn = Xz.copy(); Xn[0, 0] = -0.0
    assert rp.table_fingerprint(Xz, y, names) == rp.table_fingerprint(Xn, y, names)


def test_r1_real_changes_are_detected(data):
    X, y, names = data
    base = rp.table_fingerprint(X, y, names)
    X2 = X.copy(); X2[5, 2] += 1e-9
    assert rp.table_fingerprint(X2, y, names) != base
    assert rp.table_fingerprint(X[::-1], y[::-1], names) != base
    assert rp.table_fingerprint(X[:, ::-1], y, names[::-1]) != base
    assert rp.table_fingerprint(X, y, ["a"] + names[1:]) != base
    y2 = y.copy(); y2[0] ^= 1
    assert rp.table_fingerprint(X, y2, names) != base


def test_r1_shape_and_nan():
    a = np.arange(24, dtype=float).reshape(4, 6)
    b = a.reshape(6, 4)
    assert rp.table_fingerprint(a, np.zeros(4), list("abcdef")) != rp.table_fingerprint(b, np.zeros(6), list("abcd"))
    n1 = a.copy(); n1[0, 0] = np.nan
    n2 = a.copy(); n2[0, 0] = -np.nan
    assert rp.table_fingerprint(n1, np.zeros(4), list("abcdef")) == rp.table_fingerprint(n2, np.zeros(4), list("abcdef"))


def test_r2_config_fingerprint():
    f = rp.config_fingerprint
    assert len(f(CFG)) == 64
    assert f({"a": 1, "b": {"x": 1, "y": [1, 2]}}) == f({"b": {"y": (1, 2), "x": 1}, "a": 1})
    assert f({"C": 0.1}) == f({"C": np.float64(0.1)})
    assert f({"seed": 7}) != f({"seed": 8}) and f({"C": 1.0}) != f({"C": 1.0000001})
    assert f({"a": {"b": 1}}) != f({"a": {"b": 2}})
    for bad in ({"s": {1, 2}}, {"a": np.arange(3)}, {"o": object()}):
        with pytest.raises(TypeError):
            f(bad)


def test_r3_split():
    tr, te = rp.split_indices(100, 5, 0.25)
    assert len(te) == 25 and len(tr) == 75 and np.all(np.diff(tr) > 0) and np.all(np.diff(te) > 0)
    assert sorted(np.concatenate([tr, te])) == list(range(100))
    perm = np.random.default_rng(5).permutation(100)
    assert set(te) == set(perm[:25])
    tr2, te2 = rp.split_indices(100, 5, 0.25)
    assert np.array_equal(te, te2) and not np.array_equal(te, rp.split_indices(100, 6, 0.25)[1])


def test_r4_train_is_deterministic_and_sane(data):
    X, y, names = data
    a, b = rp.train(CFG, X, y, names), rp.train(CFG, X.copy(), y.copy(), names)
    assert a.run_id == b.run_id and len(a.run_id) == 16
    assert np.array_equal(a.coef, b.coef) and a.intercept == b.intercept
    assert a.metrics["accuracy"] >= 0.66 and a.metrics["log_loss"] < 0.62
    assert a.code_version == rp.CODE_VERSION


def test_r4_scaler_uses_training_rows_only(data):
    X, y, names = data
    r = rp.train(CFG, X, y, names)
    tr, te = rp.split_indices(len(y), CFG["seed"], CFG["test_frac"])
    assert np.allclose(r.mean, X[tr].mean(axis=0), rtol=0, atol=1e-12)
    assert np.allclose(r.scale, X[tr].std(axis=0), rtol=0, atol=1e-12)
    p = rp.predict_proba(r, X[te])
    assert p.shape == (len(te),) and np.all((p > 0) & (p < 1))
    assert abs(np.mean((p >= 0.5) == y[te]) - r.metrics["accuracy"]) < 1e-12


def test_r4_run_id_depends_on_inputs(data):
    X, y, names = data
    base = rp.train(CFG, X, y, names)
    assert rp.train({**CFG, "seed": 8}, X, y, names).run_id != base.run_id
    assert rp.train(CFG, X[:, ::-1], y, names[::-1]).run_id != base.run_id
    assert rp.train(CFG, X, y, names).run_id == base.run_id


def test_r5_store_round_trip_and_idempotence(data, tmp_path):
    X, y, names = data
    st = rp.ArtifactStore(tmp_path)
    r = rp.train(CFG, X, y, names)
    p1 = st.save(r)
    mtime = (p1 / "manifest.json").stat().st_mtime_ns
    p2 = st.save(r)
    assert p1 == p2 and (p2 / "manifest.json").stat().st_mtime_ns == mtime
    assert st.list_runs() == [r.run_id]
    s = st.load(r.run_id)
    assert s.run_id == r.run_id and s.config == r.config and s.metrics == r.metrics
    assert np.array_equal(s.coef, r.coef) and s.intercept == r.intercept
    assert np.array_equal(s.mean, r.mean) and np.array_equal(s.scale, r.scale)
    assert st.verify(r.run_id) is True and st.verify("0" * 16) is False


def test_r5_store_detects_tampering(data, tmp_path):
    X, y, names = data
    st = rp.ArtifactStore(tmp_path)
    r = rp.train(CFG, X, y, names)
    d = st.save(r)
    z = dict(np.load(d / "weights.npz"))
    z["coef"] = z["coef"] + 1e-6
    np.savez(d / "weights.npz", **z)
    assert st.verify(r.run_id) is False
    r2 = rp.train({**CFG, "seed": 9}, X, y, names)
    d2 = st.save(r2)
    m = (d2 / "manifest.json").read_text(encoding="utf-8")
    (d2 / "manifest.json").write_text(m.replace(r2.data_fp, "0" * 64), encoding="utf-8")
    assert st.verify(r2.run_id) is False
    assert st.list_runs() == sorted([r.run_id, r2.run_id])


def test_r6_diff_runs(data):
    X, y, names = data
    a = rp.train(CFG, X, y, names)
    same = rp.diff_runs(a, rp.train(CFG, X, y, names))
    assert same == {"data": False, "config": False, "code": False, "model": False, "config_keys": []}
    d = rp.diff_runs(a, rp.train({**CFG, "C": 0.1, "seed": 8}, X, y, names))
    assert d["config"] and not d["data"] and not d["code"] and d["model"] and d["config_keys"] == ["C", "seed"]
    X2 = X.copy(); X2[0, 0] += 1.0
    assert rp.diff_runs(a, rp.train(CFG, X2, y, names))["data"] is True
