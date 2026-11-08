def subgroup_report(y_true, y_pred, groups):
    raise NotImplementedError("R1: {group: {'n', 'recall', 'fpr', 'precision'}} for every group present")


def bootstrap_ci(outcomes, n_boot=1000, seed=0, alpha=0.05):
    raise NotImplementedError("R2: (mean, lo, hi) percentile bootstrap of the mean of a 0/1 (or numeric) array")


def flip_rate(predict, texts, transform):
    raise NotImplementedError("R3: share of texts whose predicted label changes when transform(texts) is predicted instead")


def operating_threshold(scores, y, target_fpr):
    raise NotImplementedError("R4: smallest t with FPR(score >= t) <= target_fpr; flagged means score >= t")
