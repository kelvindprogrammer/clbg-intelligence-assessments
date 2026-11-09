# DS-T2-023: Late Arrivals

> *A dashboard that updates by adding up the new batch is easy. One that stays correct when yesterday's events arrive today, twice, and amended, is engineering.*

![Format: implementation](https://img.shields.io/badge/format-implementation-6f42c1) ![Tier 2](https://img.shields.io/badge/tier-2-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `DS-T2-023` |
| **Title** | Late Arrivals: Incremental Revenue Aggregation with Watermarks, Corrections and Bounded Memory |
| **Subtrack** | Data Science |
| **Tier** | 2: Applied Competence and Method Selection |
| **Unit** | [DS-11: Analytical Pipelines and Data Engineering](../README.md) |
| **Format** | Implementation (secondary: System design) |
| **Difficulty** | Technical 3 · Mathematical 2 · Research 2 · Engineering 4 · Ambiguity 3 · Resources 1 (each out of 5) |
| **Estimated time** | 14–22 hours over 2 weeks |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM. No GPU, no paid services, and no internet after setup |
| **Recommended prerequisites** | Dictionaries, classes and JSON in Python; datetime handling; the idea of idempotency (see DS-T1-027); property-based thinking about tests. |
| **Skills developed** | Incremental aggregation; event time versus arrival time; watermarks and allowed lateness; at-least-once delivery and deduplication; state pruning; checkpointing and restart; oracle-based testing |
| **Technologies** | Python 3.10+, pandas (for the sweep table only), pytest. Standard library for everything else. |

---

## B. Problem Statement

A telecom's airtime reseller platform records top-ups in four regions. Agents' phones and regional gateways forward events to head office in **daily batches**, and the finance dashboard shows revenue per day per region. The platform team has been recomputing the whole table from scratch every night, which now takes hours. They want an **incremental** job that updates the totals as each batch arrives, and gives exactly the numbers the full recompute would.

Real event streams are awkward in three ways, all of which appear in the data you have been given:

- **Event time is not arrival time.** A top-up made on Monday may arrive in Tuesday's batch, or on Thursday's. Day totals therefore keep changing after the day is over.
- **Delivery is at-least-once.** Gateways resend "to be safe". The same event appears twice, sometimes in the next batch, and must not be counted twice.
- **Events get corrected.** A reversal or amendment arrives as the same `event_id` with a higher `version` and a new amount (and sometimes a different region). The old amount must be **retracted** from its old day and region and the new one added.

Two operational facts make this hard. First, the job runs for years, so it cannot remember every `event_id` forever: **memory must be bounded**. Second, the job will be restarted (deployments, crashes), so it must **checkpoint** its state to JSON and resume exactly.

The compromise that makes both possible is a **watermark** with an *allowed lateness*: an event older than the watermark is declared too late, recorded in a reject list for finance to look at, and does not change the totals. Then ids older than the watermark can be forgotten safely, because nothing about them can matter again.

The semantics are specified in the starter docstring (they are precise, and the tests enforce them). What is **not** specified is how you build it: your state design, how you prune safely, how you structure the checkpoint, and above all **how you test it**. A pipeline like this fails quietly: totals that are off by a few events never raise an exception. Your defence against that is an independent oracle (`recompute`) and tests that compare the two under many batch layouts.

Finally the business must choose the allowed lateness. Too small and revenue is rejected; too large and memory grows and old days keep changing. `lateness_sweep` turns that into evidence, and your report must recommend a value and defend it.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. Maintain a keyed aggregate incrementally and prove, by test, that it equals a full recompute.
2. Implement event-time watermarks with allowed lateness and the exact too-late rule.
3. Handle at-least-once duplicates and versioned corrections with retraction across keys.
4. Prune per-event state without changing any result, and show that memory is bounded.
5. Checkpoint and restore pipeline state through JSON and verify restart-equivalence at every cut point.
6. Use a sweep over the lateness parameter to support a business recommendation.

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

Behaviour is specified exactly in the starter docstring; the design is yours. Implement the `incragg` package in [`starter/incragg/`](starter/incragg/). The function signatures are fixed because the automated tests import them. The internals are yours.

| ID | Requirement |
|---|---|
| **R1** | `Aggregator(lateness_hours)` with `apply_batch(events) -> BatchReport(applied, duplicates, corrections, too_late)` implementing the stated semantics: events in list order; the too-late test uses the watermark **as it stood before the batch**; corrections retract and re-add across keys; keys with zero events disappear. |
| **R2** | `watermark()`, `totals()` (`{(date, region): (n_events, amount_kobo)}`) and `late_rejects()`. |
| **R3** | `state_size()`: the number of per-event records retained. After each batch you may keep only records that could still matter; the hidden tests check that memory tracks the lateness window rather than the stream length. |
| **R4** | `snapshot()` and `Aggregator.from_snapshot(snap)`: JSON-serialisable state; a restored aggregator continues to exactly the same totals, reject list and state size as an uninterrupted one, from any cut point. |
| **R5** | `recompute(batches, lateness_hours)`: totals from scratch, written to be an **independent**, simple oracle. If it shares code with `Aggregator`, it proves nothing; say how you ensured independence. |
| **R6** | `lateness_sweep(batches, hours_list) -> DataFrame[lateness_hours, too_late, state_size_end, accepted_share]` where `accepted_share` is revenue in the totals divided by revenue under effectively unlimited lateness. |

### D.2 Engineering requirements (mandatory)

- **No re-reading.** `apply_batch` may not look at earlier batches; everything it needs is in the aggregator's state.
- **Determinism.** Same inputs, same outputs; no wall-clock use.
- **Test design.** Your own tests must include an oracle comparison over several random re-splittings of the same events into batches, and a restart test at every cut point.
- **Tests.** Keep the provided tests passing and add **at least 10 tests of your own** in `tests/test_member_*.py`, including edge cases you found yourself.
- **Dependencies.** Use only the packages in [`starter/requirements.txt`](starter/requirements.txt). If you add one, justify it in your report.

### D.3 Privacy and responsibility

The data is **synthetic**; no agent, subscriber or phone number appears. Real top-up events link subscribers to purchases and are personal data under the Nigeria Data Protection Act 2023. In your report, say what you would store in the reject list and checkpoint if events carried a subscriber number (minimisation, pseudonymisation, retention) and who should read the reject list.

### D.4 Optional enhancements (not required for full marks)

- A `--explain EVENT_ID` helper that reports what the aggregator did with one event across batches.
- Handle a correction that moves an event to a different `event_time`, and explain why the spec forbids it.
- Memory profile: plot `state_size` per batch for three lateness settings.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Dataset** | [`resources/data/batches/`](resources/data/batches/): ten daily batch files `batch_2026-04-06.csv` to `batch_2026-04-15.csv` (about 1,100 events in total, with redeliveries and corrections), about 80 KB; columns `event_id`, `version`, `event_time`, `region`, `amount_kobo` |
| **Provenance** | **Synthetic**, generated by CLBG with a fixed seed. About 78% of events arrive in their own day's batch, the rest up to nine days late; about 4% are redelivered and about 3% corrected. All identifiers are fictional. |
| **Licence** | CC BY 4.0, free to reuse with attribution |
| **Integrity** | The contract test checks a SHA-256 over all ten files, so do not edit them |

**Known limitations (by design).** Batches are daily and in memory; there is no real stream, clock or concurrency. Events are never corrected to a different `event_time`. The hidden tests regenerate streams with different seeds, sizes and lateness values, including `lateness_hours = 0`.

**Setup**

```bash
cd assessments/data-science/tier-2/units/DS-11-analytical-pipelines-and-data-engineering/DS-T2-023-late-arrivals
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract        # should pass immediately: checks data and scaffold
pytest                    # most tests fail until you implement the package
```

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `incragg/` package (the completed starter) | The core technical evidence |
| 2 | `tests/test_member_*.py` | Shows you can pin behaviour down and think about edge cases |
| 3 | `outputs/lateness_sweep.csv` and a chart | The evidence behind your lateness recommendation |
| 4 | `checkpoint_demo.py` | Runs half the stream, checkpoints through JSON, resumes, and compares with an uninterrupted run |
| 5 | `REPORT.md` (from the [template](submission-template/REPORT.md)), with the AI-use declaration inside | Communicates decisions and limits; integrity declaration (see §K) |
| 6 | A 5-minute technical defence (live) | Verifies understanding (see §K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion below holds. Criteria marked ⚙ are checked by the public and hidden test suites, the rest by hand.

1. ⚙ Provided and member tests pass from a clean environment.
2. ⚙ **Oracle equality:** on hidden streams (several seeds, sizes and lateness values including 0), `totals()`, every `BatchReport` and the ordered reject list equal an independent oracle exactly. *Justification:* the semantics are deterministic, so there is no tolerance.
3. ⚙ **Bounded memory:** after the last batch `state_size()` does not exceed the number of distinct events with `event_time` at or above the watermark minus 24 hours. *Justification:* the exact bound is the number at or above the watermark; 24 hours of slack allows lazy pruning.
4. ⚙ **Restart equivalence:** a snapshot taken after any batch, round-tripped through JSON, resumes to identical totals.
5. ⚙ **Oracle independence in practice:** `recompute` matches an independent oracle on batches re-split at random boundaries, and with unlimited lateness is independent of batch order.
6. ⚙ `lateness_sweep` matches the oracle's accepted share, and is monotone in lateness.
7. ✍ The report recommends a lateness with evidence from the sweep and explains what the business gives up on each side.
8. ✍ The report explains why pruning below the watermark is safe, and what would make it unsafe.

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

The outcome is decided by the score **and** the gates: a passing defence, a reproducible run and an integrity declaration. See the [placement framework](../../../../../../docs/placement-framework.md).

---

## I. Submission Instructions

1. **Create your own private repository** named `clbg-DS-T2-023-<your-github-username>` and copy this assessment's `starter/`, `tests/`, `resources/` and `submission-template/` into it. Your package sits at the repository top level.
2. Commit as you work. Your commit history is part of the evidence (see §K); a single "final" commit will be questioned at defence.
3. Add your outputs and `REPORT.md`, then run `pytest` from a clean environment built from your `requirements.txt`.
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing a submission issue in the CLBG assessments repository, using the **Assessment submission** template. Include the repository URL and the exact commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see the [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines). General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

Optional. They are recognised in feedback and can strengthen a placement case, but never stand in for the core requirements.

1. **Idempotent batches.** Make `apply_batch` safe if the same batch is delivered twice (what identifies a batch?).
2. **Per-region lateness.** Allow a different allowed lateness for each region and discuss the effect on the global watermark.
3. **Retractions to downstream.** Emit a change-log of (key, delta) so a dashboard can update without reading `totals()`.

---

## K. Assessment Integrity

**AI tools are permitted** to help you learn, for example to explain a concept, suggest an idiom or review your code. **They are not permitted to do the assessment for you.** You must be able to explain and change every line you submit.

- **Disclose** all AI assistance in the declaration section of `REPORT.md`: which tool, what for, an example prompt, and how you verified the output. Undisclosed use that becomes apparent at defence is an integrity breach. Disclosed, reasonable use is not penalised.
- **Cite** any code adapted from documentation or other sources, with a link.
- **Collaboration:** you may discuss *general techniques* with other members. You may not share code, numbers, thresholds or report text.
- **How your understanding is verified.** In the 5-minute defence the assessor will: 
  1. picks one event id and asks you to trace what happened to it across the batches in which it appeared;
  2. asks why the too-late test uses the watermark from before the batch, and what would break if it used the updated one;
  3. gives you an unseen modification, for example a second correction type or a per-region lateness, and asks you to change the code and add the tests live.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

*This section explains the design of the assessment for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | Python classes and dicts, datetime, JSON, tests against an oracle. Idempotent loading helps. |
| **New skill developed** | Reasoning about event time, state and correctness over time; proving incremental equals batch. |
| **Decisions the member must make** | State layout; when and what to prune; checkpoint format; how to make the oracle independent; which lateness to recommend. |
| **What must be investigated independently** | How much revenue arrives late, how late, and what a given lateness costs. |
| **Why it's interesting** | Every real reporting pipeline meets late, duplicated and corrected data; the watermark idea is the same in every streaming framework. |
| **Evidence of competence** | Exact oracle equality across hidden streams, a pruning bound, restart equivalence at every cut and a defended parameter choice. |
| **Misconceptions exposed** | Add the new batch to yesterday's totals is enough. Dedup needs unbounded memory. Restarts are harmless. |
| **Preparation for later work** | Leads to DS-T3 data contracts and drift gates and to production streaming frameworks, whose semantics this reproduces in miniature. |

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
