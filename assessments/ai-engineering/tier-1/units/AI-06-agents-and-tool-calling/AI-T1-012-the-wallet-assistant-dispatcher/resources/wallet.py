"""Fictional mobile-wallet accounts, tools and scripted mock agent models for AI-T1-012.

make_accounts(seed=1) -> {"NG-1001": {"name","phone","bvn","balance","tx":[...]}, ...}   (all fictional, example.ng)
make_tools(seed=1) -> [{"name","schema","fn","description"}]   four tools over those accounts
SENSITIVE = ("bvn", "phone", "pin")                              keys that must not reach the model or the trace
make_model(mode, account="NG-1001") -> model with .next(messages) -> str     (deterministic, rule-based)
    modes: balance, chatty, badjson, unknown_tool, badargs, loop, profile, toolerror
Agent text protocol: a tool call is a JSON object {"tool": name, "args": {...}} (possibly inside a code fence or
after prose); a final answer is a line starting "FINAL:". Tool results are appended as {"role": "tool", "content": json}.
No network. No randomness beyond the explicit seed.
"""
import json
import random

SENSITIVE = ("bvn", "phone", "pin")
_RATES = {"GHS": 0.0105, "KES": 0.0850, "NGN": 1.0}
_NAMES = ["Ada Obi", "Tunde Bello", "Ngozi Eze"]


def make_accounts(seed=1):
    rng = random.Random(seed)
    out = {}
    for i, name in enumerate(_NAMES):
        acct = f"NG-{1001 + i}"
        tx = [{"id": f"T{j}", "amount": rng.choice([-1, 1]) * rng.randint(5, 90) * 100, "memo": rng.choice(["airtime", "market", "transport", "school fees", "salary"])} for j in range(8)]
        out[acct] = {"name": name, "phone": f"+23480{rng.randint(10000000, 99999999)}", "bvn": f"22{rng.randint(10**8, 10**9 - 1)}",
                     "balance": rng.randint(20, 400) * 100, "tx": tx}
    return out


def make_tools(seed=1):
    acc = make_accounts(seed)

    def need(a):
        if a not in acc:
            raise KeyError(a)
        return acc[a]

    return [
        {"name": "check_balance", "description": "Return the current balance in naira.",
         "schema": {"account": {"type": "str", "required": True}},
         "fn": lambda account: {"account": account, "balance": need(account)["balance"]}},
        {"name": "list_transactions", "description": "Return the most recent transactions.",
         "schema": {"account": {"type": "str", "required": True},
                    "limit": {"type": "int", "required": False, "default": 3, "min": 1, "max": 8}},
         "fn": lambda account, limit: {"account": account, "transactions": need(account)["tx"][:limit]}},
        {"name": "convert_currency", "description": "Convert a naira amount into another currency.",
         "schema": {"amount": {"type": "float", "required": True, "min": 0.01},
                    "to": {"type": "enum", "required": True, "values": ["GHS", "KES", "NGN"]}},
         "fn": lambda amount, to: {"amount": amount, "to": to, "converted": round(amount * _RATES[to], 2)}},
        {"name": "get_profile", "description": "Return the account holder's profile.",
         "schema": {"account": {"type": "str", "required": True}},
         "fn": lambda account: {"account": account, "name": need(account)["name"], "phone": need(account)["phone"],
                                "bvn": need(account)["bvn"]}},
    ]


def _last_tool(messages):
    for m in reversed(messages):
        if m["role"] == "tool":
            try:
                return json.loads(m["content"])
            except ValueError:
                return None
    return None


def _call(tool, **args):
    return json.dumps({"tool": tool, "args": args})


class _Model:
    def __init__(self, mode, account):
        assert mode in ("balance", "chatty", "badjson", "unknown_tool", "badargs", "loop", "profile", "toolerror")
        self.mode, self.account, self.n = mode, account, 0

    def next(self, messages):
        self.n += 1
        last, m, a = _last_tool(messages), self.mode, self.account
        if m == "balance":
            return _call("check_balance", account=a) if last is None else f"FINAL: Your balance is {last['result']['balance']} naira."
        if m == "chatty":
            if last is None:
                return "Sure, let me check that for you.\n```json\n" + _call("check_balance", account=a) + "\n```\nOne moment."
            return f"FINAL: Balance {last['result']['balance']}."
        if m == "badjson":
            if last is None:
                return '{"tool": "check_balance", "args": {"account": "' + a + '"'
            if last.get("error") == "invalid_call":
                return _call("check_balance", account=a)
            return f"FINAL: Balance {last['result']['balance']}."
        if m == "unknown_tool":
            if last is None:
                return _call("send_money", account=a, amount=500)
            return "FINAL: I cannot move money; I can only read balances."
        if m == "badargs":
            if last is None:
                return _call("list_transactions", account=a, limit=99)
            if last.get("error") == "invalid_args":
                return _call("list_transactions", account=a, limit=2)
            return f"FINAL: {len(last['result']['transactions'])} transactions."
        if m == "loop":
            return _call("check_balance", account=a)
        if m == "profile":
            if last is None:
                return _call("get_profile", account=a)
            return f"FINAL: Account holder is {last['result']['name']}."
        if m == "toolerror":
            return _call("check_balance", account="NG-9999") if last is None else "FINAL: I could not find that account."


def make_model(mode, account="NG-1001"):
    return _Model(mode, account)
