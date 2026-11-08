import numpy as np


def time_split(t, cutoff):
    raise NotImplementedError("R1: (train_idx, test_idx) with train = t < cutoff")


def interaction_matrix(users, items, n_users, n_items):
    raise NotImplementedError("R2: binary users x items matrix")


def recall_at_k(scores, train_M, test_M, k, items=None):
    raise NotImplementedError("R3: mean per-user recall@k, training items never recommended, optional column subset")


def fit_recommender(users, items, t, n_users, n_items, item_attrs, cutoff):
    raise NotImplementedError("R4: return a model with score_matrix(), chosen_ and report_ (uses only t < cutoff)")
