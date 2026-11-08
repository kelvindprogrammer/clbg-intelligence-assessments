import numpy as np


class DecisionTree:
    def __init__(self, max_depth=None, min_samples_leaf=1):
        self.max_depth, self.min_samples_leaf = max_depth, min_samples_leaf

    def fit(self, X, y):
        raise NotImplementedError("R3/R4: recursive builder; also set depth_, n_leaves_, classes_, feature_importances_")

    def predict_proba(self, X):
        raise NotImplementedError("R3")

    def predict(self, X):
        raise NotImplementedError("R3")


def export_rules(tree, feature_names):
    raise NotImplementedError("R5: one 'IF ... THEN class=c' string per leaf, left to right")


def depth_sweep(X_train, y_train, X_val, y_val, depths):
    raise NotImplementedError("R6: list of (depth, train_acc, val_acc)")
