"""Provided plumbing (already implemented): forward pass, accuracy and the container the tests expect."""
from dataclasses import dataclass, field

import numpy as np


def forward(Ws, bs, X):
    h = np.asarray(X, float)
    for i, (W, b) in enumerate(zip(Ws, bs)):
        h = h @ W + b
        if i < len(Ws) - 1:
            h = np.maximum(h, 0.0)
    return h


def accuracy(Ws, bs, X, y):
    return float((forward(Ws, bs, X).argmax(1) == np.asarray(y)).mean())


def float32_bytes(Ws, bs):
    return 4 * (sum(W.size for W in Ws) + sum(b.size for b in bs))


@dataclass
class CompressedModel:
    """Effective (dequantised) weights, the storage cost under the course storage model, and what you chose."""
    Ws: list
    bs: list
    bytes: int
    config: dict = field(default_factory=dict)

    def predict(self, X):
        return forward(self.Ws, self.bs, X).argmax(1)
