"""Starter stubs for AI-T2-008. Implement R1-R9; see README section D.

You may import toy_embed, canon and STOP from resources/advisories.py (the toy embedder is part of the brief).
DEFAULT_CFG is YOURS to tune and justify in REPORT.md; the hidden tests run make_system(docs, llm) with it.
"""
DEFAULT_CFG = {
    "max_words": 40,       # chunk size in words (whole sentences only)
    "k": 4,                # chunks retrieved per question
    "rrf_k": 60,           # fusion constant, if you use reciprocal rank fusion
    "min_coverage": 0.5,   # evidence sufficiency threshold
    "sanitize": True,
    "newest_only": True,
    "verify": True,
}


def chunk_docs(docs, max_words, overlap_sentences=0):
    raise NotImplementedError("R1: sentence-aligned chunks that carry doc, series, place and year")


class HybridRetriever:
    def __init__(self, chunks, embed=None):
        raise NotImplementedError("R2: build a lexical index and a dense index over the chunks")

    def search(self, q, k, mode="hybrid", rrf_k=60):
        raise NotImplementedError("R2: modes 'bm25', 'dense', 'hybrid'; return [(chunk_id, score)]")


def sanitize(chunks):
    raise NotImplementedError("R3: remove instruction-like sentences; return (clean_chunks, flagged_ids)")


def resolve_conflicts(chunks):
    raise NotImplementedError("R4: keep only the newest year per (series, place)")


def sufficient(question, chunks, min_coverage):
    raise NotImplementedError("R5: decide whether the evidence can answer the question")


def build_prompt(question, chunks):
    raise NotImplementedError("R6: QUESTION line plus fenced one-line-per-chunk context")


def verify_answer(text, chunks):
    raise NotImplementedError("R7: check citations, numbers and hijack cues; return (ok, reason)")


def make_system(docs, llm, cfg=None):
    raise NotImplementedError("R8: return ask(question) -> {'status','text','cites','reason'}")


def evaluate(system, qa):
    raise NotImplementedError("R9: accuracy, wrong_rate, abstain_recall, injected, n")
