# AI-T2-013: The Double Credit: A Compensating Orchestrator for AI-Planned Loan Disbursement

> *A language model plans the steps to disburse a cooperative loan; the services behind them time out after taking the money. Build the orchestrator that validates the plan, runs it in parallel, never pays twice and always cleans up.*

![Format: System-design (secondary: Debugging-forensics)](https://img.shields.io/badge/format-system--design-6f42c1) ![Tier 2](https://img.shields.io/badge/tier-2-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `AI-T2-013` |
| **Title** | The Double Credit: A Compensating Orchestrator for AI-Planned Loan Disbursement |
| **Subtrack** | AI Engineering |
| **Tier** | 2: Applied Competence |
| **Unit** | [AI-07: Agentic Workflows and Orchestration](../README.md) |
| **Format** | System-design (secondary: Debugging-forensics) |
| **Difficulty** | Technical 3 · Mathematical 1 · Research 2 · Engineering 4 · Ambiguity 3 · Resources 1 (each out of 5) |
| **Estimated time** | 14-20 hours |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM, CPU only. No GPU, no paid API, no network, no model download. The graded path uses a deterministic mock; the full test run takes under a minute |
| **Recommended prerequisites** | Python exceptions, graphs and topological ordering, pytest with scripted fakes. Recommended: AI-T1-014. |
| **Skills developed** | Plan validation; dependency layering; idempotency keys; saga-style compensation; ambiguous-failure reasoning; human approval gates; consistency auditing of a simulated back-end |
| **Technologies** | Python 3.10+, pytest (standard library only in your package) |

---

## B. Problem Statement

A cooperative society in Ibadan (fictional) lets members request small loans by chat. A language model turns each request into a **plan**: a list of steps with dependencies. Check the member, reserve funds, credit the wallet and post the ledger entry (these two in parallel), then send an SMS. The services behind the steps are ordinary back-end calls with ordinary failures, and one nasty one: sometimes the wallet service **takes the money and then times out**. A naive retry credits the member twice. A naive "the step failed, so nothing happened" rollback leaves the money in the wallet. Meanwhile the model occasionally returns a defective plan: a cycle, an unknown tool, a dependency that does not exist, a duplicate step id, or an SMS that does not wait for the money steps and could tell a member the loan is paid when it later rolls back.

You will build the orchestrator that makes this safe. It must validate the plan before any call, layer it into waves that can run in parallel and measure the saved time on a virtual clock, call each step with an idempotency key and bounded retries, ask a human before money moves on large loans, and on failure compensate every step that might have taken effect, in reverse order, including the step that failed. Finally it must prove it: a consistency audit of the mock back-end (`resources/loan_services.py`) after a whole batch, with no double credits and no leaked reservations, even at 40% timeout-after-effect rates.

The brief fixes the interfaces and the exact error strings. It does **not** fix your retry policy, your compensation retry budget or how you trade makespan against safety. Those you must choose from measurements and defend.

> **Why this matters beyond this task.** Every agentic system that moves money, books a slot or sends a message has side effects that cannot be un-sent. The reliability patterns here (idempotency, compensation, approval gates) decide whether an AI-planned action is safe to run unattended.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. ****Validate** a model-generated plan statically and feed errors back for repair.**
2. ****Schedule** steps in dependency waves and compute the parallel makespan on a virtual clock.**
3. ****Make** retries safe with idempotency keys under ambiguous timeouts.**
4. ****Compensate** completed and possibly-completed steps in reverse order and report stuck cases honestly.**
5. ****Prove** consistency with an audit over a batch of seeded failures, and show what breaks without each safeguard.**

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

Implement `sagarun` in [`starter/sagarun/`](starter/sagarun/). Interfaces are fixed; where the brief is silent the choices are yours to make and defend. Stubs raise `NotImplementedError("R<n>: ...")`.

The back-end, planner and clock are documented in [`resources/loan_services.py`](resources/loan_services.py). A plan is a list of `{"id", "tool", "deps", "args"}`. `TOOLS[t]["kind"]` is `read`, `do` (compensable, with an `undo` tool), `irreversible` (the SMS) or `undo`. `clock` has `now()`, `sleep(s)` and `fork()`. The `cfg` defaults are in `DEFAULT_CFG`.

| ID | Requirement |
|---|---|
| **R1** | `validate_plan(plan, tools) -> list[str]`, sorted. `duplicate_id: <id>` (once per id), `unknown_tool: <step>`, `unknown_dep: <step>-><dep>`. If any of those exist return them and stop. Otherwise `["cycle"]` if the graph has a cycle, else `irreversible_early: <step>` for every `irreversible` step that does not transitively depend on **every** `do` step. |
| **R2** | `waves(plan) -> list[list[str]]`: dependency layers (a step is in the first wave in which all its dependencies are done), ids sorted inside a wave. Steps in a cycle never appear. |
| **R3** | `call_step(services, step, run_id, policy, clock, idempotent=True) -> {"ok", "result", "attempts", "error"}`. The idempotency key is `"<run_id>:<step id>"` (or `None` if `idempotent` is false). Retry `TransientError` and `TimeoutError` (matched by class name) after `min(max_delay, base_delay * factor**(a-1))` seconds on `clock`; never sleep after the last attempt. `PermanentError` is not retried (error `"permanent"`), exhaustion gives `"exhausted"`, anything else `"unknown"`. |
| **R4** | `run_saga(services, plan, request, cfg, clock, approver=None) -> report` with `status` (`committed`, `rolled_back`, `rejected`, `stuck`, `invalid`), `done`, `failed`, `compensated`, `compensation_failed`, `makespan`, `errors`. Validate first (`invalid`: no calls). Run wave by wave; every step of a wave runs on its own `clock.fork()` and the main clock advances by the slowest branch. Before the first wave that contains a `do` or `irreversible` step, if `request["amount"] >= cfg["approval_threshold"]`, call `approver(request, plan)`; no approver or a falsy answer gives `rejected` with no effectful call made. After a wave in which any step failed, stop: undo, in reverse order of execution, every `do` step that was attempted (**including the failed one**, whose effect may have been applied) via its `undo` tool with the same arguments, an idempotency key `"<run_id>:undo-<id>"` and `cfg["comp_attempts"]` attempts. `rolled_back` if all undos succeeded, otherwise `stuck`. |
| **R5** | `plan_with_repair(planner, request, tools, max_asks=3) -> {"plan", "asks", "errors_history"}`: ask the planner, validate, and on defects ask again passing the sorted error list as `feedback`; `plan` is `None` after `max_asks` defective plans. |
| **R6** | `violations(audit, requests, statuses) -> list[str]` and `run_batch(services, planner, requests, cfg, clock_factory, approver=None) -> dict`. A `committed` loan must show `reserved == credited == amount`, `ledger_open == 1`, `sms == 1`; every `rolled_back`, `rejected` or `invalid` loan must show all zeros; `stuck` loans are skipped. Violations are `"<loan>: <field>"`, sorted. `run_batch` plans (with repair), runs each request on a fresh clock and returns `n`, the five status counts, `statuses`, `p95_makespan` (nearest rank: element `ceil(0.95 n) - 1` of the sorted makespans), `calls` (`services.calls`) and `violations`. |

### D.2 Engineering requirements (mandatory)

- Deterministic: no wall-clock time, no global random state, no network. Everything randomised takes an explicit seed.
- At least **12 tests of your own** in `tests/test_member_*.py`: include a scripted test for each of transient failure, timeout before the effect, timeout after the effect, permanent failure, failed compensation, defective plan and rejected approval, plus one that shows what breaks if idempotency keys are removed.
- Do not import names beginning with an underscore from `resources/` or read the mock's internals; the mock is a stand-in for an opaque service.
- `REPORT.md` (from the [template](submission-template/REPORT.md)) carries every number you cite, reproducible with one command you document.

### D.3 Responsibility

A disbursement moves a member's money, so treat the plan, the audit trail and the approval record as financial and personal data under the Nigeria Data Protection Act 2023. In the report write one paragraph on what the orchestrator should log for each step (and not log), who may see the approval queue, how long records are kept, and who is accountable when an approved loan is later found to be wrong. Explain also why a model-written plan is validated by code rather than trusted, and why the approval threshold is a business decision that must not be left to the model.

### D.4 Optional enhancements

- Add a circuit breaker that stops the batch after consecutive failures and resumes after a cool-down on the virtual clock.
- Add a resume capability: persist the report after each wave so a crashed orchestrator can recover, and show the audit is still clean.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Mock** | [`resources/loan_services.py`](resources/loan_services.py): `Services(seed, p_transient, p_timeout_after, p_timeout_before, permanent_tools, script)` with `call`, `audit`, `calls`; `MockPlanner(seed, p_bad, stubborn)`; `FakeClock` with `fork()`; `TOOLS` |
| **Data** | Loan requests are dictionaries `{loan, member, amount}` that you generate in your tests; members whose id starts with `X` are ineligible |
| **Provenance** | **Synthetic**; fictional names and amounts, no real person, account or business |
| **Licence** | CC BY 4.0 (content), MIT (code) |
| **Size** | Nothing committed beyond a few KB of Python |
| **Model access** | None. No network, key, GPU or download |

Hidden tests use other seeds, failure rates up to 40% timeout-after-effect, stubborn planners, other retry policies and plan shapes, slow branches, and a no-idempotency ablation.

**Setup**

```bash
cd assessments/ai-engineering/tier-2/units/AI-07-agentic-workflows-and-orchestration/AI-T2-013-the-double-credit
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
| 1 | `sagarun/` package | R1 to R6 |
| 2 | `tests/test_member_*.py` (at least 12 tests) | Your own scripted-behaviour tests |
| 3 | `experiments.py` | Reproduces the policy table: retry attempts, compensation attempts, idempotency on/off, sequential versus wave execution |
| 4 | `REPORT.md` (at most 1,500 words plus tables), from the [template](submission-template/REPORT.md) | Operations memo; carries the AI-use declaration |
| 5 | A 5-minute technical defence (live) | Verifies understanding (see §K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion below holds. Criteria marked (T) are checked by the public and hidden test suites; the rest are checked by hand.

1. (T) `pytest` passes the provided tests and your own from a clean environment.
2. (T) `validate_plan` and `waves` return the exact lists and messages for each defect kind, including combined defects.
3. (T) `call_step` produces the exact backoff schedule, never retries a permanent error and never sleeps after the last attempt.
4. (T) After a batch of 120 loans with 20% transient, 20% timeout-after-effect and 10% timeout-before-effect rates and 30% defective plans, `violations` is empty for three seeds, and also for a 40% timeout-after-effect world.
5. (T) A failure leaves the back-end exactly as it was: the failed step is compensated first, then completed steps in reverse order, and a failing undo yields `stuck`, not silence. *Justification:* an ambiguous timeout is indistinguishable from a failure, so the failed step must be assumed applied.
6. (T) No effectful call is made before approval of a loan at or above the threshold; an invalid plan makes zero calls.
7. The report shows, with your own numbers, the makespan saved by waves, what removing idempotency does to the audit, and the cost of your retry and compensation budgets.

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

1. **Create your own private repository** named `clbg-AI-T2-013-<your-github-username>`, copying this assessment's `starter/`, `tests/`, `resources/` and `submission-template/` folders.
2. **Expected structure:** `sagarun/` (your package), `tests/` (provided tests plus your `test_member_*.py`), `resources/` (unchanged), `requirements.txt`, `REPORT.md` (from the template, which includes the AI-use declaration).
3. **Commit as you work.** Your commit history is part of the evidence (see §K).
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing a submission issue using the **Assessment submission** template, with the repository URL and the exact commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines). General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

Optional. They are recognised in feedback but never stand in for the core requirements.

1. **Circuit breaker.** Stop calling a service after consecutive failures; test on the virtual clock.
2. **Saga log.** Persist each step outcome and prove a crash between two waves is recoverable.
3. **MCP framing.** Describe how the tool catalogue would be exposed through the Model Context Protocol and what trust boundary that creates; optional, never graded.

---

## K. Assessment Integrity

**AI tools are permitted** to help you learn, for example to explain a concept or review your code. **They are not permitted to do the assessment for you.** You must be able to explain and change every line you submit.

- **Disclose** all AI assistance in the declaration section of `REPORT.md` (tool, purpose, example prompt). Undisclosed use that becomes apparent at defence is an integrity breach; disclosed, reasonable use is not penalised.
- **Cite** any code adapted from documentation or other sources.
- **Collaboration:** you may discuss general techniques with other members. You may not share code, numbers or report text.
- **How your understanding is verified.** In a 5-minute defence the assessor will (1) ask why the failed step must be compensated and what `debit_wallet` does if the credit never happened; (2) ask what happens to your audit if the idempotency key includes the attempt number; (3) give an unseen change, such as an SMS that must go out before the ledger post, and ask what your validator and your compensation do with it.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

*This section explains the design of the assessment for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | Python exceptions, graph layering and pytest. No model internals. |
| **New skill developed** | Reasoning about ambiguous failures in a system with irreversible side effects, and engineering the safeguards that make an AI-planned workflow safe. |
| **Decisions the member must make** | Retry and compensation budgets, how to order compensation, what to log, how to batch approvals, and how to measure the cost of safety. |
| **What must be investigated independently** | Which safeguard prevents which inconsistency, by switching each off and reading the audit. |
| **Why it is interesting** | A timeout is not a failure: the most dangerous outcome is the one where the money moved and nobody knows. |
| **Evidence of competence** | A clean audit under harsh failure rates, exact error strings, and an ablation that shows what each safeguard buys. |
| **Misconceptions exposed** | 'If the call failed nothing happened.' 'Retries are always safe.' 'The model's plan can be executed as written.' |
| **Preparation for later work** | Leads into AI-T3-009 (orchestration pattern trade-offs), AI-06 tool-calling agents and AI-11 approval and trust-boundary design. |

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
