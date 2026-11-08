"""A deterministic toy text embedder with planted semantic structure (no downloads, no network).

Words belong to topics. Every word of a topic shares a topic centroid (so synonyms are close); unknown tokens
(ids, typos, rare terms) get a vector built from hashed character trigrams, so they match themselves and
near-spellings but carry no topic. A text is embedded as the SUM of its token vectors (not normalised), so
vector norm grows with text length unless you normalise it yourself.
"""
from __future__ import annotations

import re
import zlib

import numpy as np

_C, _V = "bdfghklmnprstwyz", "aeiou"


def pseudo_word(rng) -> str:
    return "".join(rng.choice(list(_C)) + rng.choice(list(_V)) for _ in range(int(rng.integers(2, 4))))


def make_topics(seed: int = 0, n_topics: int = 12, per_topic: int = 16):
    """Return a list of topics, each a list of distinct pseudo-words (no word is in two topics)."""
    rng = np.random.default_rng(seed)
    seen, topics = set(), []
    for _ in range(n_topics):
        ws = []
        while len(ws) < per_topic:
            w = pseudo_word(rng)
            if w not in seen and len(w) >= 4:
                seen.add(w)
                ws.append(w)
        topics.append(ws)
    return topics


def tokenize(text: str):
    return re.findall(r"[a-z0-9]+(?:-[a-z0-9]+)*", text.lower())


class Embedder:
    def __init__(self, topics, dim: int = 48, seed: int = 0, topic_weight: float = 0.8):
        rng = np.random.default_rng(seed + 1)
        self.dim, self.cache = dim, {}
        cent = rng.normal(size=(len(topics), dim))
        cent /= np.linalg.norm(cent, axis=1, keepdims=True)
        self.vec = {}
        for t, ws in enumerate(topics):
            for w in ws:
                n = rng.normal(size=dim)
                n /= np.linalg.norm(n)
                self.vec[w] = topic_weight * cent[t] + np.sqrt(1 - topic_weight ** 2) * n

    def _unknown(self, tok: str):
        if tok not in self.cache:
            padded = f"^{tok}$"
            grams = {padded[i:i + 3] for i in range(max(1, len(padded) - 2))}
            v = np.zeros(self.dim)
            for g in sorted(grams):
                v += np.random.default_rng(zlib.crc32(g.encode())).normal(size=self.dim)
            self.cache[tok] = 0.7 * v / np.sqrt(len(grams))
        return self.cache[tok]

    def embed(self, texts):
        out = np.zeros((len(texts), self.dim))
        for i, t in enumerate(texts):
            for tok in tokenize(t):
                out[i] += self.vec[tok] if tok in self.vec else self._unknown(tok)
        return out
