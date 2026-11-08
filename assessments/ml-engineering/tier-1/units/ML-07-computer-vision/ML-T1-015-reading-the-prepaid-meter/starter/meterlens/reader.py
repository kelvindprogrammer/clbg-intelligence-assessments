import numpy as np


def hog_features(img, cell=4, bins=8):
    raise NotImplementedError("R4: gradient-orientation histograms per cell, concatenated, L2-normalised")


class DigitReader:
    def fit(self, images, labels):
        raise NotImplementedError("R5: store one mean feature vector per class in centroids_ and the labels in classes_")

    def predict(self, images):
        raise NotImplementedError("R5: nearest centroid in feature space")

    def predict_with_reject(self, images, min_margin):
        raise NotImplementedError("R5: -1 where (second-best distance - best distance) < min_margin")
