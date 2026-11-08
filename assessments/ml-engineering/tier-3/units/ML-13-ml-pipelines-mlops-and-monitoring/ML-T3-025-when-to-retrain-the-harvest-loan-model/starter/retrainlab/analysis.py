def evaluate_policies(factories, streams, cfg):
    raise NotImplementedError("R3: mean total cost per policy and regime")


def pareto_front(points):
    raise NotImplementedError("R4: indices of non-dominated points (minimise both coordinates)")


def recommend(table):
    raise NotImplementedError("R5: minimax-regret policy name")


def sweep(factories, streams, cfg, param, values):
    raise NotImplementedError("R6: recommendation as one cfg parameter varies")
