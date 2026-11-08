import numpy as np


def make_features(Y, cal, origin, lead):
    raise NotImplementedError("R1: (n_agents, F) causal features for target day origin + lead - 1")


def wape(y_true, y_pred):
    raise NotImplementedError("R2: sum |error| / sum actual")


def evaluate(model, Y, cal, origins, horizon=7):
    raise NotImplementedError("R3: pooled WAPE of model.forecast over the origins")


def fit_forecaster(Y, cal, horizon=7):
    raise NotImplementedError("R4: return a model with forecast(Y, cal, origin), chosen_ and report_")
