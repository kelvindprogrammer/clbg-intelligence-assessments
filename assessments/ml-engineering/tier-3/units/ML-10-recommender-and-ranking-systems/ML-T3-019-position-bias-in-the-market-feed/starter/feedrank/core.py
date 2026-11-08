import numpy as np


def estimate_exam(pos, click, randomized, K):
    raise NotImplementedError("R1: examination curve relative to position 0 from the randomised slice")


def rank_within_queries(qid, score):
    raise NotImplementedError("R2: 0-based rank of each row inside its query, ties to the lower row index")


def ips_value(qid, pos, click, exam, new_rank, clip=10.0):
    raise NotImplementedError("R3: inverse-propensity estimate of mean clicks per query under new_rank")


def fit_ranker(X, pos, click, exam, clip=10.0):
    raise NotImplementedError("R4: return an object with score(X); decide how position bias enters training")


def exposure_share(qid, rank, group, exam):
    raise NotImplementedError("R5: mean over queries of the examination mass that goes to group == 1")
