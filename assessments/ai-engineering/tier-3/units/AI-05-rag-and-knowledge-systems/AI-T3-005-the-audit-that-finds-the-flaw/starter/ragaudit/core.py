"""Starter stubs for AI-T3-005. Implement R1-R6; see README section D.

A result is {"answer": str|None, "cited": [ids], "retrieved": [ids, best first], "abstained": bool}.
An item is {"id", "q", "answerable", "gold_doc", "gold"}. kb is [{"id", "text"}].
"""


def retrieval_metrics(results, items, k=5):
    raise NotImplementedError("R1: recall@k and MRR over answerable items")


def answer_metrics(results, items, kb):
    raise NotImplementedError("R2: accuracy, faithful_rate, citation_valid_rate, uncited_rate")


def abstention_metrics(results, items):
    raise NotImplementedError("R3: over_abstain_rate, under_abstain_rate, answered_on_miss_rate")


def bootstrap_ci(values, n_boot=1000, seed=0, alpha=0.05):
    raise NotImplementedError("R4: deterministic percentile bootstrap of the mean")


def paired_compare(a, b, n_boot=1000, seed=0):
    raise NotImplementedError("R5: paired bootstrap on per-item differences")


def audit(system, kb, items, seed=0):
    raise NotImplementedError("R6: run the system, compute metrics with intervals, return diagnosed flags")
