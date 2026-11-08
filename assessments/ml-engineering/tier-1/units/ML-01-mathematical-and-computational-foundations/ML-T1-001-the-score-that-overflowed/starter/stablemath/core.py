"""Implement every function below. Each stub names its requirement."""
import numpy as np


def logsumexp(a, axis=-1, keepdims=False):
    raise NotImplementedError("R1: stable log-sum-exp")


def softmax(z, axis=-1):
    raise NotImplementedError("R2: stable softmax")


def log_softmax(z, axis=-1):
    raise NotImplementedError("R3: stable log-softmax")


def sigmoid(z):
    raise NotImplementedError("R4: stable sigmoid")


def bce_with_logits(z, y):
    raise NotImplementedError("R5: stable elementwise binary cross-entropy from logits")


def softmax_cross_entropy(logits, labels):
    raise NotImplementedError("R6: return (mean_loss, grad_wrt_logits)")


def numeric_grad(f, x, eps=1e-6):
    raise NotImplementedError("R7: central finite differences")


class LogisticRegression:
    def __init__(self, l2=0.0, lr=0.5, steps=500):
        self.l2, self.lr, self.steps = l2, lr, steps
        self.loss_history_ = []

    def fit(self, X, y):
        raise NotImplementedError("R8: standardise internally, then gradient descent on bce_with_logits")

    def predict_proba(self, X):
        raise NotImplementedError("R8")

    def predict(self, X):
        raise NotImplementedError("R8")
