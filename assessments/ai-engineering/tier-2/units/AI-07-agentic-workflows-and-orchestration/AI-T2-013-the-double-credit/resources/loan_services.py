"""Deterministic mock loan back-end, mock planner and virtual clock for AI-T2-013. No network, no model, no sleeping.

    svc = Services(seed=0, p_transient=0, p_timeout_after=0, p_timeout_before=0, permanent_tools=(), script=None)
    svc.call(tool, args, key, clock) -> dict          advances the clock by the tool latency; may raise
        TransientError   nothing happened                                   (safe to retry)
        TimeoutError     slow reply: with p_timeout_after the effect HAS been applied, with p_timeout_before it has not
        PermanentError   will never succeed (not_eligible, or a tool listed in permanent_tools)
    If `key` is not None the call is idempotent: a repeat with the same key never applies the effect twice.
    svc.audit() -> {loan_id: {"reserved", "credited", "ledger_open", "sms"}}   the money-relevant world state
    svc.calls   -> total number of call() invocations
    script={tool: [outcome, ...]}: outcomes ("ok", "transient", "timeout_after", "timeout_before", "permanent") consumed
        one per call of that tool (any key), before random behaviour resumes.

    planner = MockPlanner(seed=0, p_bad=0.0, stubborn=False)
    planner.plan(request, feedback=None) -> list of steps {"id", "tool", "deps", "args"}
        With probability p_bad the first plan for a loan is defective (cycle, unknown tool, unknown dependency,
        duplicate id or an irreversible SMS that does not wait for the money steps). If `feedback` (a list of
        validation errors) is given the planner repairs the plan, unless stubborn=True, which repeats the defect.

    FakeClock(start=0.0): now(), sleep(s) (records the wait in .sleeps), tick(s) (used by services, not recorded), fork() -> new FakeClock at the same time (a parallel branch).

All members, loans and amounts are fictional. Names starting with an underscore are mock internals.
"""
import zlib

TOOLS = {
    "check_member": {"kind": "read", "undo": None},
    "reserve_funds": {"kind": "do", "undo": "release_funds"},
    "credit_wallet": {"kind": "do", "undo": "debit_wallet"},
    "post_ledger": {"kind": "do", "undo": "void_ledger"},
    "send_sms": {"kind": "irreversible", "undo": None},
    "release_funds": {"kind": "undo", "undo": None},
    "debit_wallet": {"kind": "undo", "undo": None},
    "void_ledger": {"kind": "undo", "undo": None},
}
LATENCY = {"check_member": 1, "reserve_funds": 2, "credit_wallet": 3, "post_ledger": 1, "send_sms": 1,
           "release_funds": 1, "debit_wallet": 2, "void_ledger": 1}
SLOW = 5.0


class TransientError(Exception):
    pass


class PermanentError(Exception):
    pass


class FakeClock:
    def __init__(self, start=0.0):
        self._t = float(start)
        self.sleeps = []

    def now(self):
        return self._t

    def tick(self, s):
        """Service time passing (not recorded in sleeps)."""
        self._t += s

    def sleep(self, s):
        self.sleeps.append(s)
        self._t += s

    def fork(self):
        return FakeClock(self._t)


class Services:
    tools = TOOLS

    def __init__(self, seed=0, p_transient=0.0, p_timeout_after=0.0, p_timeout_before=0.0, permanent_tools=(), script=None):
        self.seed, self.p = seed, (p_transient, p_timeout_after, p_timeout_before)
        self.permanent_tools, self.script = set(permanent_tools), {k: list(v) for k, v in (script or {}).items()}
        self.calls, self._n, self._applied = 0, {}, {}
        self._w = {}

    def _loan(self, loan):
        return self._w.setdefault(loan, {"reserved": 0, "credited": 0, "ledger_open": 0, "sms": 0})

    def _effect(self, tool, a):
        if tool == "reserve_funds":
            self._loan(a["loan"])["reserved"] = a["amount"]
        elif tool == "credit_wallet":
            self._loan(a["loan"])["credited"] += a["amount"]
        elif tool == "post_ledger":
            self._loan(a["loan"])["ledger_open"] += 1
        elif tool == "send_sms":
            self._loan(a["loan"])["sms"] += 1
        elif tool == "release_funds":
            self._loan(a["loan"])["reserved"] = 0
        elif tool == "debit_wallet":
            self._loan(a["loan"])["credited"] = 0
        elif tool == "void_ledger":
            self._loan(a["loan"])["ledger_open"] = 0

    def _outcome(self, tool, key):
        if self.script.get(tool):
            return self.script[tool].pop(0)
        if tool in self.permanent_tools:
            return "permanent"
        n = self._n[(tool, key)] = self._n.get((tool, key), 0) + 1
        u = zlib.crc32(f"{self.seed}|{tool}|{key}|{n}".encode()) / 2 ** 32
        pt, pa, pb = self.p
        return "transient" if u < pt else "timeout_after" if u < pt + pa else "timeout_before" if u < pt + pa + pb else "ok"

    def call(self, tool, args, key, clock):
        self.calls += 1
        if tool not in TOOLS:
            raise PermanentError("unknown_tool")
        out = self._outcome(tool, key)
        if tool == "check_member" and str(args.get("member", "")).startswith("X"):
            clock.tick(LATENCY[tool])
            raise PermanentError("not_eligible")
        if out == "permanent":
            clock.tick(1)
            raise PermanentError("rejected")
        if out in ("transient", "timeout_before"):
            clock.tick(1 if out == "transient" else SLOW)
            raise TransientError("503") if out == "transient" else TimeoutError("slow")
        if key is None or key not in self._applied:
            self._effect(tool, args)
            if key is not None:
                self._applied[key] = True
        if out == "timeout_after":
            clock.tick(SLOW)
            raise TimeoutError("slow reply")
        clock.tick(LATENCY[tool])
        return {"ok": True}

    def audit(self):
        return {k: dict(v) for k, v in self._w.items()}


class MockPlanner:
    KINDS = ["cycle", "unknown_tool", "unknown_dep", "duplicate", "irreversible_early"]

    def __init__(self, seed=0, p_bad=0.0, stubborn=False):
        self.seed, self.p_bad, self.stubborn, self._asked = seed, p_bad, stubborn, {}

    @staticmethod
    def good(req):
        a = {"loan": req["loan"], "amount": req["amount"], "member": req["member"]}
        return [
            {"id": "s1", "tool": "check_member", "deps": [], "args": {"member": req["member"]}},
            {"id": "s2", "tool": "reserve_funds", "deps": ["s1"], "args": {"loan": a["loan"], "amount": a["amount"]}},
            {"id": "s3", "tool": "credit_wallet", "deps": ["s2"], "args": dict(a)},
            {"id": "s4", "tool": "post_ledger", "deps": ["s2"], "args": {"loan": a["loan"], "amount": a["amount"]}},
            {"id": "s5", "tool": "send_sms", "deps": ["s3", "s4"], "args": {"member": a["member"], "loan": a["loan"], "text": "Loan disbursed"}},
        ]

    def plan(self, request, feedback=None):
        loan = request["loan"]
        n = self._asked[loan] = self._asked.get(loan, 0) + 1
        plan = self.good(request)
        u = zlib.crc32(f"{self.seed}|{loan}|bad".encode()) / 2 ** 32
        if u >= self.p_bad or (n > 1 and not self.stubborn):
            return plan
        kind = self.KINDS[zlib.crc32(f"{self.seed}|{loan}|kind".encode()) % len(self.KINDS)]
        by = {s["id"]: s for s in plan}
        if kind == "cycle":
            by["s2"]["deps"] = ["s1", "s5"]
        elif kind == "unknown_tool":
            by["s4"]["tool"] = "wire_transfer_abroad"
        elif kind == "unknown_dep":
            by["s3"]["deps"] = ["s2", "s9"]
        elif kind == "duplicate":
            by["s4"]["id"] = "s3"
        else:
            by["s5"]["deps"] = ["s1"]
        return plan
