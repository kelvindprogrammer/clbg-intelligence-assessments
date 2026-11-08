"""Synthetic SMS-assistant corpus in English, Nigerian Pidgin and Yoruba. Deterministic, fictional, no real messages.

make_corpus(seed, n_en, n_pcm, n_yo) -> {"en": [...], "pcm": [...], "yo": [...]}
CLI: python corpus.py --out DIR --seed 2026
"""
import argparse
import json
import random
from pathlib import Path

EN = ("please send airtime to my line check my data balance buy a weekly bundle transfer money to the account "
      "how much is the monthly plan recharge now subscribe for night browsing confirm payment of naira today").split()
PCM = ("abeg make una help me buy data wetin be my balance e don finish I wan send money sharp sharp "
       "network dey bad today no wahala comot di money from my account").split()
YO = ("ẹ jọ̀wọ́ fi owó ránṣẹ́ sí mi ìwọ́ntúnwọ̀nsì ra dátà nílò bawo ni ṣe lè san ẹ̀rọ ayélujára kíákíá "
      "àkọọ́lẹ̀ mi òní").split()


def make_corpus(seed=2026, n_en=400, n_pcm=100, n_yo=40):
    rng = random.Random(seed)
    out = {}
    for lang, vocab, n in (("en", EN, n_en), ("pcm", PCM, n_pcm), ("yo", YO, n_yo)):
        out[lang] = [" ".join(rng.choice(vocab) for _ in range(rng.randint(4, 8))) for _ in range(n)]
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=2026)
    a = ap.parse_args()
    Path(a.out).mkdir(parents=True, exist_ok=True)
    (Path(a.out) / "corpus.json").write_text(json.dumps(make_corpus(a.seed), ensure_ascii=False), encoding="utf-8")
