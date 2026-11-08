def two_prop_z(x1, n1, x2, n2):
    raise NotImplementedError("R1: pooled two-proportion z for p1 - p2; 0.0 when a sample is empty or the variance is zero")


def noninferior(d_c, n_c, d_k, n_k, margin_rel, z):
    raise NotImplementedError("R2: (p_c - p_k) + z * se <= margin_rel * p_k, with the unpooled standard error")
