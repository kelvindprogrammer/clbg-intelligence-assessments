"""A small fully connected network in numpy: ReLU hidden layers, softmax output, cross-entropy loss.

`params` is a list of (W, b) tuples, W of shape (fan_in, fan_out). Gradients use the same structure.
"""
from dataclasses import dataclass, field

import numpy as np  # noqa: F401


def init_params(layer_sizes, seed=0, scheme="he"):
    """R1: biases zero. scheme 'he': N(0, 2/fan_in); 'xavier': N(0, 2/(fan_in+fan_out)); 'zeros': all zero.
    Use np.random.default_rng(seed) and draw layers in order so results are reproducible."""
    raise NotImplementedError("R1: init_params")


def forward(params, X):
    """R2: return (probs, cache). Numerically stable softmax (subtract the row max). The cache is whatever your
    backward needs, one entry per layer."""
    raise NotImplementedError("R2: forward")


def loss(probs, y, params, l2=0.0):
    """R3: mean cross-entropy plus 0.5 * l2 * sum of squared weights (biases excluded). y: integer labels."""
    raise NotImplementedError("R3: loss")


def backward(params, cache, y, l2=0.0):
    """R4: gradients of `loss` w.r.t. every (W, b), same structure as params."""
    raise NotImplementedError("R4: backward")


def gradient_check(params, X, y, l2=0.0, eps=1e-5):
    """R5: largest relative error |num - ana| / max(1e-8, |num| + |ana|) over every parameter, using central
    differences of `loss`. Must restore each parameter after perturbing it."""
    raise NotImplementedError("R5: gradient_check")


@dataclass
class TrainResult:
    params: list
    history: list = field(default_factory=list)  # full-data loss after each epoch


def train(X, y, layer_sizes, epochs=100, lr=0.1, batch_size=32, momentum=0.0, l2=0.0, seed=0, init="he"):
    """R6: mini-batch SGD with classical momentum: v = momentum * v - lr * g; w = w + v.
    Parameters come from init_params(layer_sizes, seed, init). rng = np.random.default_rng(seed) is created once,
    after init_params; each epoch draws rng.permutation(n) and walks it in consecutive slices of batch_size
    (the last may be smaller). history gets loss(forward(params, X)[0], y, params, l2) after every epoch."""
    raise NotImplementedError("R6: train")


def predict(params, X):
    """R7: integer class labels (argmax of probabilities)."""
    raise NotImplementedError("R7: predict")
