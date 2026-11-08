import numpy as np


def recall_at_k(recommended, relevant, k):
    raise NotImplementedError("R1: share of the relevant set found in the first k recommendations")


def hit_rate_at_k(recommended, relevant, k):
    raise NotImplementedError("R1: 1.0 if any relevant item is in the first k, else 0.0")


def ndcg_at_k(recommended, relevant, k):
    raise NotImplementedError("R1: binary-gain NDCG with a log2(rank + 1) discount")


def leave_last_out(user, item, t, min_views=3):
    raise NotImplementedError("R2: boolean train mask and {user: held-out item}")


def item_cosine(M):
    raise NotImplementedError("R3: item-item cosine of a binary user x item matrix, zero diagonal")


def recommend(user_row, sim, k):
    raise NotImplementedError("R4: top-k unseen items by summed similarity to seen items; ties to the lower index")


def popularity_recommend(M, user_row, k):
    raise NotImplementedError("R5: top-k unseen items by training popularity")


def evaluate(M, held_out, rec_fn, k):
    raise NotImplementedError("R6: mean hit rate and mean NDCG over held-out users")
