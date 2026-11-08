"""Provided, working binary MLP (numpy, ReLU hidden layers, sigmoid output, Adam). Use it; you may extend it.

Typical use:
    net = MLP([n_features, 32, 16, 1], seed=0, l2=1e-4)
    for epoch in range(100):
        net.fit_epoch(X, y, lr=1e-3, batch_size=64, sample_weight=None)
        val_p = net.predict_proba(Xval)
"""
import numpy as np


class MLP:
    def __init__(self, layer_sizes, seed=0, l2=0.0):
        assert layer_sizes[-1] == 1
        self.rng = np.random.default_rng(seed)
        self.l2 = l2
        self.W = [self.rng.normal(0, np.sqrt(2 / a), (a, b)) for a, b in zip(layer_sizes[:-1], layer_sizes[1:])]
        self.b = [np.zeros(b) for b in layer_sizes[1:]]
        self._m = [np.zeros_like(p) for p in self.W + self.b]
        self._v = [np.zeros_like(p) for p in self.W + self.b]
        self._t = 0

    def _forward(self, X):
        acts = [X]
        for i, (W, b) in enumerate(zip(self.W, self.b)):
            z = acts[-1] @ W + b
            acts.append(1 / (1 + np.exp(-np.clip(z, -30, 30))) if i == len(self.W) - 1 else np.maximum(z, 0))
        return acts

    def predict_proba(self, X):
        return self._forward(np.asarray(X, float))[-1][:, 0]

    def fit_epoch(self, X, y, lr=1e-3, batch_size=64, sample_weight=None):
        X, y = np.asarray(X, float), np.asarray(y, float)
        w = np.ones(len(y)) if sample_weight is None else np.asarray(sample_weight, float)
        order = self.rng.permutation(len(y))
        for s in range(0, len(y), batch_size):
            idx = order[s:s + batch_size]
            acts = self._forward(X[idx])
            d = ((acts[-1][:, 0] - y[idx]) * w[idx] / w[idx].sum())[:, None]
            gW, gb = [None] * len(self.W), [None] * len(self.W)
            for i in reversed(range(len(self.W))):
                gW[i] = acts[i].T @ d + self.l2 * self.W[i]
                gb[i] = d.sum(0)
                if i:
                    d = (d @ self.W[i].T) * (acts[i] > 0)
            self._adam(gW + gb, lr)

    def _adam(self, grads, lr, b1=0.9, b2=0.999, eps=1e-8):
        self._t += 1
        params = self.W + self.b
        for k, (p, g) in enumerate(zip(params, grads)):
            self._m[k] = b1 * self._m[k] + (1 - b1) * g
            self._v[k] = b2 * self._v[k] + (1 - b2) * g * g
            p -= lr * (self._m[k] / (1 - b1 ** self._t)) / (np.sqrt(self._v[k] / (1 - b2 ** self._t)) + eps)

    def get_params(self):
        return [p.copy() for p in self.W + self.b]

    def set_params(self, params):
        n = len(self.W)
        for i in range(n):
            self.W[i][...] = params[i]
            self.b[i][...] = params[n + i]
