def tokenize(text):
    raise NotImplementedError("R1: lowercase; tokens are runs of letters/apostrophes or runs of digits; each digit run becomes '<num>'")


def char_ngrams(token, n_min=2, n_max=4):
    raise NotImplementedError("R2: n-grams of '<' + token + '>' ordered by n, then position")


def extract_features(text, n_min=2, n_max=4):
    raise NotImplementedError("R3: collections.Counter with 'w:<token>' and 'c:<ngram>' keys")
