"""Synthetic tenancy-rules knowledge base, evaluation items and a zoo of flawed RAG systems for AI-T3-005.

make_kb(seed=0) -> [{"id": "P01", "text": str}]             16 fictional tenancy provisions (one number each)
make_items(seed=0, n_answerable=40, n_unanswerable=20)
    -> [{"id","q","answerable": bool,"gold_doc": str,"gold": str}]   gold is "" for unanswerable items
make_system(flaws=(), seed=0, strength=0.4, noise=0.03, k=5, n_answerable=40, n_unanswerable=20) -> system(item_or_question)
    A black-box RAG system: system(q: str) -> {"answer": str|None, "cited": [ids], "retrieved": [ids, best first],
    "abstained": bool}. `flaws` is a name or list of names from FLAWS. Each listed flaw fires on a question with
    probability `strength` (position_bias and under_abstain use min(1, 2*strength) on their eligible questions);
    every flaw also fires at background probability `noise` even when not listed. parametric_leak is only observable
    when retrieval misses, so a leaking system misses with probability `strength` and then always answers from memory.
FLAWS: retrieval_miss, unfaithful, parametric_leak, citation_forgery, position_bias, over_abstain, under_abstain
The behaviour is deterministic given (seed, question id). No network, no model.
Everything is fictional; place names are used only as labels.
"""
import random
import re

FLAWS = ["retrieval_miss", "unfaithful", "parametric_leak", "citation_forgery", "position_bias", "over_abstain",
         "under_abstain"]
_AREAS = ["Surulere", "Yaba", "Ikeja", "Lekki", "Ajah", "Mushin", "Apapa", "Ikorodu"]
_PROV = [
    ("A landlord must give a weekly tenant {n} days of written notice to quit.", "How many days of written notice to quit must a landlord give a weekly tenant?"),
    ("A landlord must give a monthly tenant {n} days of written notice to quit.", "How many days of written notice to quit must a landlord give a monthly tenant?"),
    ("A landlord must give a yearly tenant {n} days of written notice to quit.", "How many days of written notice to quit must a landlord give a yearly tenant?"),
    ("A landlord may demand at most {n} months of rent in advance.", "What is the most months of rent in advance a landlord may demand?"),
    ("A refundable caution deposit may not exceed {n} percent of the annual rent.", "What percent of the annual rent is the cap on a refundable caution deposit?"),
    ("The caution deposit must be returned within {n} days after the tenant leaves.", "Within how many days after the tenant leaves must the caution deposit be returned?"),
    ("A recovery of premises order takes effect only after {n} days.", "After how many days does a recovery of premises order take effect?"),
    ("A landlord must repair structural defects within {n} days of a written request.", "Within how many days of a written request must a landlord repair structural defects?"),
    ("A receipt must be issued within {n} days of every rent payment.", "Within how many days of a rent payment must a receipt be issued?"),
    ("No late-payment penalty may be charged within {n} days of the due date.", "How many days after the due date before a late-payment penalty may be charged?"),
    ("A tenant must give the landlord {n} days of notice before subletting a room.", "How many days of notice must a tenant give the landlord before subletting a room?"),
    ("Water or power may be disconnected only after {n} days of written warning.", "After how many days of written warning may water or power be disconnected?"),
    ("An agent commission may not exceed {n} percent of the annual rent.", "What percent of the annual rent is the cap on an agent commission?"),
    ("A landlord must give {n} hours of notice before inspecting an occupied flat.", "How many hours of notice must a landlord give before inspecting an occupied flat?"),
    ("A rent increase requires {n} days of written notice to the tenant.", "How many days of written notice does a rent increase require?"),
    ("The rent tribunal must hear a tenant complaint within {n} days of filing.", "Within how many days of filing must the rent tribunal hear a tenant complaint?"),
]
_UNANS = ["What is the fine for building without a permit?", "How long does a land title registration take?",
          "Which bank offers the cheapest mortgage?", "How many bedrooms must a family flat have?",
          "What is the penalty for tampering with an electricity meter?", "Who pays the tenement rate?",
          "When does the next housing census start?", "What is the tax on rental income?",
          "How many tenants may share one flat?", "What is the fee for a certified true copy of a lease?",
          "Is a verbal lease valid for a shop?", "How do I register a residents association?",
          "How tall may a fence be?", "What is the price of a bag of cement?", "Can I keep a dog in a rented flat?",
          "How is service charge divided in an estate?", "What happens when a landlord dies?",
          "How long is a customary tenancy?", "Are short-let apartments licensed?", "What is the stamp duty on a lease?"]


def make_kb(seed=0):
    rng = random.Random(seed)
    nums = rng.sample(range(2, 91), len(_PROV))
    return [{"id": f"P{i + 1:02d}", "text": s.format(n=n)} for i, ((s, _), n) in enumerate(zip(_PROV, nums))]


def make_items(seed=0, n_answerable=40, n_unanswerable=20):
    rng = random.Random(seed + 7)
    kb = make_kb(seed)
    items = []
    for j in range(n_answerable):
        i = j % len(_PROV) if j < len(_PROV) else rng.randrange(len(_PROV))
        gold = re.search(r"\d+", kb[i]["text"]).group(0)
        items.append({"q": f"{_PROV[i][1]} I live in {rng.choice(_AREAS)}.", "answerable": True,
                      "gold_doc": kb[i]["id"], "gold": gold})
    for q in rng.sample(_UNANS, n_unanswerable):
        items.append({"q": f"{q} I live in {rng.choice(_AREAS)}.", "answerable": False, "gold_doc": "", "gold": ""})
    rng.shuffle(items)
    for j, it in enumerate(items):
        it["id"] = f"Q{j:03d}"
    return items


def make_system(flaws=(), seed=0, strength=0.4, noise=0.03, k=5, n_answerable=40, n_unanswerable=20):
    flaws = {flaws} if isinstance(flaws, str) else set(flaws)
    assert flaws <= set(FLAWS), flaws
    kb = make_kb(seed)
    nums = {d["id"]: re.search(r"\d+", d["text"]).group(0) for d in kb}
    by_q = {}
    for it in make_items(seed, n_answerable, n_unanswerable):
        by_q[it["q"]] = it

    def system(q):
        q = q["q"] if isinstance(q, dict) else q
        it = by_q.get(q)
        rng = random.Random(f"{seed}|{q}")
        fire = {}
        for f in FLAWS:
            p = strength if f in flaws else noise
            if f in ("position_bias", "under_abstain") and f in flaws:
                p = min(1.0, 2 * strength)
            fire[f] = rng.random() < p
        if "parametric_leak" in flaws:  # a leaking system misses retrieval on its own draws and then answers from memory
            fire["retrieval_miss"] = fire["retrieval_miss"] or fire["parametric_leak"]
            fire["parametric_leak"] = True
        ids = [d["id"] for d in kb]
        gold = it["gold_doc"] if it and it["answerable"] else None
        pool = [i for i in ids if i != gold]
        rng.shuffle(pool)
        rank = rng.choice([1, 1, 1, 2, 2, 3, 4])
        retrieved = pool[:k]
        if gold and not fire["retrieval_miss"]:
            retrieved = pool[:rank - 1] + [gold] + pool[rank - 1:k - 1]
        res = {"answer": None, "cited": [], "retrieved": retrieved, "abstained": True}
        if gold is None:
            if fire["under_abstain"]:
                res.update(answer=f"The answer is {nums[retrieved[0]]}.", cited=[retrieved[0]], abstained=False)
            return res
        if gold not in retrieved:
            if fire["parametric_leak"]:
                res.update(answer=f"The answer is {nums[gold]}.", cited=[], abstained=False)
            return res
        if fire["over_abstain"]:
            return res
        n, cited = nums[gold], [gold]
        if fire["unfaithful"]:
            wrong = int(n) + rng.randint(1, 5)
            while str(wrong) in nums.values():
                wrong += 1
            n = str(wrong)
        elif fire["position_bias"] and retrieved[0] != gold:
            n, cited = nums[retrieved[0]], [retrieved[0]]
        if fire["citation_forgery"]:
            cited = [rng.choice([i for i in ids if i not in retrieved])]
        res.update(answer=f"The answer is {n}.", cited=cited, abstained=False)
        return res

    return system
