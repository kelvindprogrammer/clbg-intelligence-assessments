"""A tiny deterministic language model standing in for a real one (no network, no weights download).

The model is a 4-gram table (context = last four tokens) fitted on synthetic USSD banking replies, a fraction
`noise` of which contain one corrupted ("hallucinated") token. Interface used by the assessment:

    lm = build_lm(seed=2026, noise=0.12)
    lm.vocab            list[str]; id 0 is "<bos>", id 1 is "<eos>"
    lm.logits(ids)      np.ndarray (len(vocab),) of log-probabilities for the next token after `ids`
                        (`ids` excludes <bos>; <bos> is implicit before the first token)
    lm.is_valid(ids)    True iff the decoded sentence matches one of the approved reply templates exactly
    lm.decode(ids)      list[str]

Everything is fictional.
"""
import random

import numpy as np

SLOTS = {
    "AMT": ["5000", "10000", "50000", "200000"], "CODE": ["737", "894", "966"],
    "ACTION": ["check", "block", "activate"], "ITEM": ["pin", "account", "card"], "OBJ": ["card", "account"],
    "NAME": ["ade", "chika", "musa", "ngozi"], "STATUS": ["successful", "pending", "reversed"],
}
TEMPLATES = [
    "your transfer limit is {AMT} naira per day",
    "your balance is {AMT} naira",
    "dial {CODE} to {ACTION} your {ITEM}",
    "please enter your {ITEM} to {ACTION} the {OBJ}",
    "transfer of {AMT} naira to {NAME} was {STATUS}",
]
JUNK = ["free", "unlimited", "approved", "sorry", "refund", "wahala", "tomorrow"]


def _fill(rng, tpl):
    return [rng.choice(SLOTS[w[1:-1]]) if w.startswith("{") else w for w in tpl.split()]


def _vocab():
    words = set(JUNK)
    for t in TEMPLATES:
        words.update(w for w in t.split() if not w.startswith("{"))
    for v in SLOTS.values():
        words.update(v)
    return ["<bos>", "<eos>"] + sorted(words)


class TinyLM:
    def __init__(self, vocab, table):
        self.vocab, self.table = vocab, table
        self.uniform = np.full(len(vocab), -np.log(len(vocab)))

    def logits(self, ids):
        key = tuple(([0] * 4 + list(ids))[-4:])
        return self.table.get(key, self.uniform).copy()

    def decode(self, ids):
        return [self.vocab[i] for i in ids if i > 1]

    def is_valid(self, ids):
        toks = self.decode(ids)
        for t in TEMPLATES:
            parts = t.split()
            if len(parts) == len(toks) and all((tok in SLOTS[p[1:-1]]) if p.startswith("{") else tok == p
                                               for p, tok in zip(parts, toks)):
                return True
        return False


def build_lm(seed=2026, noise=0.12, n=3000):
    rng = random.Random(seed)
    vocab = _vocab()
    idx = {w: i for i, w in enumerate(vocab)}
    counts = {}
    for _ in range(n):
        toks = _fill(rng, rng.choice(TEMPLATES))
        if rng.random() < noise:
            toks[rng.randrange(len(toks))] = rng.choice(vocab[2:])
        ids = [0] * 4 + [idx[t] for t in toks] + [1]
        for i in range(4, len(ids)):
            counts.setdefault(tuple(ids[i - 4:i]), np.full(len(vocab), 0.01))[ids[i]] += 1
    return TinyLM(vocab, {k: np.log(v / v.sum()) for k, v in counts.items()})
