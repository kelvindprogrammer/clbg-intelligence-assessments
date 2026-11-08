"""Public requirement tests. These FAIL on the starter until build_register works.

They check the contract and basic statistical hygiene only. They cannot tell you whether your
links are real: nobody can, on this data alone. The hidden suite scores your register against
the planted truth on re-generated panels. To check your method yourself, simulate panels where
you know the truth and use `score_register` (see README section D.1, R3).
"""
import time

import pytest

import rainprice as rp


@pytest.fixture(scope="module")
def reg(panel):
    t0 = time.time()
    r = rp.build_register(panel)
    r.attrs["seconds"] = time.time() - t0
    return r


def test_register_contract(reg):
    rp.validate_register(reg)


def test_runs_in_time(reg):
    assert reg.attrs["seconds"] < 300


def test_covers_every_pair(panel, reg):
    pairs = set(zip(panel.prices["state"], panel.prices["commodity"]))
    assert pairs <= set(zip(reg["state"], reg["commodity"])), "every (state, commodity) pair must appear at least once"


def test_supported_rows_are_corrected_for_multiplicity(reg):
    sup = reg[reg["status"] == "supported"]
    assert len(sup) > 0
    assert (sup["q_value"] >= sup["p_value"] - 1e-12).all(), "q_value must be a multiplicity-adjusted p_value"
    assert (sup["ci_low"] <= sup["effect"]).all() and (sup["effect"] <= sup["ci_high"]).all()


def test_selective(panel, reg):
    sup = reg[reg["status"] == "supported"]
    claimed = set(zip(sup["state"], sup["commodity"]))
    assert len(claimed) < len(panel.prices.groupby(["state", "commodity"])) / 2, "claiming most pairs is not a finding"


def test_deterministic(panel, reg):
    again = rp.build_register(panel)
    assert again.reset_index(drop=True).equals(reg.reset_index(drop=True)), "build_register must be deterministic"
