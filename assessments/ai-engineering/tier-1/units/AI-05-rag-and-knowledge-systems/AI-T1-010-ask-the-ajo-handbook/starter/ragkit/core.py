"""Starter stubs for AI-T1-010. Implement R1-R7; see README section D."""
STOP = frozenset("the a an of to and is in for on at by or be are as it that this with".split())


def tokenize(text):
    raise NotImplementedError("R1: lowercase, split on non-alphanumerics, drop STOP words")


def chunk_text(doc_id, text, size, overlap):
    raise NotImplementedError("R2: sliding word windows with ids '<doc_id>#<i>'")


class BM25Index:
    def __init__(self, chunks, k1=1.5, b=0.75):
        raise NotImplementedError("R3: build term frequencies, document frequencies and average length")

    def score(self, query):
        raise NotImplementedError("R3: BM25 score for every chunk sharing a query term")

    def search(self, query, k):
        raise NotImplementedError("R3: top-k (chunk_id, score), score desc then id asc")


def build_context(hits, chunks_by_id, budget_words):
    raise NotImplementedError("R4: '[id] text' blocks under a word budget")


def extract_citations(answer):
    raise NotImplementedError("R5: ordered, de-duplicated [doc#n] markers")


def check_answer(answer, used_ids):
    raise NotImplementedError("R5: classify the answer's citations against what was retrieved")


def answer_question(model, index, question, k, budget):
    raise NotImplementedError("R6: retrieve, build context, call model, verify, abstain when appropriate")


def evaluate(index, qa, k):
    raise NotImplementedError("R7: recall@k and MRR at document level")
