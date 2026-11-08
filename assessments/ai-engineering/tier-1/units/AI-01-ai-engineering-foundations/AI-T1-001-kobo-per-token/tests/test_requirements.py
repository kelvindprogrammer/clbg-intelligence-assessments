import math

import pytest

import corpus
import tokenlab as t

LOW = ["low low low low low lower lower newest newest newest newest newest newest widest widest widest"]


def test_r1_first_merges_and_tie_break():
    m = t.train_bpe(LOW, 3)
    assert m == [("e", "s"), ("es", "t"), ("est", "</w>")]


def test_r1_stops_when_no_pair_repeats():
    assert t.train_bpe(["ab cd"], 10) == []
    m = t.train_bpe(["ab ab cd"], 50)
    assert len(m) < 50 and m[0] == ("a", "b")


def test_r1_counts_are_weighted_by_word_frequency():
    # 'xy' appears in one frequent word; 'zq' in two rare ones. Frequency, not type count, decides.
    m = t.train_bpe(["xy " * 5 + "zq zqa"], 1)
    assert m == [("x", "y")]


def test_r1_deterministic_and_does_not_mutate():
    c = ["pay pay payment"]
    assert t.train_bpe(c, 4) == t.train_bpe(c, 4) and c == ["pay pay payment"]


def test_r2_encode_applies_merges_in_order():
    m = t.train_bpe(LOW, 3)
    assert t.encode("newest", m) == ["n", "e", "w", "est</w>"]
    assert t.encode("es", m) == ["es", "</w>"]


def test_r2_unseen_characters_pass_through():
    m = t.train_bpe(LOW, 3)
    assert t.encode("zest", m) == ["z", "e", "s", "t</w>"] or t.encode("zest", m)[0] == "z"
    assert "".join(t.encode("qüx", m)).replace("</w>", "") == "qüx"


def test_r3_round_trip_normalises_whitespace():
    c = corpus.make_corpus(seed=5)
    m = t.train_bpe(c["en"] + c["yo"], 80)
    for line in c["yo"][:20] + c["en"][:20]:
        assert t.decode(t.encode(line, m)) == line
    assert t.decode(t.encode("  a   b \n", m)) == "a b"
    assert t.decode([]) == ""


def test_r4_vocab_order_and_ids():
    m = t.train_bpe(LOW, 3)
    v = t.build_vocab(LOW, m)
    base = sorted(set("lowernstidw") | {"</w>"})
    assert list(v)[: len(base)] == base
    assert list(v)[len(base):] == ["es", "est", "est</w>"]
    assert list(v.values()) == list(range(len(v)))


def test_r5_token_cost_rounds_up_in_integer_kobo():
    m = []
    assert t.token_cost("ab", m, 1000) == 3  # a, b, </w>
    assert t.token_cost("ab", m, 1) == 1
    assert t.token_cost("", m, 500) == 0
    assert isinstance(t.token_cost("ab cd", m, 333), int)
    assert t.token_cost("ab cd", m, 333) == math.ceil(6 * 333 / 1000)


def test_r6_fertility_is_tokens_per_word():
    assert t.fertility(["ab cd", "ef"], []) == pytest.approx(9 / 3)
    m = t.train_bpe(["ab ab ab"], 5)
    assert t.fertility(["ab"], m) == 1.0


def _gap(train, merges=200):
    c = corpus.make_corpus(2026)
    m = t.train_bpe(train(c), merges)
    return t.fertility(c["yo"], m) / t.fertility(c["en"], m)


def test_acceptance_english_first_tokeniser_taxes_yoruba():
    # Justification: reference gap is about 4.6x; 3x leaves room for tie-break-neutral variants.
    assert _gap(lambda c: c["en"]) >= 3.0


def test_acceptance_balanced_training_closes_the_gap():
    # Reference gap is about 1.0; 1.6x is the bar.
    assert _gap(lambda c: c["en"][:60] + c["pcm"][:60] + c["yo"]) <= 1.6


def test_acceptance_yoruba_message_costs_more_under_english_tokeniser():
    c = corpus.make_corpus(2026)
    m = t.train_bpe(c["en"], 200)
    assert t.token_cost(c["yo"][0] + " " + c["yo"][1], m, 2500) > 3 * t.token_cost(c["en"][0] + " " + c["en"][1], m, 2500)
