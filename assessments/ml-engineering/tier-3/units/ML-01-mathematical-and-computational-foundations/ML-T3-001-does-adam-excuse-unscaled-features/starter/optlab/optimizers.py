import numpy as np

from .types import Trace


def loss_grad(w, X, y, l2=0.0):
    raise NotImplementedError("R1: stable logistic loss and gradient")


def hessian(w, X, y, l2=0.0):
    raise NotImplementedError("R1: Hessian of the logistic loss")


def solve_reference(X, y, l2=0.0):
    raise NotImplementedError("R2: damped Newton to ||g|| < 1e-12, return (w_star, f_star)")


def gradient_descent(X, y, f_star, l2=0.0, precond=None, target=1e-6, max_iter=100000):
    raise NotImplementedError("R3: step 1/L, optional diagonal column scaling")


def nesterov(X, y, f_star, l2=0.0, precond=None, target=1e-6, max_iter=100000):
    raise NotImplementedError("R4: momentum (k-1)/(k+2) with function-value restart")


def newton(X, y, f_star, l2=0.0, target=1e-6, max_iter=100):
    raise NotImplementedError("R5: damped Newton with backtracking")


def adam(X, y, f_star, lr=0.01, l2=0.0, target=1e-6, max_iter=20000, beta1=0.9, beta2=0.999, eps=1e-8):
    raise NotImplementedError("R6: Adam")
