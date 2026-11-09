"""Deterministic mock summariser and synthetic bank-chat generator for AI-T1-015 (no network, no model).

    ExtractiveSummariser().summarise(texts, max_tokens) -> str
        Takes the first sentence of each text in order, joins them with spaces, then cuts the result to at most
        max_tokens tokens (tokens counted with the rule \\w+|[^\\w\\s]; the cut falls on a whitespace word boundary).
        It is lossy on purpose: anything outside the first sentence of a message, or past the cut, is gone.

    make_conversation(seed, n_turns=30) -> {"messages": [...], "facts": [...]}
        messages: {"id": int, "role": "user"|"assistant", "text": str, "pin": False}
        facts:    strings (account suffix, amount, date) stated once, in the first user message.

All people, accounts and amounts are fictional. Names starting with an underscore are mock internals.
"""
import random
import re

_TOK = re.compile(r"\w+|[^\w\s]")
FILLER_USER = ["Please hold on, I am still here.", "Ok, thank you.", "Can you check again?", "I did not receive any alert.",
               "Is it taking long? I am on a bad network.", "Yes, I can wait.", "Please be quick, I am at the market.",
               "I will send a screenshot later."]
FILLER_BOT = ["I am checking that for you now.", "Thank you for waiting. Your request is being reviewed by the team.",
              "Please do not share your PIN or token with anyone.", "I can see the transfer attempt on your statement.",
              "Another update will follow shortly.", "The reference for this request is being generated."]
MONTHS = ["March", "April", "May", "June", "July"]


class ExtractiveSummariser:
    def summarise(self, texts, max_tokens):
        firsts = []
        for t in texts:
            m = re.search(r"[.!?]", t)
            firsts.append(t[: m.end()] if m else t)
        words, out = " ".join(firsts).split(), []
        for w in words:
            if len(_TOK.findall(" ".join(out + [w]))) > max_tokens:
                break
            out.append(w)
        return " ".join(out)


def make_conversation(seed, n_turns=30):
    rng = random.Random(seed)
    acct, amount, day, month = f"{rng.randrange(1000, 9999)}", f"{rng.randrange(2, 90) * 500}", rng.randrange(1, 28), rng.choice(MONTHS)
    first = (f"Hello, my account ends with {acct}. I want to dispute a transfer of NGN {amount} on {day} {month}. "
             f"It was not me and I never gave anyone my token.")
    msgs = [{"id": 0, "role": "user", "text": first, "pin": False}]
    for i in range(1, n_turns):
        role = "assistant" if i % 2 else "user"
        pool = FILLER_BOT if role == "assistant" else FILLER_USER
        msgs.append({"id": i, "role": role, "text": rng.choice(pool) + " " + rng.choice(pool), "pin": False})
    return {"messages": msgs, "facts": [acct, amount, f"{day} {month}"]}
