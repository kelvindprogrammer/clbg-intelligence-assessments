def village_block_split(village, test_frac, seed):
    raise NotImplementedError("R1: (train_idx, test_idx), sorted; whole villages go to one side; round(test_frac * n_villages) test villages, at least 1")


def cluster_bootstrap_ci(correct, groups, n_boot=1000, seed=0, alpha=0.05):
    raise NotImplementedError("R2: (mean, lo, hi); resample whole groups with replacement, pooled mean of the 0/1 array each time")
