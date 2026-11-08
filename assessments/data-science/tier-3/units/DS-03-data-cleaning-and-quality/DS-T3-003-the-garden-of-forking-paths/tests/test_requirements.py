"""Public requirement tests: they check that your multiverse is complete, consistent and reproducible.

They say nothing about whether your decision space is GOOD. That is judged by the assessor
(README section G). They FAIL until multiverse/spec.yaml, multiverse/results.csv and
run_universe exist and agree with each other.
"""
import itertools
import math

import numpy as np
import pandas as pd
import pytest
import yaml

from conftest import MV

import multiverse

STAT_COLUMNS = ["estimate", "se", "ci_low", "ci_high", "p_value", "n_obs"]


@pytest.fixture(scope="module")
def spec():
    p = MV / "spec.yaml"
    assert p.is_file(), "multiverse/spec.yaml is missing"
    return yaml.safe_load(p.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def results():
    p = MV / "results.csv"
    assert p.is_file(), "multiverse/results.csv is missing"
    return pd.read_csv(p, dtype={"universe_id": str}, keep_default_na=False)


def _valid(spec):
    names = list(spec["decisions"])
    out = []
    for combo in itertools.product(*[spec["decisions"][n]["options"] for n in names]):
        ch = dict(zip(names, combo))
        if any(all(ch.get(k) == v for k, v in ex.items()) for ex in spec.get("exclusions") or []):
            continue
        out.append(ch)
    return names, out


def test_spec_structure(spec):
    assert spec.get("estimand") and spec.get("model")
    dec = spec["decisions"]
    assert len(dec) >= 6, "R2: at least six decisions"
    for name, d in dec.items():
        assert len(d["options"]) >= 2, name
        assert len(str(d.get("rationale", ""))) >= 40, f"{name}: give a rationale"
    assert set(spec["default"]) == set(dec)
    assert all(spec["default"][k] in dec[k]["options"] for k in dec)


def test_results_cover_the_space_exactly(spec, results):
    names, valid = _valid(spec)
    assert list(results.columns[: 1 + len(names)]) == ["universe_id"] + names
    for c in STAT_COLUMNS:
        assert c in results.columns, c
    assert results["universe_id"].is_unique
    got = {tuple(r) for r in results[names].astype(str).itertuples(index=False)}
    want = {tuple(str(ch[n]) for n in names) for ch in valid}
    assert got == want and len(results) == len(valid), "results.csv must contain every valid universe exactly once"
    assert len(valid) >= 100, "R2: the space should contain at least 100 universes"


def test_results_are_sane(results):
    est, lo, hi = results["estimate"].astype(float), results["ci_low"].astype(float), results["ci_high"].astype(float)
    assert np.isfinite(est).all()
    assert (lo <= est + 1e-12).all() and (est <= hi + 1e-12).all()
    assert (results["se"].astype(float) > 0).all()
    assert results["p_value"].astype(float).between(0, 1).all()


def test_default_universe_runs(spec):
    out = multiverse.run_universe(dict(spec["default"]))
    for c in STAT_COLUMNS:
        assert c in out, c
    assert math.isfinite(out["estimate"]) and out["n_obs"] > 0


def test_results_are_reproducible(spec, results):
    names, _ = _valid(spec)
    sample = results.sample(n=min(5, len(results)), random_state=2026)
    for _, row in sample.iterrows():
        out = multiverse.run_universe({n: row[n] for n in names})
        assert out["estimate"] == pytest.approx(float(row["estimate"]), rel=1e-6, abs=1e-9), row["universe_id"]
