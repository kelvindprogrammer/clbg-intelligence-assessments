# DS-T3-020: Same Schema, Different Truth

> *The worst data incident is the one where every check is green. Build a gate that catches changes of meaning, and measure how often it cries wolf.*

![Format: system-design](https://img.shields.io/badge/format-system%20design-6f42c1) ![Tier 3](https://img.shields.io/badge/tier-3-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `DS-T3-020` |
| **Title** | Same Schema, Different Truth: A Data-Contract and Drift Gate for a Market-Price Feed |
| **Subtrack** | Data Science |
| **Tier** | 3: Advanced Practice and Research-Informed Judgement |
| **Unit** | [DS-11: Analytical Pipelines and Data Engineering](../README.md) |
| **Format** | System design (secondary: Implementation) |
| **Difficulty** | Technical 4 · Mathematical 3 · Research 3 · Engineering 5 · Ambiguity 4 · Resources 1 (each out of 5) |
| **Estimated time** | 22–34 hours over 3 weeks |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM. No GPU, no paid services, and no internet after setup |
| **Recommended prerequisites** | DS-T1-027 and DS-T2-023 or equivalent (loading, validation and incremental processing); pandas group-by and robust statistics; YAML; an understanding of false-positive/false-negative trade-offs. |
| **Skills developed** | Data contracts; schema evolution classification; rule validation with rates; drift detection against a learned baseline; threshold calibration; fault injection; operating-characteristic estimation; gate policy design |
| **Technologies** | Python 3.10+, pandas, NumPy, PyYAML, pytest. No data-quality framework is required, and none may stand in for your own design. |

---

## B. Problem Statement

The National Agricultural Price Desk publishes a daily national food-price index. It is fed by market surveys from state agencies: every day each agency sends a CSV of prices per commodity per market. Journalists, the central bank's inflation team and a food-aid programme all read the index. The pipeline between the CSVs and the index has failed in two instructive ways:

- A state renamed a column. The pipeline crashed, nobody was paged until the morning, and the index was late. This is a **loud** failure, cheap to catch.
- Another state switched its handsets from naira to **kobo**. Every column existed, every type was right, every row passed validation. The index that day showed food prices a hundred times too high. It was published, and quoted. This is a **silent** failure, and it is the one that costs credibility.

A data contract (what columns, types and value rules the feed promises) catches the first and cannot, alone, catch the second, because the unit change leaves all the promises technically true. Catching it needs a **baseline** of what the data normally looks like and a test for "this is not normal". But any such test has a price: prices inflate gradually, Sunday batches have fewer markets, some nulls are routine. A detector tuned to shout at everything unusual will block the index every Monday, and a team that is paged for false alarms stops listening.

You have the contract (`resources/contract.yaml`, deliberately written with loose limits: it was written before anyone imagined a kobo handset), and a stream of 30 daily batches. The first 15 are known clean. The last 15 contain faults of kinds you will need to work out, plus ordinary variation that is **not** a fault. Nobody tells you which is which. Hidden tests run your gate on freshly generated streams in which the faults are scheduled differently.

Your task is to design and build the gate, and to **measure** it:

1. Classify schema changes (missing, retyped, new columns) with rules a consumer can defend.
2. Enforce the contract's rules by *rate*, not by presence: one bad row in a hundred is within tolerance, ten is not.
3. Learn a baseline from clean history and detect semantic drift the contract cannot see, with thresholds set from observed normal variation and justified in the report.
4. Combine everything into an accept, quarantine or block decision with reason codes.
5. Build a **fault-injection harness** that applies each known fault to clean batches, and use it to estimate, per fault kind, how often your gate catches it and, on clean batches, how often it raises a false alarm.

At Tier 3 you are given interfaces, a reason-code vocabulary and a policy table, but the detection method, the thresholds, the baseline update policy and the argument for the operating point are yours to design and defend.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. Classify schema changes by consumer impact and justify each classification.
2. Express a data contract as rate-based rules and see where a contract alone is blind.
3. Learn a baseline from clean history and detect distribution and unit drift with calibrated thresholds.
4. Separate faults from normal variation (inflation, weekly volume, routine nulls).
5. Estimate a gate's detection and false-alarm rates with fault injection, and report them honestly.
6. Argue the choice among accept, quarantine and block for each fault family in terms of cost.

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

Interfaces, reason codes and the action policy are exact; the detection design is yours. Implement the `contractgate` package in [`starter/contractgate/`](starter/contractgate/). The function signatures are fixed because the automated tests import them. The internals are yours.

| ID | Requirement |
|---|---|
| **R1** | `infer_schema(df)` maps each column to `int`, `float` or `string`. |
| **R2** | `diff_schema(contract, schema)` returns reason codes: `schema:missing_column:<col>`, `schema:type_change:<col>` (numeric contract types accept int or float; string accepts only string) and the informational `schema:new_column:<col>`. |
| **R3** | `validate_batch(df, contract)` returns `rule:null|category|date_format|range:<col>` and `rule:key_duplicate:key` codes **only when the violating share of rows exceeds the contract's allowed rate**; absent or retyped columns are skipped without error. It must tolerate empty batches. |
| **R4** | `fit_baseline(batches, contract)` and `detect_drift(df, baseline)`: learn from clean batches and return `drift:scale_shift:<col>` and `drift:null_rate:<col>` codes. Thresholds must come from observed variation in the baseline batches and be explained in the report; a 12% price rise and a Sunday batch with fewer rows must not trigger. |
| **R5** | `gate(df, contract, baseline) -> Decision` combines schema, rule and drift reasons using the provided `decide`. Informational reasons never stop a batch. The gate must not crash on hostile input (empty frames, missing or retyped columns). |
| **R6** | `run_stream(batches, contract, n_baseline=15)`: fit on the first `n_baseline` batches, then return one `Decision` per remaining batch. |
| **R7** | `inject_fault(df, kind, seed)`: copy a batch with exactly one fault of a kind in `KINDS` (effects specified in the starter docstring), deterministic in `seed`; `ValueError` for unknown kinds. |
| **R8** | `operating_characteristics(batches, contract, n_fit, n_eval, seed)`: a `[kind, n, detected, rate]` table; the `clean` row counts false alarms, each fault row counts batches on which the gate's action equals `KINDS[kind]`. |

### D.2 Engineering requirements (mandatory)

- **No leakage from the test stream.** The baseline is fit on known-clean history only; do not tune thresholds on batches 15–29 of the public stream.
- **Determinism and speed.** A full `run_stream` over 30 batches takes seconds, not minutes.
- **Explainable output.** Every non-accept decision carries at least one reason code naming the column responsible.
- **Tests.** Keep the provided tests passing and add **at least 12 tests of your own** in `tests/test_member_*.py`, including edge cases you found yourself.
- **Dependencies.** Use only the packages in [`starter/requirements.txt`](starter/requirements.txt). If you add one, justify it in your report.

### D.3 Privacy and responsibility

The data is **synthetic**: markets, states and prices are fictional. Real price feeds are public statistics, but market-level collector data can reveal individual traders in small markets. In your report, state what you would log when quarantining a batch (batch metadata and aggregates, not raw rows), who needs access to quarantined data, and how alerts should be worded so that they do not expose an identifiable source.

### D.4 Optional enhancements (not required for full marks)

- Treat the baseline as rolling: update it with accepted batches only and show the effect on inflation handling and on a slow-drift fault you design.
- Write the contract as a machine-readable schema (for example JSON Schema or pandera) and compare what it can and cannot express with your YAML rules.
- A cost model: assign costs to false alarms, missed faults and delayed publication, and choose thresholds that minimise expected cost.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Dataset** | [`resources/data/batches/`](resources/data/batches/): 30 daily batches `batch_00.csv` to `batch_29.csv` (about 80–100 rows each: 20 markets × 5 commodities; Sundays are smaller), about 130 KB. [`resources/contract.yaml`](resources/contract.yaml): the data contract. |
| **Provenance** | **Synthetic**, generated by CLBG with a fixed seed: market price levels, 0.3% daily inflation, lognormal noise, 2% routine null `state`. Batches 0–14 are clean; batches 15–29 contain faults and clean days in an order you must discover. No real agency or market is described. |
| **Licence** | CC BY 4.0, free to reuse with attribution |
| **Integrity** | The contract test checks a SHA-256 over all 30 batches, so do not edit them |

**Policy table (fault kind, expected action, what a sensible reason code looks like).** `rename_column`: block, `schema:missing_column`. `new_column`: accept, `schema:new_column` (informational). `type_change`: block, `schema:type_change`. `unit_change`: block, `drift:scale_shift`. `null_spike`: quarantine, `drift:null_rate` or `rule:null`. `new_category`: quarantine, `rule:category`. `date_flip`: block, `rule:date_format`. `dup_keys`: quarantine, `rule:key_duplicate`.

**Known limitations (by design).** One feed, one handset-level fault family, 15 clean baseline batches. Dates flipped on days of the month of 12 or below cannot be detected by parsing, and the stream is built so that this case does not arise; discuss it in your report. Hidden streams use different seeds, fault days and affected columns.

**Setup**

```bash
cd assessments/data-science/tier-3/units/DS-11-analytical-pipelines-and-data-engineering/DS-T3-020-same-schema-different-truth
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract        # should pass immediately: checks data and scaffold
pytest                    # most tests fail until you implement the package
```

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `contractgate/` package (the completed starter) | The core technical evidence |
| 2 | `tests/test_member_*.py` | Shows you can pin behaviour down and think about edge cases |
| 3 | `outputs/operating_characteristics.csv` and a short table of thresholds with the evidence for each | Your measured detection and false-alarm rates, and where each threshold came from |
| 4 | `gate_log.csv`: the decision and reasons for batches 15 to 29 of the public stream | The result a data steward would act on |
| 5 | `analysis.py` or `analysis.ipynb` | Regenerates the thresholds, the operating characteristics and the log |
| 6 | `REPORT.md` (from the [template](submission-template/REPORT.md)), with the AI-use declaration inside | Communicates decisions and limits; integrity declaration (see §K) |
| 7 | A 5-minute technical defence (live) | Verifies understanding (see §K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion below holds. Criteria marked ⚙ are checked by the public and hidden test suites, the rest by hand.

1. ⚙ Provided and member tests pass from a clean environment.
2. ⚙ Schema, rule and drift reason codes are exactly as specified on the public planted tests; the gate never crashes on hostile batches.
3. ⚙ **Hidden fault handling:** on five freshly generated streams, each with eight scheduled faults, at most **one** fault per stream gets the wrong action. *Justification:* every fault is a gross, designed change (a 100× unit shift, a 25% null spike, a 25% duplicate surge), so a calibrated gate has headroom; one miss allows for a borderline threshold choice.
4. ⚙ **Hidden false alarms:** across the seven clean days of every stream, **no** batch is blocked and at most **one** is quarantined.
5. ⚙ **Attribution:** at least seven of the eight faults carry a reason code naming the correct column (or `key` for duplicates).
6. ⚙ **Your harness is honest:** `inject_fault` has the specified effects, is deterministic, and `operating_characteristics` reports a false-alarm rate of at most 0.2 and a detection rate of at least 0.8 for every kind on the public clean batches.
7. ✍ The report explains how each threshold was derived from observed variation in clean history and shows the evidence.
8. ✍ The report argues the accept, quarantine and block assignment for each fault family in terms of cost, and names a fault your gate would miss.
9. ✍ The report states the limits of 15 baseline batches and one synthetic feed.

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

1. **Create your own private repository** named `clbg-DS-T3-020-<your-github-username>` and copy this assessment's `starter/`, `tests/`, `resources/` and `submission-template/` into it. Your package sits at the repository top level.
2. Commit as you work. Your commit history is part of the evidence (see §K); a single "final" commit will be questioned at defence.
3. Add your outputs and `REPORT.md`, then run `pytest` from a clean environment built from your `requirements.txt`.
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing a submission issue in the CLBG assessments repository, using the **Assessment submission** template. Include the repository URL and the exact commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see the [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines). General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

Optional. They are recognised in feedback and can strengthen a placement case, but never stand in for the core requirements.

1. **Slow drift.** Design and detect a 1%-per-day creeping price shift, and explain why the gate's inflation tolerance makes it hard.
2. **Per-state baselines.** Detect a unit change affecting only one state's rows, and measure the cost in false alarms.
3. **Alert design.** Write the message a steward receives for a quarantined batch, and test with a colleague whether they can act on it.

---

## K. Assessment Integrity

**AI tools are permitted** to help you learn, for example to explain a concept, suggest an idiom or review your code. **They are not permitted to do the assessment for you.** You must be able to explain and change every line you submit.

- **Disclose** all AI assistance in the declaration section of `REPORT.md`: which tool, what for, an example prompt, and how you verified the output. Undisclosed use that becomes apparent at defence is an integrity breach. Disclosed, reasonable use is not penalised.
- **Cite** any code adapted from documentation or other sources, with a link.
- **Collaboration:** you may discuss *general techniques* with other members. You may not share code, numbers, thresholds or report text.
- **How your understanding is verified.** In the 5-minute defence the assessor will: 
  1. picks one threshold in your gate and asks where its value came from and what happens if it doubles or halves;
  2. asks why a unit change passes a contract that is stricter than it looks, and what the contract author should change;
  3. gives you an unseen modification, for example a new fault kind (a 10% price shift in one state, or a swapped pair of columns), and asks you to extend the injector, the detector and the operating-characteristics table live.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

*This section explains the design of the assessment for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | Validation rules and quarantine, group-by statistics, robust location and spread, false-positive and false-negative thinking. |
| **New skill developed** | Designing a quality gate as a measurable classifier: with a policy, thresholds derived from data and a harness that estimates its error rates. |
| **Decisions the member must make** | How to treat each schema change; which statistics to baseline; how to set thresholds; whether to update the baseline; which fault goes to which action. |
| **What must be investigated independently** | What normal variation looks like in the feed, and which of the last 15 public batches are faulty and why. |
| **Why it's interesting** | Silent semantic changes are the most expensive data incidents, and a gate's value depends as much on its false alarms as on its catches. |
| **Evidence of competence** | Hidden-stream fault handling and false-alarm limits, correct attribution, an honest harness and a threshold argument grounded in measured variation. |
| **Misconceptions exposed** | A passing schema means correct data. Any anomaly detector is good. Thresholds can be eyeballed on the test stream. |
| **Preparation for later work** | Leads to data observability, model monitoring in ML engineering and the governance of shared data products. |

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
