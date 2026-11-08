"""The implementations from the post-mortem. They are PROVIDED so you can demonstrate their failures. Do not edit."""
import numpy as np


def naive_softmax(z):
    e = np.exp(z)
    return e / e.sum(axis=-1, keepdims=True)


def naive_logsumexp(a):
    return np.log(np.exp(a).sum(axis=-1))


def naive_sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))


def naive_bce(z, y):
    p = naive_sigmoid(z)
    return -(y * np.log(p) + (1 - y) * np.log(1 - p))
