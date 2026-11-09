# AI-T1-012: The Wallet Assistant Dispatcher: Typed Tools, Parsed Calls and a Bounded Loop

> *A mobile-wallet start-up lets customers ask an assistant for their balance and recent transactions. The model proposes tool calls; your code decides whether they are valid, runs them safely and keeps private fields out of sight.*

![Format: implementation](https://img.shields.io/badge/format-implementation-6f42c1) ![Tier 1](https://img.shields.io/badge/tier-1-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `AI-T1-012` |
| **Title** | The Wallet Assistant Dispatcher: Typed Tools, Parsed Calls and a Bounded Loop |
| **Subtrack** | AI Engineering |
| **Tier** | 1: Foundation and Technical Fluency |
| **Unit** | [AI-06: AI Agents and Tool Calling](../README.md) |
| **Format** | implementation |
| **Difficulty** | Technical 2 · Mathematical 1 · Research 1 · Engineering 3 · Ambiguity 1 · Resources 1 (each out of 5) |
| **Estimated time** | 8-12 hours over 1 week |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM, CPU only. No GPU, no paid API, no network, no model download. Everything graded runs against a deterministic mock and a small generated corpus; the full test run takes under a minute |
| **Recommended prerequisites** | Python, JSON and pytest. No machine-learning background is needed. |
| **Skills developed** | Schema validation; tool registry design; defensive parsing; redaction; bounded agent loops; error recovery |
| **Technologies** | Python 3.10+, pytest (standard library only in your package) |

---

## B. Problem Statement

PocketNaira (fictional) is a mobile-wallet start-up whose customers ask an assistant questions such as "What is my balance?" or "Show my last three transactions". The language model does not touch the database. It writes a small JSON request, `{"tool": "check_balance", "args": {"account": "NG-1001"}}`, and **your code** validates it, runs the matching function and feeds the result back. When the model has what it needs, it writes `FINAL: <answer>`.

In the demo the model always wrote perfect JSON. In production it sometimes:

- wraps the call in friendly prose and a code fence;
- sends broken JSON, an unknown tool, or an argument outside its range (a transaction limit of 99);
- asks for an account that does not exist, so the tool raises an exception;
- gets stuck repeating the same call;
- receives tool output containing fields the assistant must never see, such as a customer's BVN (bank verification number) or phone number.

You will build the five small parts that make this safe: `validate_args`, a `ToolRegistry`, `parse_tool_call`, `redact` and `run_agent`. The model is a deterministic scripted mock (`resources/wallet.py::make_model`) with eight modes, including `chatty`, `badjson`, `badargs`, `unknown_tool`, `toolerror` and `loop`. Four wallet tools over fictional accounts are provided.

Everything is specified exactly so that you can test it exactly. The point of Tier 1 is to see how little code stands between a model's text and a real action, and how many ways that code can be wrong.

> **Why this matters beyond this task.** An agent's safety is mostly decided by the boring code between "the model said" and "the system did". Argument validation, error containment and redaction are where that line is drawn.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. **Validate** tool arguments against a declared schema and return precise, sorted errors.
2. **Contain** unknown tools, invalid arguments and tool exceptions so that the loop never crashes.
3. **Parse** a tool call or a final answer out of messy model text, including braces inside strings.
4. **Redact** sensitive fields before they reach the model or the trace.
5. **Bound** the loop and explain what each stopping reason means.

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

Implement `toolbox` in [`starter/toolbox/`](starter/toolbox/). Stubs raise `NotImplementedError("R<n>: ...")`.

A **schema** maps parameter names to specs: `{"type": "int"|"float"|"str"|"bool"|"enum", "required": bool, "default": ..., "min": ..., "max": ..., "values": [...]}`.

| ID | Requirement |
|---|---|
| **R1** | `validate_args(schema, args) -> list[str]`, sorted. Errors: `missing: p` (required, absent, and no default); `type: p` (`bool` is not `int`; an `int` is a valid `float`; `enum` values must be strings); `range: p` (type ok but below `min` or above `max`, inclusive bounds); `enum: p` (a string not in `values`); `unexpected: p` (argument not in the schema). A parameter reports at most one of type, range and enum. |
| **R2** | `ToolRegistry` with `register(name, schema, fn, description)` (`ValueError` on a duplicate name), `describe()` and `call(name, args)`. `describe` gives one line per tool sorted by name: `name(p1, p2?): description`, parameters sorted, with `?` after each optional parameter (not required, or has a default). `call` returns `{"ok": True, "result": ...}` on success and never raises: `{"ok": False, "error": "unknown_tool", "tool": name}`, `{"ok": False, "error": "invalid_args", "details": [...]}` (including when `args` is not a dict) or `{"ok": False, "error": "tool_error", "type": "<exception class name>"}`. Missing optional parameters with a `default` are filled in before the call. |
| **R3** | `parse_tool_call(text)` returns `("final", answer)` if the stripped text starts with `FINAL:`; otherwise it finds the first complete JSON object in the text (braces inside JSON strings, including escaped quotes, do not count) and returns `("call", name, args)`. Otherwise `("invalid", reason)` with `no_json` (no `{`), `bad_json` (unbalanced or unparseable) or `bad_shape` (not an object with a string `tool` and a dict `args`). Only the first object is used. |
| **R4** | `redact(obj, keys=SENSITIVE_KEYS)`: return a deep copy in which the value of every dictionary key whose lowercase form is in `keys` is `"***"`, at any depth, including inside lists. The input is not mutated. |
| **R5** | `run_agent(model, registry, user_msg, max_steps=6, redact_keys=SENSITIVE_KEYS) -> {"final", "steps", "trace", "stopped"}`. Start with `[{"role": "user", "content": user_msg}]`. Each step calls `model.next(messages)` with a copy of the messages, appends the raw reply as an `assistant` message, and parses it. A final answer ends the run (`stopped="final"`). A valid call runs through the registry; its result is redacted and appended as a `tool` message whose content is `json.dumps(result, sort_keys=True)`. An invalid reply is answered with a tool message `{"ok": false, "error": "invalid_call", "detail": reason}` and the loop continues. After `max_steps` model calls without a final answer, return `final=None`, `stopped="max_steps"`. `trace` has one entry per step: `{"step", "kind": "call"|"invalid"|"final", ...}`; call entries carry `tool`, `args` (redacted) and `result` (redacted); invalid entries carry `tool=None`, `args=None` and `result`; final entries carry `text`. |

### D.2 Engineering requirements (mandatory)

- Deterministic: no wall-clock time, no global random state, no network.
- Standard library only inside `toolbox`.
- At least **8 tests of your own** in `tests/test_member_*.py`, covering a tool that raises, a call hidden in prose, braces inside a string, and a runaway loop.
- Do not import underscore-prefixed names from `resources/`. `REPORT.md` (from the [template](submission-template/REPORT.md)) carries the short explanations and every number you cite.

### D.3 Responsibility

BVN, phone numbers and account balances are personal and financial data under the Nigeria Data Protection Act 2023. In the report, write one short paragraph explaining why redaction happens before the result enters the model context rather than only in the final answer, what else should be kept out of logs, and why a model that cannot see the BVN cannot leak it.

### D.4 Optional enhancements

- Add a per-tool `max_calls` budget to the registry and test it.
- Add a `dry_run` mode that validates a call but does not execute it.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Mock model** | [`resources/wallet.py`](resources/wallet.py): `make_model(mode, account)` with `.next(messages)`; modes `balance`, `chatty`, `badjson`, `unknown_tool`, `badargs`, `loop`, `profile`, `toolerror` |
| **Tools** | `make_tools(seed)` returns four tool specs (`check_balance`, `list_transactions`, `convert_currency`, `get_profile`) over `make_accounts(seed)` |
| **Provenance** | **Synthetic** accounts, names, phone numbers and BVNs; fictional and generated; no real person or number |
| **Licence** | CC BY 4.0 (content), MIT (code) |
| **Size** | Nothing committed beyond a 6 KB module |
| **Model access** | None. No network, key, GPU or download |

Hidden tests use other seeds and accounts, other schemas, custom redaction keys and nastier model output.

**Setup**

```bash
cd assessments/ai-engineering/tier-1/units/AI-06-agents-and-tool-calling/AI-T1-012-the-wallet-assistant-dispatcher
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract           # passes immediately: checks the scaffold
pytest                       # requirement tests fail until you implement the package
```

Nothing in the graded path calls a hosted model. If you want to try your code against a real local open-weight model (for example through Ollama) or a hosted API afterwards, that is an optional extension; never put keys or outputs from such runs into the repository.

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `toolbox/` package | R1 to R5 |
| 2 | `tests/test_member_*.py` (at least 8 tests) | Your own checks |
| 3 | `REPORT.md`, at most 800 words, from the [template](submission-template/REPORT.md) | Short explanations and the trace table; carries the AI-use declaration |
| 4 | A 5-minute walkthrough (live) | Verifies understanding (see §K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion below holds. Criteria marked (T) are checked by the public and hidden test suites; the rest are checked by hand.

1. (T) `pytest` passes the provided tests and your own from a clean environment.
2. (T) `validate_args` returns the exact sorted error lists in the public and hidden tests, including `bool` versus `int`.
3. (T) `ToolRegistry.call` never raises, for any tool exception class, and reports the class name.
4. (T) `parse_tool_call` handles prose, code fences, nested objects, braces and escaped quotes inside strings, and returns the stated invalid reasons.
5. (T) With the `loop` mock the agent stops after exactly `max_steps` model calls; with `badjson`, `badargs` and `unknown_tool` it recovers or ends cleanly with a final answer.
6. (T) No BVN or phone number appears in the trace or in any message passed to the model, including with custom `redact_keys`.
7. The report's trace table matches what your code produces for each mock mode.

---

## H. Evaluation Rubric

The full rubric with performance-level descriptors is in **[rubric.md](rubric.md)**. Summary:

| Dimension | Points |
|---|---|
| Problem understanding and technical reasoning | 10 |
| Technical correctness | 20 |
| Implementation quality | 15 |
| Methodology and evidence | 15 |
| Testing and evaluation | 15 |
| Documentation and reproducibility | 10 |
| Critical thinking and limitations | 10 |
| Presentation and communication | 5 |
| **Total** | **100** |

The outcome is decided by the score **and** the gates: a passing defence, a reproducible run, and an integrity declaration. See the [placement framework](../../../../../../docs/placement-framework.md).

---

## I. Submission Instructions

1. **Create your own private repository** named `clbg-AI-T1-012-<your-github-username>`, copying this assessment's `starter/`, `tests/`, `resources/` and `submission-template/` folders.
2. **Expected structure:** `toolbox/` (your package), `tests/` (provided tests plus your `test_member_*.py`), `resources/` (unchanged), `requirements.txt`, `REPORT.md` (from the template, which includes the AI-use declaration).
3. **Commit as you work.** Your commit history is part of the evidence (see §K).
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing a submission issue using the **Assessment submission** template, with the repository URL and the exact commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines). General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

Optional. They are recognised in feedback but never stand in for the core requirements.

1. **Parallel calls.** Let a model emit two calls in one reply and decide how the loop should respond.
2. **Schema from signatures.** Build a schema automatically from a Python function's type hints.
3. **Real model check.** Point the loop at a local open-weight model and see which of the failure modes occur (optional; never graded).

---

## K. Assessment Integrity

**AI tools are permitted** to help you learn, for example to explain a concept or review your code. **They are not permitted to do the assessment for you.** You must be able to explain and change every line you submit.

- **Disclose** all AI assistance in the declaration section of `REPORT.md` (tool, purpose, example prompt). Undisclosed use that becomes apparent at defence is an integrity breach; disclosed, reasonable use is not penalised.
- **Cite** any code adapted from documentation or other sources.
- **Collaboration:** you may discuss general techniques with other members. You may not share code, numbers or report text.
- **How your understanding is verified.** In a short defence the assessor will (1) ask why `bool` must not count as `int` and what a model could do with `True` as a limit; (2) ask what would happen if redaction ran only on the final answer; (3) give an unseen change, such as two JSON objects in one reply, and ask what your parser does and whether that is safe.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

*This section explains the design of the assessment for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | Python, JSON, exceptions, a first sight of a tool-calling loop. |
| **New skill developed** | Treating model output as untrusted input to a small, strict interpreter. |
| **Decisions the member must make** | How to structure parser state, what a trace entry holds, and what the loop should append after an invalid reply. |
| **What must be investigated independently** | How each mock mode exercises a different branch, and which errors the model can recover from. |
| **Why it is interesting** | The agent is a dozen lines, and every line is a place where a model's mistake becomes an action. |
| **Evidence of competence** | Exact validation and parsing, contained failures, bounded loop, and redaction that holds with custom keys. |
| **Misconceptions exposed** | 'The model will produce valid JSON.' 'Redact when you show the user.' 'An exception in a tool is the tool's problem.' |
| **Preparation for later work** | Leads into AI-T2-011 (budgets, approvals and injection in tool output) and AI-T3-007 (permission policy design). |

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
