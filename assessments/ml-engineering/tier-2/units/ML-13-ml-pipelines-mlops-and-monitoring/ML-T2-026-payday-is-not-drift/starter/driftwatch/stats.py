def psi(ref, cur, bins=10):
    raise NotImplementedError("R1: population stability index with reference-quantile bins")


def ks_stat(a, b):
    raise NotImplementedError("R2: exact two-sample Kolmogorov-Smirnov statistic, ties handled")


def calibrate_threshold(null_stats, target_far):
    raise NotImplementedError("R3: empirical threshold keeping the false-alarm rate at or below target_far")


def bonferroni_alpha(total_alpha, n_tests):
    raise NotImplementedError("R3: per-test level for a family of n_tests")
