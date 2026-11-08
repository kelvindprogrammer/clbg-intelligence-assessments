class NaiveBayes:
    def __init__(self, alpha=1.0):
        self.alpha = alpha

    def fit(self, docs, labels):
        raise NotImplementedError("R4: docs are dicts feature->count; set classes_ (sorted), vocab_, log_prior_, log_lik_")

    def predict_log_proba(self, docs):
        raise NotImplementedError("R4: (n, n_classes) log-probabilities whose rows log-sum-exp to 0; unseen features are ignored")

    def predict(self, docs):
        raise NotImplementedError("R4: most probable class label for each doc")


class LanguageID:
    def __init__(self, alpha=1.0, n_min=2, n_max=4):
        self.alpha, self.n_min, self.n_max = alpha, n_min, n_max

    def fit(self, texts, labels):
        raise NotImplementedError("R5: featurise with extract_features and fit NaiveBayes")

    def predict_proba(self, texts):
        raise NotImplementedError("R5: (n, n_classes) probabilities, rows sum to 1")

    def predict(self, texts):
        raise NotImplementedError("R5")

    def predict_with_abstain(self, texts, min_prob):
        raise NotImplementedError("R5: label, or 'unk' when the top probability is below min_prob")
