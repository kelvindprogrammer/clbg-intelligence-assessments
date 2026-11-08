def group_thresholds(score, y, group, criterion, tol, gain=1.0, loss=4.0, grid=51):
    raise NotImplementedError("R3: profit-maximising per-group thresholds under a fairness constraint")


def tradeoff_curve(score, y, group, criterion, tols, gain=1.0, loss=4.0, grid=51):
    raise NotImplementedError("R4: profit and achieved gap for a list of tolerances")
