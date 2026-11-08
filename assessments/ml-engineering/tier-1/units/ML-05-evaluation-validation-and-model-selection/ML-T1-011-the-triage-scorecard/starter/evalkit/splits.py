import numpy as np  # noqa: F401


def stratified_group_kfold(y, groups, k, seed=0):
    """R5: return a list of k (train_idx, test_idx) pairs of numpy index arrays.

    Every group lies wholly in one test fold; every row is in exactly one test fold;
    positives are spread evenly across folds. Deterministic for a given seed.
    """
    raise NotImplementedError("R5: stratified_group_kfold")
