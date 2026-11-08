"""Public requirement tests. These FAIL on the starter until you implement the package.

They are a sample of the requirements, not the full set. Assessors run a larger hidden suite,
including on re-generated station logs with a different demand level, so code that only
satisfies these examples will not pass. Write your own tests in tests/test_member_*.py.
"""
import json
import math
import os
import subprocess
import sys

import numpy as np
import pytest

from conftest import DATA

import fuel_queue as fq


# ---------------------------------------------------------------- R1
def test_erlang_c_known_values():
    assert fq.erlang_c(1, 0.6) == pytest.approx(0.6, rel=1e-12)          # M/M/1: P(wait) = rho
    assert fq.erlang_c(2, 1.0) == pytest.approx(1 / 3, rel=1e-12)        # M/M/2 at rho = 0.5
    assert fq.erlang_b(2, 1.0) == pytest.approx(0.2, rel=1e-12)


def test_erlang_c_is_stable_for_large_c():
    p = fq.erlang_c(500, 480.0)
    assert 0.0 < p < 1.0 and math.isfinite(p)


@pytest.mark.parametrize("c,a", [(4, 4.0), (4, 4.3), (0, 1.0)])
def test_erlang_c_rejects_unstable_or_invalid(c, a):
    with pytest.raises(ValueError):
        fq.erlang_c(c, a)


# ---------------------------------------------------------------- R2
def test_mmc_metrics_mm1_and_littles_law():
    m = fq.mmc_metrics(0.5, 1.0, 1)
    assert m.wq == pytest.approx(1.0)                 # rho / (mu - lam)
    assert m.lq == pytest.approx(0.5 * m.wq)          # Little's law
    assert m.w == pytest.approx(m.wq + 1.0)
    assert m.p_wait_exceeds(0.0) == pytest.approx(m.p_wait)
    assert m.p_wait_exceeds(2.0) == pytest.approx(0.5 * math.exp(-0.5 * 2.0))


# ---------------------------------------------------------------- R3
def test_simulate_fcfs_hand_example():
    w = fq.simulate_fcfs([0, 1, 2, 3], [3, 3, 3, 3], 2)
    assert np.allclose(w, [0, 0, 1, 1])


def test_simulate_fcfs_single_pump_matches_lindley():
    rng = np.random.default_rng(1)
    arr = np.cumsum(rng.exponential(1.0, 500))
    srv = rng.exponential(0.8, 500)
    w = fq.simulate_fcfs(arr, srv, 1)
    lind = np.zeros(500)
    for i in range(1, 500):
        lind[i] = max(0.0, lind[i - 1] + srv[i - 1] - (arr[i] - arr[i - 1]))
    assert np.allclose(w, lind)


def test_simulate_fcfs_validates_input():
    with pytest.raises(ValueError):
        fq.simulate_fcfs([0, 2, 1], [1, 1, 1], 1)


# ---------------------------------------------------------------- R5
def test_batch_means_exact_arithmetic():
    iv = fq.batch_means_ci(np.arange(40.0), n_batches=4)
    assert iv.estimate == pytest.approx(19.5)
    half = 3.182446305284263 * 10 * math.sqrt(5 / 3) / 2
    assert iv.upper - iv.estimate == pytest.approx(half, rel=1e-6)


# ---------------------------------------------------------------- R6
def test_estimate_inputs_counts_demand_not_throughput(log):
    est = fq.estimate_inputs(log, 240.0)
    assert est.n_arrivals == 1303
    assert est.lam == pytest.approx(1303 / (5 * 240.0))
    assert est.n_served == int((log["status"] == "served").sum())
    assert est.cv_service > 1.15, "the service-time CV in this log is well above 1"


# ---------------------------------------------------------------- R7
def test_simulation_agrees_with_erlang_c():
    v = fq.validate_against_mmc(1.0, 0.3, 4, t=10.0, n=200_000, warmup=10_000, seed=11)
    assert v.agrees
    assert v.sim_wq.lower < v.analytic_wq < v.sim_wq.upper
    assert v.sim_wq.estimate == pytest.approx(v.analytic_wq, rel=0.10)


# ---------------------------------------------------------------- R8 (end-to-end)
@pytest.fixture(scope="module")
def rec(log):
    return fq.recommend_pumps(log)


def test_unstable_pump_counts_are_never_recommended(rec):
    t = rec.table
    assert {"c", "rho", "stable", "p_exceed_sim", "p_exceed_lower", "p_exceed_upper", "p_exceed_mmc"} <= set(t.columns)
    unstable = t[~t["stable"].astype(bool)]
    assert (unstable["rho"] >= 1).all()
    assert rec.c_recommended is not None and rec.c_recommended > unstable["c"].max()


def test_recommendation_on_official_log(rec):
    assert rec.c_recommended == 6
    assert rec.c_mmc == 5, "the M/M/c formula with the estimated mean service should under-provision here"


def test_cli_runs(tmp_path):
    proc = subprocess.run([sys.executable, "-m", "fuel_queue", str(DATA), "--out", str(tmp_path)],
                          capture_output=True, text=True, timeout=300,
                          env={**os.environ, "PYTHONPATH": os.pathsep.join(p for p in sys.path if p)})
    assert proc.returncode == 0, proc.stderr
    summary = json.loads((tmp_path / "recommendation.json").read_text(encoding="utf-8"))
    assert summary["c_recommended"] == 6
    assert (tmp_path / "pump_table.csv").exists()
