def fairness_report(y, pred, group):
    raise NotImplementedError("R1: per-group rates and the standard gaps")


def reweighing_weights(y, group):
    raise NotImplementedError("R2: Kamiran-Calders reweighing weights")
