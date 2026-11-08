"""Deterministic synthetic code-switched messages in eight fictional languages in four cousin pairs (no real text, no real people).

    python datagen.py --out DIR --seed 2026      # writes sample_clean.txt and sample_shifted.txt (previews only)
"""
import argparse
import os

import numpy as np
from sklearn.feature_extraction.text import HashingVectorizer

LANGS = ["koro", "kori", "hasi", "hase", "iwe", "iwo", "pidj", "pidg"]   # fictional; each pair is a close-cousin pair
CONS = list("bdfghjklmnprstwyz") + ["gb", "kp", "sh", "ny", "ch"]
VOW = list("aeiou") + ["ia", "ua", "oo"]
N_FEATURES = 2 ** 16


def _inventories():
    g = np.random.default_rng(4242)                # the 'languages' are fixed; only the sample changes with the seed
    allsyl = [c + v for c in CONS for v in VOW]
    base = []
    for fam in range(4):
        root = g.choice(allsyl, 60, replace=False)
        base.append(np.array(root))
        cousin = list(root[:42]) + list(g.choice(allsyl, 18, replace=False))      # cousin shares 70% of syllables
        base.append(np.array(cousin))
    pref = [g.dirichlet(np.ones(60) * 0.7) for _ in range(8)]
    return base, pref


_INV = None


def _word(rng, lang):
    global _INV
    if _INV is None:
        _INV = _inventories()
    base, pref = _INV
    k = rng.integers(2, 4)
    return "".join(base[lang][rng.choice(60, p=pref[lang])] for _ in range(k))


def make_corpus(seed, n, shifted=False):
    """Return (texts, labels). Clean: 3 to 9 words, 4% typos. Shifted: 1 to 4 words, 15% typos, ~15% of words code-switched."""
    rng = np.random.default_rng(seed + (999_983 if shifted else 0))
    texts, y = [], rng.integers(0, 8, n)
    for lang in y:
        nw = rng.integers(1, 5) if shifted else rng.integers(3, 10)
        words = []
        for _ in range(nw):
            l = int(lang)
            if shifted and rng.random() < 0.15:
                l = int(rng.integers(0, 8))
            words.append(_word(rng, l))
        s = " ".join(words)
        p = 0.15 if shifted else 0.04
        chars = list(s)
        for i in range(len(chars)):
            if chars[i] != " " and rng.random() < p:
                chars[i] = str(rng.choice(list("abdeghiklmnoprstuwy")))
        s = "".join(chars)
        texts.append(s)
    return texts, y


def vectorizer(n_features=N_FEATURES):
    return HashingVectorizer(analyzer="char_wb", ngram_range=(1, 4), n_features=n_features, alternate_sign=False, norm="l2")


def avg_active(texts, n_features=N_FEATURES):
    """Mean number of non-zero hashed n-gram features per message (drives the multiply-add count)."""
    return float(np.mean(np.diff(vectorizer(n_features).transform(texts).indptr)))


def make_task(seed=2026):
    """Labelled clean training set, unlabelled transfer pool (clean + shifted), small labelled shifted validation set,
    and large test sets of both kinds."""
    tr_t, tr_y = make_corpus(seed, 1200)
    pc_t, _ = make_corpus(seed + 1, 9000)
    ps_t, _ = make_corpus(seed + 1, 6000, shifted=True)
    v_t, v_y = make_corpus(seed + 2, 150, shifted=True)
    c_t, c_y = make_corpus(seed + 3, 3000)
    s_t, s_y = make_corpus(seed + 4, 3000, shifted=True)
    return dict(train_texts=tr_t, train_y=tr_y, pool_texts=pc_t + ps_t, val_texts=v_t, val_y=v_y,
                clean_texts=c_t, clean_y=c_y, shifted_texts=s_t, shifted_y=s_y)


def train_teacher(task):
    """Full-size teacher: multinomial logistic regression on 2**16 hashed features (about 2 MB in float32).
    Returns (W, b) with W of shape (2**16, 8)."""
    from sklearn.linear_model import LogisticRegression
    m = LogisticRegression(C=10, max_iter=500).fit(vectorizer().transform(task["train_texts"]), task["train_y"])
    return m.coef_.T.copy(), m.intercept_.copy()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=2026)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    for name, sh in (("clean", False), ("shifted", True)):
        t, y = make_corpus(a.seed, 50, sh)
        with open(os.path.join(a.out, f"sample_{name}.txt"), "w") as f:
            f.writelines(f"{LANGS[int(l)]}\t{x}\n" for x, l in zip(t, y))


if __name__ == "__main__":
    main()
