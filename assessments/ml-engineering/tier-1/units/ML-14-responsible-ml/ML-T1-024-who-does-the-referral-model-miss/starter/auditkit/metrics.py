def group_metrics(y_true, y_pred, group):
    raise NotImplementedError("R1: per-group n, positives, selection_rate, tpr, fpr, ppv")


def disparity(metrics, key, ref=None, min_n=30):
    raise NotImplementedError("R2: differences and ratios against a reference group, with a small-group guard")


def bootstrap_gap_ci(y_true, y_pred, group, g1, g2, metric="tpr", n_boot=1000, seed=0, alpha=0.05):
    raise NotImplementedError("R3: group-stratified percentile bootstrap of a metric gap")


def calibration_by_group(y_true, score, group, bins=5):
    raise NotImplementedError("R4: per-group reliability bins and expected calibration error")
