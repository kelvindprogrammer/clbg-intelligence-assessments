def roc_auc(y, score):
    raise NotImplementedError("R1: rank-based ROC-AUC with average ranks for ties")


def permutation_importance(predict, X, y, n_repeats=5, seed=0):
    raise NotImplementedError("R2: mean AUC drop when a column is permuted")


def shapley_sampling(f, x, background, n_perm=200, seed=0):
    raise NotImplementedError("R3: permutation-sampling Shapley values (phi, base)")
