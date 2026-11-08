"""Synthetic regulatory circulars: long documents, each hiding one 'needle' sentence.

    python resources/circulars.py --out DIR --seed 2026      # writes circulars.json (docs + queries)

Each document is ~300 words of filler about two background topics and ONE needle sentence that carries a unique
reference code and a few words of the document's key topic. Five documents share each key topic.
Queries come in two kinds: 'id' (contains the code) and 'topic' (uses other words of the key topic, so there is
no word overlap with the needle; relevant = all documents of that topic).
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

import toyembed


def make_circular_world(seed: int = 2026, n_topics: int = 12, docs_per_topic: int = 5, n_dev: int = 80, n_test: int = 120):
    rng = np.random.default_rng(seed)
    all_topics = toyembed.make_topics(seed, n_topics + 1, 16)
    topics, glue = all_topics[:-1], all_topics[-1]
    emb = toyembed.Embedder(topics, seed=seed)
    docs, key, codes = [], [], []
    for t in range(n_topics):
        for _ in range(docs_per_topic):
            others = [x for x in range(n_topics) if x != t]
            bg = [topics[int(i)] for i in rng.choice(others, 2, replace=False)]
            n_sent = int(rng.integers(20, 26))
            sents = [" ".join(str(rng.choice(bg[int(rng.integers(2))] if rng.random() < 0.15 else glue)) for _ in range(12)) for _ in range(n_sent)]
            code = f"cir-{int(rng.integers(1000, 9999))}"
            while code in codes:
                code = f"cir-{int(rng.integers(1000, 9999))}"
            needle_words = [str(w) for w in rng.choice(topics[t][:8], 6, replace=False)]
            needle = " ".join([str(rng.choice(glue)), code] + needle_words + [str(rng.choice(glue)) for _ in range(4)])
            sents.insert(int(rng.integers(0, n_sent)), needle)
            docs.append(" ".join(sents))
            key.append(t)
            codes.append(code)
    key = np.array(key)

    def queries(n):
        qs, rel, kinds = [], [], []
        for _ in range(n):
            d = int(rng.integers(len(docs)))
            if rng.random() < 0.5:
                qs.append(f"{codes[d]} {rng.choice(topics[key[d]][:8])}")
                rel.append([d])
                kinds.append("id")
            else:
                t = int(key[d])
                qs.append(" ".join(str(w) for w in rng.choice(topics[t][8:], 4, replace=False)))
                rel.append([int(i) for i in np.flatnonzero(key == t)])
                kinds.append("topic")
        return qs, rel, kinds
    dev, test = queries(n_dev), queries(n_test)
    return dict(docs=docs, dev=dev, test=test, embed=emb.embed)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=2026)
    a = ap.parse_args()
    w = make_circular_world(a.seed)
    Path(a.out).mkdir(parents=True, exist_ok=True)
    (Path(a.out) / "circulars.json").write_text(json.dumps({k: w[k] for k in ("docs", "dev", "test")}), encoding="utf-8")
