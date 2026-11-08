def split_indices(n, seed, test_frac):
    raise NotImplementedError("R3: deterministic (train_idx, test_idx) split")


def train(config, X, y, names):
    raise NotImplementedError("R4: deterministic training run returning a Run")


def predict_proba(run, X):
    raise NotImplementedError("R4: probability of class 1 using the run's scaler and weights")
