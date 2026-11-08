"""Deterministic synthetic customer complaints to a fictional power distribution company (mixed English and Pidgin)
for ML-T2-016. Entirely invented: no real feeder, customer or company. A Pidgin speaker should review the
templates before any non-teaching use."""
import argparse
import numpy as np

CLASSES = ["billing", "outage", "meter", "transformer", "tariff"]
PRIOR = [0.25, 0.38, 0.20, 0.10, 0.07]
AREAS = ["Adeoye Close", "Bode Street", "Sabon Titi", "Unity Estate", "Mokola Road", "Hilltop", "Ajegunle Lane", "Kofar Gabas", "Ireti Court", "Market Road"]
EARLY = {
    "billing": ["my bill for this month is too high abeg check am", "i never use light but una send me bill of {n} naira", "wrong bill for {a} please correct am",
                "estimated bill no correct o meter reading never reach", "dem charge me double for last month bill", "i dey pay for light wey i no use, check my bill"],
    "outage": ["no light for {a} since yesterday", "light don go for {a} for three days now", "nepa don take light we dey dark since morning",
               "power outage for {a} abeg restore am", "we never see light for {n} hours", "light go and no come back for {a}"],
    "meter": ["my prepaid meter no dey accept token", "i buy token for {n} naira but e no load", "meter dey blink red and no light on am",
              "meter don spoil abeg replace am", "token no go enter my meter since morning", "prepaid meter dey show error for {a}"],
    "transformer": ["transformer don blow for {a}", "thieves steal cable for {a} transformer", "transformer dey sound and fire dey comot",
                    "pole don fall for {a} wire dey road", "oil dey leak from transformer for {a}"],
    "tariff": ["why una increase tariff of light", "tariff don change without notice abeg explain", "light price don go up and we no sabi why",
               "how much be the new tariff per kilowatt", "una raise the rate again o why"],
}
LATE = {
    "billing": ["the app show wrong bill for {a} abeg fix am", "ussd bill check show {n} naira but i never use am", "dem send me bill on whatsapp wey no correct",
                "postpaid bill don double and nobody explain", "my invoice no match wetin meter read"],
    "outage": ["light don vanish for {a} since last night", "blackout for {a} abeg", "{a} dey dark again", "we no get supply for {n} hours now",
               "grid don trip and {a} dey dark"],
    "meter": ["smart meter no dey show credit", "vendor sell me token but meter reject am", "meter app no load my token", "i recharge for {n} naira, smart meter still dey red",
              "my new meter no dey read"],
    "transformer": ["transformer burst for {a} with big noise", "vandals carry transformer cable for {a}", "pole fall for {a} and wire dey ground", "transformer fire for {a} abeg come fast"],
    "tariff": ["why dem move {a} to band a without notice", "band a rate too high for we", "new band rate don scatter my budget", "dem say band a get 20 hours but we no see am",
               "the new band price no make sense"],
}


def _noise(s, rng, p):
    out, i = [], 0
    while i < len(s):
        ch, r = s[i], rng.random()
        if ch.isalpha() and r < p * 0.4:
            i += 1; continue                                       # dropped letter
        if ch.isalpha() and r < p * 0.7 and i + 1 < len(s):
            out.append(s[i + 1]); out.append(ch); i += 2; continue  # swapped neighbours
        if ch.isalpha() and r < p:
            out.append(ch * 2); i += 1; continue                   # doubled
        out.append(ch); i += 1
    return "".join(out)


def make_complaints(n=1500, seed=0, period="early"):
    """period 'early' uses the old vocabulary and light noise; 'late' adds new vocabulary (bands, apps, vendors) and heavier
    typos. Late messages still use some early templates (20%)."""
    rng = np.random.default_rng(seed)
    texts, labels = [], []
    for _ in range(n):
        c = CLASSES[rng.choice(5, p=PRIOR)]
        pool = EARLY[c] if period == "early" or rng.random() < 0.2 else LATE[c]
        s = pool[rng.integers(len(pool))].format(a=AREAS[rng.integers(len(AREAS))], n=int(rng.integers(2, 60)) * 100)
        if rng.random() < 0.25:
            s = ["pls ", "oga ", "good morning ", "abeg "][rng.integers(4)] + s
        s = _noise(s, rng, 0.03 if period == "early" else 0.12)
        if rng.random() < 0.15:
            s = s.upper()
        texts.append(s); labels.append(c)
    return texts, labels


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=2026)
    a = ap.parse_args()
    for per in ("early", "late"):
        t, l = make_complaints(1500, a.seed, per)
        with open(f"{a.out}/complaints_{per}_seed{a.seed}.tsv", "w", encoding="utf-8") as f:
            f.write("label\ttext\n" + "".join(f"{y}\t{x}\n" for x, y in zip(t, l)))
