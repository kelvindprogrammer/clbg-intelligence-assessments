def deletion_curve(f, X, attributions, baseline):
    raise NotImplementedError("R4: mean prediction as top-attributed features are replaced by a baseline")


def deletion_auc(curve):
    raise NotImplementedError("R4: normalised area under a deletion curve")


def agreement(a, b, k):
    raise NotImplementedError("R5: top-k Jaccard and Spearman agreement of two attribution vectors")


def stability(method, f, X_rows, noise_sd, seed, k):
    raise NotImplementedError("R5: mean top-k Jaccard of attributions under small input noise")
