"""Synthetic thrift-cooperative handbook and question set for AI-T1-010.

make_handbook(seed) -> [{"id": "S01", "title": str, "text": str}]
make_questions(seed) -> [{"q": str, "gold": "S03"}]  (gold = the section holding the fact)
make_model(mode)     -> callable(question, context) -> str   (deterministic mock answerer)
All content is fictional. No network, no randomness beyond the explicit seed.
"""
import random
import re

# (title, [(fact sentence, question)]) ; {n} is replaced by a seeded integer in (lo, hi)
_TOPICS = [
    ("Monthly contributions", [
        ("Every member must pay a monthly contribution of {n} thousand naira into the pool before the fifth day.", "What is the monthly contribution due from every member into the pool?"),
        ("A contribution received after the fifth day attracts a lateness charge of {n} hundred naira.", "How much is the lateness charge for a contribution received after the fifth day?")]),
    ("Loan eligibility", [
        ("A member becomes eligible for a loan only after {n} months of unbroken contributions.", "After how many months of unbroken contributions is a member eligible for a loan?"),
        ("The maximum loan is {n} times the savings balance of the borrower.", "What multiple of the savings balance is the maximum loan?")]),
    ("Loan interest", [
        ("Loans carry simple interest of {n} percent per year on the outstanding principal.", "What yearly simple interest applies to the outstanding principal of loans?"),
        ("Repayment must be completed within {n} months unless the executive council grants a rollover.", "Within how many months must repayment be completed unless a rollover is granted?")]),
    ("Guarantors", [
        ("Each borrower must present {n} guarantors who are fully paid-up members.", "How many guarantors who are fully paid-up members must each borrower present?"),
        ("A guarantor is released from liability once {n} percent of the loan has been repaid.", "At what percent repaid is a guarantor released from liability?")]),
    ("Withdrawal and exit", [
        ("A member who resigns receives the savings balance after a waiting period of {n} weeks.", "How many weeks is the waiting period before a resigning member receives the savings balance?"),
        ("An exit fee of {n} percent of the savings balance is retained for the emergency fund.", "What exit fee percent is retained for the emergency fund?")]),
    ("General meetings", [
        ("The annual general meeting needs a quorum of {n} percent of registered members.", "What quorum percent of registered members does the annual general meeting need?"),
        ("Notice of any general meeting must be posted {n} days beforehand on the notice board.", "How many days beforehand must notice of a general meeting be posted on the notice board?")]),
    ("Welfare and bereavement", [
        ("The bereavement grant to the family of a deceased member is {n} thousand naira.", "How large is the bereavement grant to the family of a deceased member?"),
        ("A welfare claim must be lodged with the secretary within {n} days of the event.", "Within how many days must a welfare claim be lodged with the secretary?")]),
    ("Annual dividends", [
        ("Surplus is shared as dividends at the end of the year in proportion to savings held for at least {n} months.", "For at least how many months must savings be held to share in surplus dividends?"),
        ("The executive council may retain up to {n} percent of surplus as reserve before dividends are declared.", "Up to what percent of surplus may the executive council retain as reserve?")]),
    ("Records and audit", [
        ("Passbooks are balanced against the ledger every {n} weeks by the financial secretary.", "How often in weeks are passbooks balanced against the ledger by the financial secretary?"),
        ("An external audit is commissioned when the pool exceeds {n} million naira.", "At what pool size in millions of naira is an external audit commissioned?")]),
    ("Disputes", [
        ("A written complaint is answered by the disciplinary committee within {n} days.", "Within how many days does the disciplinary committee answer a written complaint?"),
        ("A suspended member may appeal to the general meeting within {n} days of the suspension.", "Within how many days of the suspension may a suspended member appeal to the general meeting?")]),
]
_FILL = ["Members are reminded that this handbook is read together with the constitution of the society.",
         "Questions about this section should be directed to the secretary during the monthly meeting.",
         "The executive council reviews these provisions every year and announces changes at the general meeting.",
         "All officers act in the interest of members and keep records open to inspection by members."]


def make_handbook(seed=7):
    rng = random.Random(seed)
    docs = []
    for i, (title, facts) in enumerate(_TOPICS, 1):
        sents = [rng.choice(_FILL)]
        for f, _ in facts:
            sents.append(f.format(n=rng.randint(2, 9)))
            sents.append(rng.choice(_FILL))
        docs.append({"id": f"S{i:02d}", "title": title, "text": " ".join(sents)})
    return docs


def make_questions(seed=7, vague=False):
    """vague=True drops the two rarest words of each question (members rarely quote the handbook)."""
    rng = random.Random(seed + 1)
    qs = [{"q": q, "gold": f"S{i:02d}"} for i, (_, facts) in enumerate(_TOPICS, 1) for _, q in facts]
    if vague:
        df = {}
        for t, facts in _TOPICS:
            for f, q in facts:
                for w in set(re.findall(r"[a-z]+", (t + " " + f).lower())):
                    df[w] = df.get(w, 0) + 1
        for item in qs:
            ws = re.findall(r"[a-z]+", item["q"].lower())
            rare = sorted(set(ws), key=lambda w: (df.get(w, 0), w))[:2]
            item["q"] = " ".join(w for w in ws if w not in rare)
    rng.shuffle(qs)
    return qs


_CITE = re.compile(r"^\[([^\]]+)\]\s*(.*)$")


def make_model(mode="faithful"):
    """Deterministic mock answerer. Context is blocks '[id] text' separated by a blank line.
    modes: faithful (first sentence of top block, cited), forger (cites an id that is not in context),
    uncited (no citation), mixed (one cited sentence, one uncited sentence)."""
    def model(question, context):
        blocks = [b for b in context.split("\n\n") if b.strip()]
        if not blocks:
            return "I don't know."
        m = _CITE.match(blocks[0].strip())
        cid, text = (m.group(1), m.group(2)) if m else ("?", blocks[0])
        first = re.split(r"(?<=[.!?])\s+", text.strip())[0].rstrip(".")
        if mode == "faithful":
            return f"{first} [{cid}]."
        if mode == "forger":
            return f"{first} [S99#0]."
        if mode == "uncited":
            return f"{first}."
        if mode == "mixed":
            return f"{first} [{cid}]. Members should also read the constitution."
        raise ValueError(mode)
    return model
