"""Synthetic FAQ world: short complaints, topic FAQs of varying length, and a few long boilerplate documents.

    python resources/faqs.py --out DIR --seed 2026      # writes faqs.json
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

import toyembed


def make_faq_world(seed: int = 2026, n_topics: int = 12, faqs_per_topic: int = 5, n_queries: int = 120, n_boiler: int = 4):
    """Return dict: docs, queries, relevant (list of sorted doc-id lists), embed (callable texts -> matrix), boiler_ids.

    A query is relevant to every FAQ of its topic. Boilerplate documents (terms and conditions) are long, mix words
    of many topics, and are relevant to nothing."""
    rng = np.random.default_rng(seed)
    topics = toyembed.make_topics(seed, n_topics)
    emb = toyembed.Embedder(topics, seed=seed)
    docs, topic_of = [], []
    for t in range(n_topics):
        for _ in range(faqs_per_topic):
            n = int(rng.integers(8, 60))
            words = [str(rng.choice(topics[t])) if rng.random() < 0.75 else str(rng.choice(topics[int(rng.integers(n_topics))])) for _ in range(n)]
            docs.append(" ".join(words))
            topic_of.append(t)
    boiler_ids = []
    for _ in range(n_boiler):
        words = [str(rng.choice(topics[int(rng.integers(n_topics))])) for _ in range(1500)]
        boiler_ids.append(len(docs))
        docs.append(" ".join(words))
        topic_of.append(-1)
    queries, relevant = [], []
    topic_arr = np.array(topic_of)
    for _ in range(n_queries):
        t = int(rng.integers(n_topics))
        n = int(rng.integers(3, 7))
        queries.append(" ".join(str(rng.choice(topics[t])) for _ in range(n)))
        relevant.append([int(i) for i in np.flatnonzero(topic_arr == t)])
    return dict(docs=docs, queries=queries, relevant=relevant, embed=emb.embed, boiler_ids=boiler_ids)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=2026)
    a = ap.parse_args()
    w = make_faq_world(a.seed)
    Path(a.out).mkdir(parents=True, exist_ok=True)
    (Path(a.out) / "faqs.json").write_text(json.dumps({k: w[k] for k in ("docs", "queries", "relevant", "boiler_ids")}), encoding="utf-8")
