"""Deterministic synthetic SMS (scam vs legitimate) in English, Pidgin and simplified Yoruba-style text for ML-T3-015.
Entirely invented teaching data; the languages are rough template approximations, not a language resource."""
import argparse
import numpy as np

GROUPS = ["en", "pcm", "yo"]
SCAM = {
    "en": ["congratulations you have won N{n} in the promo send your full name and bvn to claim", "your account will be blocked verify your bvn and pin at {l}",
           "pay a registration fee of N{n} to confirm your job placement", "get a loan of N{n} in five minutes no collateral send otp to activate",
           "please send me the otp you just received i sent it by mistake", "your atm card is suspended confirm your pin at {l}"],
    "pcm": ["abeg oga na you win N{n} for promo send ur bvn make we pay you", "dem go block ur account if you no verify bvn for {l}", "pay N{n} for registration and the job na yours",
            "loan dey for you N{n} just send otp o", "abeg send me the otp wey enter your phone na mistake", "ur atm card don block confirm ur pin for {l}"],
    "yo": ["e ku ise o ti win N{n} ninu promo fi bvn re ranse lati gba", "a o ti account yin ayafi ti e ba verify bvn ni {l}", "san N{n} fun registration ki o gba ise yin",
           "owo loan N{n} wa fun yin fi otp ranse", "jowo fi otp ti o de ranse si mi asise ni", "atm card yin ti di ti e ba confirm pin ni {l}"],
}
HARD_SCAM = {
    "en": ["debit alert N{n} on your account balance is N{m} if not you call {l}", "your parcel is held pay N{n} delivery fee at {l}", "your salary of N{n} is pending confirm your bvn at {l}"],
    "pcm": ["debit alert N{n} don comot your account balance na N{m} if no be you call {l}", "your parcel dey hold pay N{n} delivery fee for {l}", "your salary of N{n} dey pending confirm ur bvn for {l}"],
    "yo": ["owo N{n} ti jade ninu account yin balance ni N{m} ti ko ba je yin pe {l}", "parcel yin wa ni ibi san N{n} fun delivery ni {l}", "owo osu yin N{n} wa ni pending confirm bvn ni {l}"],
}
HARD_LEGIT = {
    "en": ["dear customer never share your otp pin or bvn with anyone", "verify this transaction in the official bank app", "your bank statement is ready download it in the app"],
    "pcm": ["dear customer no ever share your otp pin or bvn with anybody", "verify this transaction for the bank app", "your bank statement ready download am for the app"],
    "yo": ["onibara wa e ma fi otp pin tabi bvn yin han enikeni", "e verify transaction yi ninu bank app", "statement yin ti ready e download re ninu app"],
}
NOVEL_SCAM = {
    "en": ["free data bundle waiting for you reply with your pin to receive it", "your nin must be updated today send your details to {l} or lose your sim",
           "i am stuck abroad please send N{n} urgently i will pay you back"],
    "pcm": ["free data dey wait for you reply with ur pin make you collect am", "una must update nin today send ur details for {l} or dem go block sim",
            "i dey stranded abeg send N{n} fast i go pay you back"],
    "yo": ["data ofe wa fun yin fi pin yin ranse lati gba", "e gbodo update nin loni fi alaye yin ranse si {l} tabi a o ti sim yin", "mo wa ni ilu oyinbo e jowo fi N{n} ranse kia"],
}
NOVEL_LEGIT = {
    "en": ["your data bundle expires tomorrow dial the code on your phone to renew", "polling unit has changed check the notice board", "thanks for shopping with us your order is confirmed"],
    "pcm": ["your data go expire tomorrow dial the code for your phone to renew", "polling unit don change check the notice board", "thank you for shopping with us your order don confirm"],
    "yo": ["data yin yoo pari ni ola e te koodu lori foonu yin lati tun se", "polling unit ti yipada e wo notice board", "o seun fun rira yin order yin ti confirm"],
}
FILL = {"en": ["details at {l}", "track it at {l}"], "pcm": ["see details for {l}", "track am for {l}"], "yo": ["alaye ni {l}", "tele e ni {l}"]}
LEGIT = {
    "en": ["debit alert N{n} on your account balance is N{m}", "your otp is {d} do not share it with anyone", "your parcel will be delivered to your address today",
           "airtime recharge of N{n} was successful", "your salary of N{n} has been credited to your account", "meeting moved to three pm see you at the office"],
    "pcm": ["debit alert N{n} don comot your account balance na N{m}", "your otp na {d} no share am with anybody", "your parcel go reach your side today",
            "your airtime recharge of N{n} don enter", "oga see you for office by three pm", "mama say make you call am"],
    "yo": ["owo N{n} ti jade ninu account yin balance ni N{m}", "otp yin ni {d} e ma fi han enikeni", "ounje ti de ile e wa gba",
           "airtime N{n} ti wole", "a o ri yin ni ile ijosin ni ose yi", "ma pe e ni aaro"],
}
REGIMES = {                        # P(cue | scam), P(cue | legit), group mix, scam prevalence
    "train": (0.95, 0.03, (0.60, 0.25, 0.15), 0.40),
    "shift": (0.05, 0.60, (0.34, 0.33, 0.33), 0.30),
}


def add_style(text, rng):
    """Dress a message in urgent style (capitals, a lead-in and exclamation marks)."""
    return ("URGENT " + text.upper() + rng.choice(["!!", "!!!", " !!"])) if rng.random() < 0.8 else text.upper() + "!!"


def strip_style(text):
    t = text.lower().replace("urgent", "")
    return " ".join(t.replace("!", " ").split())


def make_sms(n=1500, seed=0, regime="train"):
    """Return texts, y (1 = scam), groups (list of 'en'/'pcm'/'yo')."""
    p_cs, p_cl, mix, prev = REGIMES[regime]
    rng = np.random.default_rng(seed)
    texts, ys, gs = [], [], []
    for _ in range(n):
        g = GROUPS[rng.choice(3, p=mix)]
        y = int(rng.random() < prev)
        hard = rng.random() < (0.45 if y else 0.30)
        novel = False
        pool = (NOVEL_SCAM if y else NOVEL_LEGIT)[g] if novel else ((HARD_SCAM if hard else SCAM) if y else (HARD_LEGIT if hard else LEGIT))[g]
        s = pool[rng.integers(len(pool))].format(n=int(rng.integers(2, 99)) * 500, m=int(rng.integers(2, 99)) * 700, d=int(rng.integers(100000, 999999)),
                                               l=rng.choice(["bit.ly/x" + str(rng.integers(100)), "tiny.cc/b" + str(rng.integers(100))]))
        fmt = dict(n=int(rng.integers(2, 99)) * 500, m=int(rng.integers(2, 99)) * 700, d=int(rng.integers(100000, 999999)), l="bit.ly/x" + str(rng.integers(100)))
        if y and rng.random() < 0.4:                                   # scams often quote a genuine-looking alert first
            s = LEGIT[g][rng.integers(len(LEGIT[g]))].format(**fmt) + " " + s
        if not y and rng.random() < 0.25:                              # genuine messages often carry a link too
            s += " " + FILL[g][rng.integers(len(FILL[g]))].format(**fmt)
        if rng.random() < (p_cs if y else p_cl):
            s = add_style(s, rng)
        texts.append(s); ys.append(y); gs.append(g)
    return texts, np.array(ys), np.array(gs)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=2026)
    a = ap.parse_args()
    for reg in REGIMES:
        t, y, g = make_sms(1500, a.seed, reg)
        with open(f"{a.out}/sms_{reg}_seed{a.seed}.tsv", "w", encoding="utf-8") as f:
            f.write("label\tgroup\ttext\n" + "".join(f"{b}\t{c}\t{d}\n" for b, c, d in zip(y, g, t)))
