def build_candidates(task, teacher_W, teacher_b):
    raise NotImplementedError("R4: at least 8 candidates from at least 3 families, including the teacher itself")


def choose(rows, max_bytes, max_macs, n_val):
    raise NotImplementedError("R5: one-standard-error rule among feasible rows; return the chosen name")
