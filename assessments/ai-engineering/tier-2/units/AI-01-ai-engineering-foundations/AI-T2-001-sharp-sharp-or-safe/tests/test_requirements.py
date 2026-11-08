import numpy as np
import pytest

import decodelab as d
import lm as lmmod

LM = lmmod.build_lm(2026)
EOS = 1


def test_r1_softmax_temperature_and_stability():
    assert d.softmax(np.array([0.0, np.log(2)])) == pytest.approx([1 / 3, 2 / 3])
    p = d.softmax(np.array([1000.0, 1001.0]))
    assert np.isfinite(p).all() and p.sum() == pytest.approx(1)
    assert d.softmax(np.array([0.0, np.log(2)]), 2.0)[1] < 2 / 3
    assert list(d.softmax(np.array([1.0, 3.0, 3.0]), 0)) == [0, 1, 0]


def test_r2_top_k():
    assert d.filter_top_k(np.array([.4, .3, .2, .1]), 2) == pytest.approx([4 / 7, 3 / 7, 0, 0])
    assert d.filter_top_k(np.array([.25] * 4), 2) == pytest.approx([.5, .5, 0, 0])
    p = np.array([.1, .2, .7])
    assert d.filter_top_k(p, 0) == pytest.approx(p) and d.filter_top_k(p, 9) == pytest.approx(p)


def test_r3_top_p():
    assert d.filter_top_p(np.array([.2, .5, .3]), 0.7) == pytest.approx([0, .5 / .8, .3 / .8])
    assert d.filter_top_p(np.array([.2, .5, .3]), 0.5) == pytest.approx([0, 1, 0])
    assert d.filter_top_p(np.array([.2, .5, .3]), 1e-9) == pytest.approx([0, 1, 0])
    assert d.filter_top_p(np.array([.2, .5, .3]), 1.0) == pytest.approx([.2, .5, .3])


def test_r4_repetition_penalty_sign_aware_and_pure():
    lg = np.array([2.0, -1.0, 0.5])
    out = d.apply_repetition_penalty(lg, [0, 1, 1], 2.0)
    assert list(out) == [1.0, -2.0, 0.5] and list(lg) == [2.0, -1.0, 0.5]


def test_r5_generate_deterministic_bounded_and_clean():
    a, b = d.generate(LM, 7, {"temperature": 1.0}), d.generate(LM, 7, {"temperature": 1.0})
    assert a == b and all(i > 1 for i in a)
    assert len(d.generate(LM, 7, max_len=3)) <= 3
    assert len({tuple(d.generate(LM, s)) for s in range(30)}) > 5


def test_r5_greedy_limits():
    g = {tuple(d.generate(LM, s, {"temperature": 0})) for s in range(10)}
    assert len(g) == 1
    assert {tuple(d.generate(LM, s, {"top_k": 1})) for s in range(10)} == g


def test_r6_sequence_logprob_matches_manual_chain():
    ids = [LM.vocab.index(w) for w in "your balance is 5000 naira".split()]
    ctx, tot = [], 0.0
    for t in ids + [EOS]:
        tot += LM.logits(ctx)[t]  # build_lm stores normalised log-probabilities
        ctx.append(t)
    assert d.sequence_logprob(LM, ids) == pytest.approx(tot)
    assert d.sequence_logprob(LM, ids) < 0


def test_r7_beam_beats_or_ties_greedy_and_width1_is_greedy():
    g = d.generate(LM, 0, {"temperature": 0})
    assert d.beam_search(LM, 1) == g
    assert d.sequence_logprob(LM, d.beam_search(LM, 4)) >= d.sequence_logprob(LM, g) - 1e-9


def test_r8_evaluate_config_metrics():
    m = d.evaluate_config(LM, {"temperature": 0}, list(range(40)))
    assert set(m) == {"valid_rate", "unique_rate", "repeat_rate"}
    assert m["valid_rate"] == 1.0 and m["unique_rate"] == pytest.approx(1 / 40)
    plain = d.evaluate_config(LM, {}, list(range(100, 200)))
    assert 0.55 < plain["valid_rate"] < 0.95 and plain["unique_rate"] > 0.45


def test_acceptance_choose_decoding_generalises_to_heldout_seeds():
    # Justification: reference top_p 0.9 at T=1 gives valid 1.0 and unique ~0.5 on 100 held-out seeds;
    # plain sampling gives ~0.8 valid and low temperature gives ~0.3 unique, so both bars bind.
    cfg = d.choose_decoding(LM, list(range(50)), 0.97, 0.45)
    m = d.evaluate_config(LM, cfg, list(range(1000, 1100)))
    assert m["valid_rate"] >= 0.95 and m["unique_rate"] >= 0.40


def test_acceptance_choose_decoding_raises_when_infeasible():
    with pytest.raises(ValueError):
        d.choose_decoding(LM, list(range(30)), 1.0, 0.99)
