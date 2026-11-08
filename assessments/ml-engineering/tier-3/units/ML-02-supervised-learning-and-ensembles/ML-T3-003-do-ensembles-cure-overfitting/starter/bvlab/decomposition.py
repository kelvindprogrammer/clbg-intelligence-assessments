import numpy as np


def bias_variance(make_model, n_train=300, rounds=40, seed=0, noise_sd=0.5, n_irrelevant=0, n_eval=1000, n_boot=40):
    raise NotImplementedError("R1-R3: repeated resampling, unbiased variance, corrected bias2, bootstrap SEs over rounds")


def grid_study(specs, **kwargs):
    raise NotImplementedError("R4: one merged record per (label, make_model, overrides)")
