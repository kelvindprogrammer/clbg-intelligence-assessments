"""Public requirement tests. They FAIL on the starter. Hidden tests regenerate the price history."""
import json

import numpy as np
import pytest

import powercost as pc
from conftest import DATA, ROOT

OPTS = json.loads((ROOT / "resources" / "data" / "options.json").read_text())
RATE = 0.20


# R1
def test_fit_price_process_on_known_returns():
    r = np.array([0.01, -0.02, 0.03, 0.00])
    p = 100 * np.exp(np.concatenate([[0], np.cumsum(r)]))
    mu, sigma = pc.fit_price_process(p)
    assert mu == pytest.approx(r.mean()) and sigma == pytest.approx(r.std(ddof=1))


# R2
def test_simulate_paths_follows_the_stated_construction():
    got = pc.simulate_paths(300.0, 0.01, 0.04, 12, 5, seed=3)
    z = np.random.default_rng(3).standard_normal((5, 12))
    assert got.shape == (5, 12)
    assert got == pytest.approx(300.0 * np.exp(np.cumsum(0.01 + 0.04 * z, axis=1)))


# R3
def test_parameter_uncertainty_widens_the_horizon_distribution():
    prices = pc.load_prices(DATA)["price_ngn_per_litre"].to_numpy()
    mu, sigma = pc.fit_price_process(prices)
    fixed = pc.simulate_paths(prices[-1], mu, sigma, 120, 20000, seed=1)[:, -1]
    wide = pc.simulate_paths_param_uncertainty(prices, 120, 20000, seed=1)[:, -1]
    ratio = np.log(wide).std() / np.log(fixed).std()
    assert 1.3 < ratio < 1.7  # theory: sqrt(1 + T/n) = 1.5 for T=120, n=95


# R4
def test_pv_cost_single_month_by_hand():
    opt = {"capex": 1000.0, "monthly_fixed": 10.0, "litres_per_month": 2.0, "replacement_month": None, "replacement_cost": 0}
    m = 1.2 ** (1 / 12) - 1
    got = pc.pv_cost(opt, np.array([[50.0], [80.0]]), 0.20)
    assert got == pytest.approx([1000 + (10 + 2 * 50) / (1 + m), 1000 + (10 + 2 * 80) / (1 + m)])


def test_pv_cost_includes_replacement_only_inside_the_horizon():
    opt = {"capex": 0.0, "monthly_fixed": 0.0, "litres_per_month": 0.0, "replacement_month": 6, "replacement_cost": 600.0}
    m = 1.2 ** (1 / 12) - 1
    assert pc.pv_cost(opt, np.ones((1, 12)), 0.2)[0] == pytest.approx(600 / (1 + m) ** 6)
    assert pc.pv_cost(opt, np.ones((1, 5)), 0.2)[0] == 0


# R5
def test_compare_structure_and_risk_ordering():
    paths = pc.simulate_paths(500.0, 0.01, 0.06, 120, 2000, seed=5)
    t = pc.compare(OPTS, paths, RATE)
    assert list(t.columns) == ["option", "mean", "p05", "p95", "cvar95", "prob_cheapest"]
    assert list(t["option"]) == list(OPTS)
    assert t["prob_cheapest"].sum() == pytest.approx(1.0)
    assert (t["cvar95"] >= t["p95"] - 1e-6).all() and (t["p95"] > t["mean"]).all() and (t["mean"] > t["p05"]).all()


# R6
def test_breakeven_price_equalises_present_values():
    a, b = OPTS["diesel"], OPTS["solar_battery"]
    p = pc.breakeven_price(a, b, 120, RATE)
    path = np.full((1, 120), p)
    assert pc.pv_cost(a, path, RATE)[0] == pytest.approx(pc.pv_cost(b, path, RATE)[0], rel=1e-9)
    assert pc.breakeven_price(a, dict(a), 120, RATE) != pc.breakeven_price(a, dict(a), 120, RATE)  # nan


# R7
def test_tornado_orders_by_swing_and_has_sensible_signs():
    base = {"p0": 600.0, "mu": 0.01, "annual_rate": 0.2}
    rng = {"p0": (400.0, 900.0), "mu": (0.0, 0.02), "annual_rate": (0.1, 0.3), "capex_b": (10e6, 18e6)}
    t = pc.tornado(OPTS["diesel"], OPTS["solar_battery"], base, rng)
    assert list(t.columns) == ["param", "low_diff", "high_diff", "swing"]
    assert t["swing"].is_monotonic_decreasing and set(t["param"]) == set(rng)
    row = t.set_index("param").loc["p0"]
    assert row["high_diff"] > row["low_diff"]  # dearer diesel makes diesel relatively worse (a - b rises)
    cap = t.set_index("param").loc["capex_b"]
    assert cap["low_diff"] - cap["high_diff"] == pytest.approx(8e6)  # dearer solar capex lowers PV(a) - PV(b)


# end to end on the official history
def test_official_history_story():
    prices = pc.load_prices(DATA)["price_ngn_per_litre"].to_numpy()
    mu, sigma = pc.fit_price_process(prices)
    assert 0.001 < mu < 0.011 and 0.04 < sigma < 0.06
    paths = pc.simulate_paths_param_uncertainty(prices, 120, 4000, seed=0)
    t = pc.compare(OPTS, paths, RATE).set_index("option")
    flat = np.full((1, 120), prices[-1])
    static = {k: pc.pv_cost(v, flat, RATE)[0] for k, v in OPTS.items()}
    assert static["diesel"] < static["solar_battery"]                 # the static comparison favours diesel
    assert t.loc["solar_battery", "mean"] < t.loc["diesel", "mean"]   # the stochastic one does not
    assert 0.4 < t.loc["solar_battery", "prob_cheapest"] + t.loc["hybrid", "prob_cheapest"] <= 1.0
    assert t.loc["diesel", "cvar95"] > t.loc["diesel", "p95"]
