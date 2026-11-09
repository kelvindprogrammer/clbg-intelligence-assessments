# AI-T1-014: Mama Nkechi's Order Desk: A Workflow Engine with Explicit State

> *A market trader takes orders on WhatsApp all day. Build the small state machine that classifies, extracts, prices, asks for clarification and hands complaints to a person, without ever looping forever.*

![Format: Implementation (secondary: Investigation)](https://img.shields.io/badge/format-implementation-6f42c1) ![Tier 1](https://img.shields.io/badge/tier-1-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `AI-T1-014` |
| **Title** | Mama Nkechi's Order Desk: A Workflow Engine with Explicit State |
| **Subtrack** | AI Engineering |
| **Tier** | 1: Foundation |
| **Unit** | [AI-07: Agentic Workflows and Orchestration](../README.md) |
| **Format** | Implementation (secondary: Investigation) |
| **Difficulty** | Technical 2 · Mathematical 1 · Research 1 · Engineering 3 · Ambiguity 1 · Resources 1 (each out of 5) |
| **Estimated time** | 8-12 hours |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM, CPU only. No GPU, no paid API, no network, no model download. The graded path uses a deterministic mock; the full test run takes under a minute |
| **Recommended prerequisites** | Python functions, dictionaries and exceptions; pytest. No framework knowledge is needed. |
| **Skills developed** | Explicit workflow state; labelled routing; step retries; loop guards; human-in-the-loop checkpoints; static graph validation; deciding when a fixed workflow beats an open-ended agent |
| **Technologies** | Python 3.10+, pytest (standard library only in your package) |

---

## B. Problem Statement

Mama Nkechi (fictional) sells rice, beans, garri and palm oil from a stall in Ariaria Market, Aba, and takes most orders as WhatsApp messages: "send me 2 bags of rice and 3 tins of palm oil". Her nephew wants to automate the repetitive part with a language model, and has already written the model calls. What is missing is the **control flow around them**. A message must be classified (order, complaint, other). An order must have its items extracted, priced against the catalogue and confirmed. An item that is not in the catalogue needs a clarifying question to the customer, but a customer who keeps answering with nonsense must not trap the system in a loop. A complaint must never be answered by the machine: it goes to a person, and when the person has acted the run must continue from where it stopped, even if the server restarted in between. And the model sometimes fails with a transient error that is worth retrying, while a programming error is not.

This is a **workflow, not an agent**: the set of steps is known in advance, so the control flow lives in code, in a graph you can read, test and validate before it runs. You will build the engine (`run_workflow`, `resume`, `validate_graph`) and the order-desk graph (`build_order_desk`) around a deterministic rule-based mock (`resources/desk_model.py`) whose failures you can script. State is an explicit dictionary that every step receives a copy of and returns updates to, so any run can be traced, paused and replayed.

> **Why this matters beyond this task.** Most production AI features are workflows with one or two model calls inside them. Engineers who can make the surrounding control flow explicit, bounded and inspectable are the ones whose systems survive their first bad day.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. ****Implement** a workflow engine that routes by label, keeps state explicit and records a trace.**
2. ****Retry** transient step failures a bounded number of times and never retry other errors.**
3. ****Guard** against cycles with visit and step budgets and report them as a status, not an exception.**
4. ****Checkpoint** at a human step with JSON-serialisable state and resume it later.**
5. ****Explain** why this job is a workflow rather than an agent, citing what the explicit state buys you.**

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

Implement `orderdesk` in [`starter/orderdesk/`](starter/orderdesk/). Interfaces are fixed; where the brief is silent the choices are yours to make and defend. Stubs raise `NotImplementedError("R<n>: ...")`.

The mock's documented interface is in [`resources/desk_model.py`](resources/desk_model.py). A **graph** is a dict: step name to `{"fn": fn, "next": {label: target}, "retries": n}` (`retries` optional, default 0). `fn(state, ctx) -> (updates, label)`. A **target** is a step name, `END`, or `"HUMAN:<step>"` (pause, then resume at `<step>`). The label `"*"` in `next` is the default edge.

| ID | Requirement |
|---|---|
| **R1** | `run_workflow(graph, start, state, ctx, max_steps=20, max_visits=3) -> {"status", "state", "trace", "error", "checkpoint"}`. Work on a deep copy of `state`; give each step its own deep copy too, so a step cannot mutate shared state. After a step, merge `updates` into the state, append `{"step", "label", "attempts"}` to `trace`, then follow `next[label]`, falling back to `next["*"]`. `END` gives status `done`. An unknown start or target step gives status `error` with `"unknown_step: <name>"`; no matching edge gives `"no_edge: <step>:<label>"`. |
| **R2** | Step retries. A step that raises an exception whose class name is `TransientError` is called again, up to `retries` extra times (`attempts` in the trace counts all calls). Any other exception, or exhausted retries, ends the run with status `error`, error `"<step>: <ExceptionClassName>"`, a trace entry with `label` `None`, and the state as it was before that step. The engine never raises. |
| **R3** | Loop guards. Entering the same step more than `max_visits` times gives status `loop`, error `"loop: <step>"`; executing more than `max_steps` steps gives status `loop`, error `"max_steps"`. |
| **R4** | Human checkpoints. A `"HUMAN:<step>"` target ends the run with status `paused` and `checkpoint = {"resume_at": "<step>", "state": <copy>}`, which must survive `json.dumps`. `resume(graph, checkpoint, ctx, updates=None, **limits)` continues from `resume_at` with the checkpoint state merged with `updates`, without mutating the checkpoint. |
| **R5** | `validate_graph(graph, start) -> list[str]`, sorted: `"unknown_start"` (and nothing else), `"unknown_target: a->b"`, `"unreachable: s"` (not reachable from `start`; a `HUMAN:x` edge reaches `x`) and `"no_end"` (no `END` edge reachable). |
| **R6** | `build_order_desk(model, catalogue) -> graph` with start step `classify`. `classify` (2 retries) routes `order`, `complaint`, anything else. `order` goes to `extract` (2 retries; label `items` or `none`), then `price` (label `ok` or `unknown_item`; total is the sum of catalogue price times quantity), then `confirm`, which sets `reply = "Total NGN <total> for <n> line(s)"` and `outcome = "quoted"`. `none` or `unknown_item` goes to `clarify`: at most 2 clarifications, each calling `ctx["ask_customer"](state)`, which returns replacement text or `None`; new text goes back to `extract`; `None` or a third request pauses for staff. A complaint pauses for staff, resuming at `resolved`, which sets `reply = "Handled by staff: <staff_note>"` and `outcome = "escalated"`. Other messages end with `outcome = "no_order"`. |

### D.2 Engineering requirements (mandatory)

- Deterministic: no wall-clock time, no global random state, no network. Everything randomised takes an explicit seed.
- At least **8 tests of your own** in `tests/test_member_*.py`: including a graph of your own with a cycle, a pause that pauses twice, and a step that raises a non-transient error.
- Do not import names beginning with an underscore from `resources/` or read the mock's internals; the mock is a stand-in for an opaque service.
- `REPORT.md` (from the [template](submission-template/REPORT.md)) carries every number you cite, reproducible with one command you document.

### D.3 Responsibility

Order messages contain names, phone numbers and delivery addresses, which are personal data under the Nigeria Data Protection Act 2023. In the report write one paragraph on what the trace and the checkpoint should and should not contain, how long a paused checkpoint should be kept, and who is accountable when a complaint sits in the staff queue unanswered. Explain also why the complaint path is deliberately human, and what you would need to see before automating any part of it.

### D.4 Optional enhancements

- Add a `max_total_attempts` budget across the whole run and show that it prevents a retry storm.
- Render the validated graph as a Mermaid diagram from the same dictionary.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Mock** | [`resources/desk_model.py`](resources/desk_model.py): `DeskModel(fail_first=0)` with `classify(text)`, `extract(text)`, `calls`; `TransientError`; `CATALOGUE` |
| **Data** | Short WhatsApp-style order messages written in the tests; prices in naira per unit are in `CATALOGUE` |
| **Provenance** | **Synthetic**; fictional names and amounts, no real person, account or business |
| **Licence** | CC BY 4.0 (content), MIT (code) |
| **Size** | Nothing committed beyond a few KB of Python |
| **Model access** | None. No network, key, GPU or download |

Hidden tests use other catalogues and quantities, a different number of scripted failures, customers who keep answering badly, other graphs, and repeated pauses.

**Setup**

```bash
cd assessments/ai-engineering/tier-1/units/AI-07-agentic-workflows-and-orchestration/AI-T1-014-mama-nkechis-order-desk
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract           # passes immediately: checks the scaffold
pytest                       # requirement tests fail until you implement the package
```

Nothing in the graded path calls a hosted model. Trying your code against a real local open-weight model or a Model Context Protocol server afterwards is an optional extension; never put keys or outputs from such runs into the repository.

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `orderdesk/` package | R1 to R6 |
| 2 | `tests/test_member_*.py` (at least 8 tests) | Your own scripted-behaviour tests |
| 3 | `REPORT.md` (at most 700 words), from the [template](submission-template/REPORT.md) | Answers to the three questions in the template; carries the AI-use declaration |
| 4 | A 5-minute technical defence (live) | Verifies understanding (see §K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion below holds. Criteria marked (T) are checked by the public and hidden test suites; the rest are checked by hand.

1. (T) `pytest` passes the provided tests and your own from a clean environment.
2. (T) `run_workflow` returns exactly the specified status, error strings and trace entries, never mutates the input state and never raises.
3. (T) A transient failure is retried exactly `retries` times; a non-transient error is not retried.
4. (T) A two-step cycle ends with status `loop` after exactly the specified number of trace entries; a customer who keeps giving unusable text causes exactly two clarification requests, then a pause.
5. (T) A checkpoint survives `json.dumps` and `resume` reproduces the continuation; the checkpoint itself is unchanged by resuming.
6. (T) `validate_graph` returns the exact sorted problem lists, and `build_order_desk(...)` validates clean.
7. The report explains, with the trace of one real run, why a workflow is the right pattern here and names one change to the requirements that would make an agent the better pattern.

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

1. **Create your own private repository** named `clbg-AI-T1-014-<your-github-username>`, copying this assessment's `starter/`, `tests/`, `resources/` and `submission-template/` folders.
2. **Expected structure:** `orderdesk/` (your package), `tests/` (provided tests plus your `test_member_*.py`), `resources/` (unchanged), `requirements.txt`, `REPORT.md` (from the template, which includes the AI-use declaration).
3. **Commit as you work.** Your commit history is part of the evidence (see §K).
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing a submission issue using the **Assessment submission** template, with the repository URL and the exact commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines). General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

Optional. They are recognised in feedback but never stand in for the core requirements.

1. **Idempotent steps.** Give each step an idempotency key and show a retried step cannot double-quote.
2. **Parallel branches.** Allow a step to fan out to two steps and join; decide what the trace looks like.
3. **Real model check.** Replace the mock classifier with a small local model; optional, never graded.

---

## K. Assessment Integrity

**AI tools are permitted** to help you learn, for example to explain a concept or review your code. **They are not permitted to do the assessment for you.** You must be able to explain and change every line you submit.

- **Disclose** all AI assistance in the declaration section of `REPORT.md` (tool, purpose, example prompt). Undisclosed use that becomes apparent at defence is an integrity breach; disclosed, reasonable use is not penalised.
- **Cite** any code adapted from documentation or other sources.
- **Collaboration:** you may discuss general techniques with other members. You may not share code, numbers or report text.
- **How your understanding is verified.** In a 5-minute defence the assessor will (1) ask why `max_visits` and `max_steps` are separate limits and what each catches; (2) ask what would go wrong if steps received the live state object instead of a copy; (3) give an unseen change, such as a new `refund` intent that must pause for staff but resume at a different step, and ask you to make it live.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

*This section explains the design of the assessment for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | Python dictionaries, exceptions and pytest. No framework and no model internals. |
| **New skill developed** | Treating control flow around a model as an explicit, bounded, inspectable object. |
| **Decisions the member must make** | Where to copy state, what a trace entry holds, how to order the checks for loops against retries, and how to model the clarification limit. |
| **What must be investigated independently** | Where a run ends in each failure case, by reading the trace; the difference between a visit limit and a step limit. |
| **Why it is interesting** | The same engine runs a market stall today and a payments approval tomorrow; the model is the least important part. |
| **Evidence of competence** | Exact statuses and traces under scripted failures, a JSON checkpoint that resumes, and a graph that validates. |
| **Misconceptions exposed** | 'Agents are always better than workflows.' 'A loop will end by itself.' 'Retry everything.' |
| **Preparation for later work** | Leads into AI-T2-013 (compensation and idempotency) and AI-T3-009 (choosing orchestration patterns). |

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
