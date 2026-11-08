"""Deterministic synthetic short messages in English, Nigerian Pidgin and simplified Yoruba (ASCII, no tone marks)
for ML-T1-017. Fictional templates written for teaching; not a language resource. A native-speaker review is
recommended before any real use."""
import argparse
import numpy as np

LANGS = ["en", "pcm", "yo"]
ITEMS = ["airtime", "data", "transfer", "ticket", "rice", "fuel", "token", "receipt", "wallet", "network", "alert", "bus fare"]
T = {
    "en": ["please send me the {i}", "i want to buy {i} today", "how much is the {i}", "my {i} is not working", "have you paid for the {i}",
           "thank you i got the {i}", "can you help me with the {i}", "the {i} is ready", "i did not receive {i}", "what time does the {i} come"],
    "pcm": ["abeg make you send {i} give me", "i wan buy {i} but network no dey work", "wetin be the price of {i}", "oga {i} don finish for my side",
            "na so e be o {i} no dey", "how far you don pay for {i}", "make we settle {i} sharp sharp", "e no easy o {i} dey cost well well",
            "i dey wait for {i} since morning", "wahala dey o {i} no show"],
    "yo": ["jowo mo fe ra {i}", "elo ni {i} yi", "owo mi ko ti de e jowo e duro fun {i}", "bawo ni se {i} wa", "mo ti san owo fun {i}",
           "e se ma fi {i} ranse si mi", "ko si {i} ni ile", "nibo ni mo ti le ra {i}", "{i} yi ko ye mi", "e wa gba {i} yin"],
}
SHORT = {"en": ["ok thanks", "{i} please", "good morning", "yes i agree"], "pcm": ["{i} abeg", "no wahala", "i dey come", "na so"], "yo": ["e se o", "{i} jowo", "o dara", "mo wa nbe"]}


TAGS = {"en": ["please", "ok", "hello", "thanks"], "pcm": ["abeg", "oga", "na so", "wahala"], "yo": ["jowo", "e se", "bawo", "o dara"]}


def _noise(s, rng, p):
    out = []
    for ch in s:
        r = rng.random()
        if ch.isalpha() and r < p * 0.5:
            continue                                   # dropped letter
        if ch.isalpha() and r < p:
            out.append(ch * 2)                         # doubled letter
        else:
            out.append(ch)
    return "".join(out)


def make_messages(n=900, seed=0, noise=0.04, short_frac=0.12):
    """Return texts (list[str]) and labels (list[str] in LANGS)."""
    rng = np.random.default_rng(seed)
    texts, labels = [], []
    for _ in range(n):
        lang = LANGS[rng.integers(3)]
        pool = SHORT[lang] if rng.random() < short_frac else T[lang]
        s = pool[rng.integers(len(pool))].format(i=ITEMS[rng.integers(len(ITEMS))])
        if rng.random() < 0.35:
            s += " N" + str(int(rng.integers(1, 40)) * 100)
        if rng.random() < 0.3:                          # code-switch: a short tag from another language in front
            other = LANGS[(LANGS.index(lang) + rng.integers(1, 3)) % 3]
            s = TAGS[other][rng.integers(4)] + " " + s
        s = _noise(s, rng, noise)
        if rng.random() < 0.2:
            s = s.upper()
        if rng.random() < 0.3:
            s += rng.choice([" :)", "!!", "...", " \U0001F64F"])
        texts.append(s); labels.append(lang)
    return texts, labels


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=2026)
    a = ap.parse_args()
    t, l = make_messages(900, a.seed)
    with open(f"{a.out}/messages_seed{a.seed}.tsv", "w", encoding="utf-8") as f:
        f.write("label\ttext\n" + "".join(f"{y}\t{x}\n" for x, y in zip(t, l)))
