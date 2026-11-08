"""Public requirement tests. These FAIL on the starter until you implement the package.

A sample only: the hidden suite re-generates reference logs from generators with other
(unknown to you) effective space sizes. Write your own tests in tests/test_member_*.py.
"""
import json
import math
import os
import subprocess
import sys

import numpy as np
import pytest

from conftest import DATA

import ref_collisions as rc


# ---------------------------------------------------------------- R1-R2
def test_classic_birthday_values():
    assert rc.p_collision_exact(23, 365) == pytest.approx(0.5072972343, rel=1e-9)
    assert rc.p_collision_exact(70, 365) == pytest.approx(0.9991595760, rel=1e-9)
    assert rc.p_collision_exact(1, 365) == 0.0
    assert rc.p_collision_exact(366, 365) == 1.0


def test_exact_is_accurate_for_tiny_probabilities():
    N = 31 ** 10
    exact = rc.p_collision_exact(1000, N)
    # For tiny probabilities, exact and Poisson agree to about n/N relative error.
    assert exact == pytest.approx(1000 * 999 / 2 / N, rel=1e-6)
    assert rc.p_collision_exact(10 ** 6, 31 ** 10) == pytest.approx(-math.expm1(-(10 ** 6) * (10 ** 6 - 1) / 2 / N), rel=1e-3)


def test_approximation_and_expected_pairs():
    assert rc.expected_colliding_pairs(25_000, 31 ** 6) == pytest.approx(25_000 * 24_999 / 2 / 31 ** 6)
    assert rc.p_collision_approx(23, 365) == pytest.approx(1 - math.exp(-23 * 22 / 730))
    assert abs(rc.p_collision_approx(23, 365) - rc.p_collision_exact(23, 365)) < 0.01


# ---------------------------------------------------------------- R3
def test_nonuniform_reduces_to_uniform_and_increases_risk():
    u = np.full(1000, 1 / 1000)
    assert rc.p_collision_nonuniform(30, u) == pytest.approx(rc.p_collision_approx(30, 1000))
    skew = np.r_[np.full(100, 0.5 / 100), np.full(900, 0.5 / 900)]
    assert rc.p_collision_nonuniform(30, skew) > rc.p_collision_nonuniform(30, u)
    with pytest.raises(ValueError):
        rc.p_collision_nonuniform(30, [0.5, 0.6])


# ---------------------------------------------------------------- R4
def test_max_n_and_min_length():
    n = rc.max_n_for_risk(365, 0.5)
    assert n == 22
    assert rc.min_code_length(10, 1000, 0.01) == 8          # 10^7 gives 0.049, 10^8 gives 0.005
    assert rc.min_code_length(31, 120_000, 0.01, guesses=10_000, guess_risk=1e-3) == 9


def test_guess_success_prob():
    assert rc.guess_success_prob(10, 1000, 1) == pytest.approx(0.01)
    assert rc.guess_success_prob(10, 1000, 100) == pytest.approx(1 - 0.99 ** 100)
    assert rc.guess_success_prob(0, 1000, 100) == 0.0


# ---------------------------------------------------------------- R5
def test_simulation_agrees_with_theory():
    iv = rc.simulate_collision_prob(30, 1000, 4000, np.random.default_rng(2026))
    assert iv.lower < rc.p_collision_exact(30, 1000) < iv.upper
    assert iv.lower <= iv.estimate <= iv.upper


# ---------------------------------------------------------------- R6-R7
def test_count_pairs():
    assert rc.count_colliding_pairs(["A", "B", "A", "C", "A", "B"]) == 3 + 1
    assert rc.count_colliding_pairs([]) == 0


def test_space_estimate_interval_covers_known_space():
    rng = np.random.default_rng(11)
    codes = rng.integers(0, 200_000, size=4_000)
    est = rc.estimate_space_size(codes.tolist())
    assert est.pairs == rc.count_colliding_pairs(codes.tolist())
    assert est.lower < 200_000 < est.upper
    assert est.n_hat == pytest.approx(4000 * 3999 / 2 / est.pairs)


def test_space_estimate_zero_pairs():
    est = rc.estimate_space_size(["AAAAAA", "BBBBBB", "CCCCCC"])
    assert est.pairs == 0 and math.isinf(est.n_hat) and math.isinf(est.upper)
    assert est.lower == pytest.approx(3 / 3.6888794541139363, rel=1e-6)   # 3 pairs / Poisson 97.5% bound for 0


def test_log_shows_excess_collisions(refs):
    day = refs[refs["date"] == "2026-10-12"]["ref"].tolist()
    assert rc.excess_collision_pvalue(day, 31 ** 6) < 1e-10
    assert rc.char_uniformity_pvalue(refs["ref"].tolist()) > 0.01   # the symbols LOOK uniform
    est = rc.estimate_space_size(refs["ref"].tolist())
    assert est.upper < 31 ** 6 / 10


def test_cli_runs(tmp_path):
    proc = subprocess.run([sys.executable, "-m", "ref_collisions", str(DATA), "--out", str(tmp_path)],
                          capture_output=True, text=True, timeout=300,
                          env={**os.environ, "PYTHONPATH": os.pathsep.join(p for p in sys.path if p)})
    assert proc.returncode == 0, proc.stderr
    ev = json.loads((tmp_path / "evidence.json").read_text(encoding="utf-8"))
    assert ev["recommended_length"] == 9 and ev["pooled"]["pairs"] > 50
