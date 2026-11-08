import numpy as np
import pytest

import prompt_mock as pm
import promptlab as pl

MOCK = pm.PromptMock()
BASE = pm.make_prompt()


def test_r1_evaluate_prompt_shape_and_duplicate_seeds():
    items = pm.make_eval_set(1, 50)
    m = pl.evaluate_prompt(MOCK, BASE, items, [0, 1, 2])
    assert m.shape == (50, 3) and m.dtype == bool
    assert np.array_equal(m[:, 0], MOCK.run(BASE, items, 0))
    with pytest.raises(ValueError):
        pl.evaluate_prompt(MOCK, BASE, items, [0, 0, 1])
    with pytest.raises(ValueError):
        pl.evaluate_prompt(MOCK, BASE, [], [0])


def test_r2_paired_bootstrap_basic_properties():
    z, o = np.zeros((40, 2), bool), np.ones((40, 2), bool)
    r = pl.paired_bootstrap(z, o, n_boot=200)
    assert r == {"diff": 1.0, "lo": 1.0, "hi": 1.0}
    r = pl.paired_bootstrap(o, o)
    assert r["diff"] == 0 == r["lo"] == r["hi"]
    rng = np.random.default_rng(0)
    a, b = rng.random((60, 3)) < 0.6, rng.random((60, 3)) < 0.7
    r1, r2 = pl.paired_bootstrap(a, b, seed=4), pl.paired_bootstrap(a, b, seed=4)
    assert r1 == r2 and r1["lo"] <= r1["diff"] <= r1["hi"]
    assert r1["diff"] == pytest.approx(b.mean() - a.mean())
    wide = pl.paired_bootstrap(a, b, level=0.99, seed=4)
    narrow = pl.paired_bootstrap(a, b, level=0.80, seed=4)
    assert wide["hi"] - wide["lo"] > narrow["hi"] - narrow["lo"]
    with pytest.raises(ValueError):
        pl.paired_bootstrap(a, b[:, :2])


def test_r2_resamples_items_not_cells():
    # Half the items improve in every seed, half worsen in every seed: item-level SE is large; a cell-level
    # bootstrap would shrink the interval by sqrt(seeds). Theoretical 95% half-width is about 1.96/sqrt(n).
    n, s = 100, 8
    old = np.zeros((n, s), bool)
    new = np.zeros((n, s), bool)
    new[: n // 2] = True
    old[n // 2:] = True
    r = pl.paired_bootstrap(old, new, n_boot=2000, seed=1)
    assert (r["hi"] - r["lo"]) / 2 > 0.8 * 1.96 / np.sqrt(n)


def test_r3_required_items():
    assert pl.required_items(0.3, 0.03) == 785
    assert pl.required_items(0.3, 0.06) < pl.required_items(0.3, 0.03)
    assert pl.required_items(0.3, 0.03, power=0.9) > 785
    with pytest.raises(ValueError):
        pl.required_items(0.3, 0)


def test_r4_check_leakage_normalises_case_and_whitespace():
    items = pm.make_eval_set(5, 40)
    leaked = items[7]["text"]
    prompt = BASE + "\nExample [en]: " + leaked.upper().replace(" ", "  ") + " => balance"
    assert pl.check_leakage(prompt, items) == [items[7]["id"]]
    assert pl.check_leakage(BASE, items) == []


def _rand(p, shape, rng):
    return rng.random(shape) < p


def test_r5_gate_structure_and_obvious_cases():
    rng = np.random.default_rng(0)
    old = _rand(0.6, (200, 3), rng)
    sl = {"all2": np.ones(200, bool)}
    better = pl.regression_gate(old, _rand(0.8, (200, 3), rng), sl)
    assert set(better) >= {"decision", "reasons", "overall", "slices"} and better["decision"] == "ship"
    worse = pl.regression_gate(old, _rand(0.4, (200, 3), rng), sl)
    assert worse["decision"] == "block" and worse["reasons"] and "overall" in " ".join(worse["reasons"])


def test_r5_gate_is_deterministic_and_does_not_mutate():
    rng = np.random.default_rng(1)
    old, new = _rand(0.6, (120, 3), rng), _rand(0.58, (120, 3), rng)
    sl = {"g": np.arange(120) < 60}
    o2, n2 = old.copy(), new.copy()
    a, b = pl.regression_gate(old, new, sl, seed=3), pl.regression_gate(old, new, sl, seed=3)
    assert a == b and np.array_equal(old, o2) and np.array_equal(new, n2)


def test_r5_subgroup_regression_hidden_by_overall_gain_is_blocked_and_named():
    rng = np.random.default_rng(2)
    old = np.vstack([_rand(0.7, (300, 3), rng), _rand(0.7, (100, 3), rng)])
    new = np.vstack([_rand(0.76, (300, 3), rng), _rand(0.45, (100, 3), rng)])
    assert new.mean() > old.mean() - 0.02
    sl = {"majority": np.arange(400) < 300, "minority": np.arange(400) >= 300}
    r = pl.regression_gate(old, new, sl)
    assert r["decision"] == "block" and any("minority" in x for x in r["reasons"])


def test_r5_tiny_slices_are_not_tested():
    rng = np.random.default_rng(3)
    old, new = _rand(0.7, (100, 2), rng), _rand(0.7, (100, 2), rng)
    r = pl.regression_gate(old, new, {"tiny": np.arange(100) < 5, "big": np.arange(100) >= 50})
    assert "tiny" not in r["slices"] and "big" in r["slices"]


def test_r6_operating_characteristics_counts_decisions():
    seq = iter(["block", "ship", "ship", "inconclusive"])
    out = pl.operating_characteristics(lambda t: (np.zeros((2, 1)), np.zeros((2, 1)), {}),
                                       lambda o, n, s, seed=0: {"decision": next(seq)}, trials=4)
    assert out == {"block_rate": 0.25, "ship_rate": 0.5, "inconclusive_rate": 0.25}


def pair_maker(old_prompt, new_prompt, n=300, seeds=3):
    def mk(t):
        items = pm.make_eval_set(t, n)
        old = pl.evaluate_prompt(MOCK, old_prompt, items, list(range(seeds)))
        new = pl.evaluate_prompt(MOCK, new_prompt, items, list(range(100, 100 + seeds)))
        sl = {lang: np.array([it["lang"] == lang and not it["attack"] for it in items]) for lang in pm.LANGS}
        sl["attack"] = np.array([it["attack"] for it in items])
        return old, new, sl
    return mk


def test_acceptance_cosmetic_edit_rarely_blocked():
    # Justification: the reference blocks about 6.5% of cosmetic edits (nominal family-wise level 5% plus
    # percentile-bootstrap under-coverage in small slices); 12% allows for a different but sound correction.
    r = pl.operating_characteristics(pair_maker(BASE, BASE + "\nBe polite."), pl.regression_gate, 150, seed=1)
    assert r["block_rate"] <= 0.12


def test_acceptance_real_regressions_are_caught():
    # Reference block rates: guard removed 0.97, prompt bloat 0.95.
    g = pl.operating_characteristics(pair_maker(BASE, pm.make_prompt(guard=False)), pl.regression_gate, 60, seed=2)
    b = pl.operating_characteristics(pair_maker(BASE, pm.make_prompt(filler_words=160)), pl.regression_gate, 60, seed=3)
    assert g["block_rate"] >= 0.85 and b["block_rate"] >= 0.80


def test_acceptance_thin_evidence_is_never_shipped():
    # With 100 items a real 4-point regression is mostly undetectable; the gate must say so rather than ship.
    r = pl.operating_characteristics(pair_maker(BASE, pm.make_prompt(filler_words=160), n=100), pl.regression_gate, 80, seed=4)
    assert r["ship_rate"] <= 0.10


def test_acceptance_language_slice_regression_needs_more_items():
    # Removing the Yoruba example costs about 9 points on Yoruba only (17% of traffic).
    old_p = pm.make_prompt(shots={"en": 1, "pcm": 1, "yo": 1})
    new_p = pm.make_prompt(shots={"en": 1, "pcm": 1})
    big = pl.operating_characteristics(pair_maker(old_p, new_p, n=900), pl.regression_gate, 60, seed=5)
    assert big["block_rate"] >= 0.5  # reference about 0.72
