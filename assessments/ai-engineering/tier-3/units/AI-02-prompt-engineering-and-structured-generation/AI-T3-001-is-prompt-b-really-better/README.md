# AI-T3-001: Is Prompt B Really Better? A Regression Gate for Prompts in a Multilingual Care Bot

> *Every prompt edit looks like an improvement on the five examples someone tried. Design an evaluation protocol and a ship/block gate whose error rates you can state, and defend what it cannot see.*

![Format: Open-ended (secondary: Investigation)](https://img.shields.io/badge/format-open-ended-6f42c1) ![Tier 3](https://img.shields.io/badge/tier-3-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `AI-T3-001` |
| **Title** | Is Prompt B Really Better? A Regression Gate for Prompts in a Multilingual Care Bot |
| **Subtrack** | AI Engineering |
| **Tier** | 3: Advanced and Research-Grade |
| **Unit** | [AI-02: Prompt Engineering and Structured Generation](../README.md) |
| **Format** | Open-ended (secondary: Investigation) |
| **Difficulty** | Technical 4 · Mathematical 4 · Research 4 · Engineering 3 · Ambiguity 5 · Resources 1 (each out of 5) |
| **Estimated time** | 24-34 hours over 3 weeks |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM, CPU only. No GPU, no paid API, no network, no model download. The graded path uses a deterministic mock; the full test run takes under a minute |
| **Recommended prerequisites** | Confidence intervals and the bootstrap; hypothesis testing and multiple comparisons at the level of an applied statistics course; numpy. Recommended: AI-T2-002 and a statistics unit |
| **Skills developed** | Designing an evaluation protocol for non-deterministic systems; item-clustered paired inference; multiple-comparison control across slices; power and sample-size planning; contamination checks; quantifying a gate's operating characteristics by simulation; arguing validity |
| **Technologies** | Python 3.10+, numpy, pytest (statistics from the standard library allowed) |

---

## B. Problem Statement

Naija Connect (fictional) runs a customer-care bot for a telecom. The bot routes messages in English, Pidgin, Yoruba and Hausa to intents, with a structured JSON reply. About one prompt change a day is proposed: more examples, fewer examples, "think step by step", a longer instruction, a new safety sentence. Each author tests on a handful of messages and reports "B is better". Last quarter two such changes shipped and quietly made Yoruba routing worse because the average went up, and one removed the injection guard because nobody tested attack messages. Management wants an automatic gate in the release pipeline: **ship**, **block**, or **inconclusive** (get more data).

Nobody can say what such a gate should be. Run once, a model is noisy: the same prompt with another sampling seed gives different answers. Evaluation items differ enormously in difficulty, so a comparison that ignores pairing wastes most of its power. Languages and the attack slice are small, so slice results are noisy, and checking five slices at 5% each makes a false alarm likely. A bigger evaluation set costs money and delays releases. A gate that blocks too often will be bypassed; one that never blocks is theatre.

You will design the protocol and build the gate. The model is a **prompt-sensitive mock** (`resources/prompt_mock.py`): a documented simulator in which prompts move accuracy by language, structured-output requests reduce format failures, a guard sentence reduces hijacking of attack messages, long prompts cost accuracy, and outputs are noisy across sampling seeds and fixed in difficulty per item. Because the mock's effects are documented, you can create regressions of known size and measure how often your gate catches them. That is the research move: **evaluate the evaluator**.

The brief fixes function signatures and a few acceptance bars. Everything of substance is yours to decide and defend: how to resample, whether and how to correct across slices, what "inconclusive" means, what the tolerance is, how many items and seeds to spend, and what to do about contamination.

> **Why this matters beyond this task.** Prompt and model changes are the main source of silent quality regressions in LLM products. A gate with known error rates turns "it seems better" into an engineering decision.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. **Choose** the resampling unit and pairing for noisy, item-heterogeneous LLM evaluations, and show why it matters.
2. **Control** false alarms across language and attack slices without losing all power, and justify the trade-off.
3. **Plan** evaluation size and seed count from variance and a minimum effect worth detecting.
4. **Measure** the gate's false-block, detection and inconclusive rates by simulation, including against naive alternatives.
5. **Detect** contamination between prompt examples and evaluation items.
6. **Argue** the limits of validity: what a mock, an item set and a significance rule can and cannot support.

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

Implement `promptlab` in [`starter/promptlab/`](starter/promptlab/). Interfaces are fixed; where the brief is silent the choices are yours to make and defend. Stubs raise `NotImplementedError("R<n>: ...")`.

Items are `{"id", "text", "lang", "intent", "attack"}`. Result matrices are boolean arrays of shape `(n_items, n_seeds)`; `slices` maps a name to a boolean item mask. `DEFAULT_GATE` in the starter is a starting point.

| ID | Requirement |
|---|---|
| **R1** | `evaluate_prompt(mock, prompt, items, seeds) -> np.ndarray[bool]` of shape `(n_items, n_seeds)`, column `j` equal to `mock.run(prompt, items, seeds[j])`. Raise `ValueError` for empty items or for empty or duplicate seeds (a repeated seed repeats the noise and fakes precision). |
| **R2** | `paired_bootstrap(old, new, n_boot=1000, level=0.95, seed=0) -> {"diff", "lo", "hi"}`. `diff` is the mean accuracy of `new` minus `old`; the interval is a percentile bootstrap that **resamples items** (all seeds of an item travel together) on per-item paired differences. Deterministic given `seed`; `ValueError` on shape mismatch. |
| **R3** | `required_items(sd_diff, delta, alpha=0.05, power=0.8) -> int`: items needed to detect a paired mean difference `delta` given the per-item standard deviation of differences, two-sided normal approximation, rounded up. `ValueError` if `delta <= 0`. |
| **R4** | `check_leakage(prompt, items) -> list[str]`: ids of items whose text appears in the prompt, ignoring case and whitespace differences. |
| **R5** | `regression_gate(old, new, slices, cfg=None, seed=0) -> dict` with `decision` in `"ship"`, `"block"`, `"inconclusive"`, `reasons` (strings; each reason names the slice or `overall` that triggered it), `overall` (the R2 dict) and `slices` (name to R2-style dict for the slices actually tested). Slices with fewer than `cfg["min_slice_items"]` items are not tested. Deterministic given `seed`, and it never mutates its inputs. **Everything else is your design:** the correction across slices, margins, the meaning of `inconclusive`, defaults in `cfg`. |
| **R6** | `operating_characteristics(make_pair, gate, trials, seed=0) -> {"block_rate", "ship_rate", "inconclusive_rate"}`: call `make_pair(trial_seed)` to get `(old, new, slices)` for each of `trials` trials, apply `gate(old, new, slices, seed=...)`, and report decision shares. |

### D.2 Engineering requirements (mandatory)

- Deterministic: no wall-clock time, no global random state, no network. Everything randomised takes an explicit seed.
- At least **12 tests of your own** in `tests/test_member_*.py`; include a calibration test (cosmetic edits) and a power test (a known regression), each with a stated number of trials and a tolerance you justify.
- `experiments.py` regenerates every number in the report, including the operating characteristics of **at least three gate variants** (the naive rule 'block if the new mean is lower', an uncorrected item-level gate, and your gate) across at least four scenarios (cosmetic edit, guard removed, a language-specific regression, a mixed change such as chain-of-thought) and at least two evaluation sizes. Report trial counts and Monte Carlo error. Importing underscore-prefixed names from `resources/` is forbidden.
- `REPORT.md` (from the [template](submission-template/REPORT.md)) carries every number you cite, reproducible with one command you document.

### D.3 Responsibility

The mock is fictional, but the harm model is not. In the report, write one paragraph on who is harmed when a gate ships a Yoruba or Hausa regression because the aggregate looked fine, who decides what a minimum tolerable drop is for a minority-language slice, and why the choice of slices is itself a fairness decision. Say what real evaluation data from customers would require under the Nigeria Data Protection Act 2023 (consent or another lawful basis, minimisation, retention) and why synthetic items cannot replace it.

### D.4 Optional enhancements

- Sequential testing: let the gate request more seeds or items until it can decide, and show the error rates are preserved.
- A cost model: expected cost of a false block versus a missed regression, and the gate threshold that minimises it.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Mock model** | [`resources/prompt_mock.py`](resources/prompt_mock.py): `PromptMock(base_logit, difficulty_sd, format_fail, hijack, cot_effect).run(prompt, items, seed)`; the module docstring documents every effect |
| **Data** | `make_eval_set(seed, n)` returns care-bot messages in four languages with an intent label and a 10% attack slice; `make_prompt(shots, json, guard, cot, filler_words, tweak)` builds prompts the mock understands |
| **Provenance** | **Synthetic**: templated phrases in English, Pidgin, Yoruba and Hausa with random reference numbers; no real customer or operator message. The mock's effect sizes are invented for the exercise and are **not** findings about real models |
| **Licence** | CC BY 4.0 (content), MIT (code) |
| **Size** | Nothing committed beyond a 7 KB module |
| **Model access** | None. No network, key, GPU or download |

Hidden tests use a differently parameterised mock (lower baseline accuracy, lower difficulty variance, stronger hijacking), other eval-set seeds, 400 items and 4 seeds, and a different base prompt.

**Setup**

```bash
cd assessments/ai-engineering/tier-3/units/AI-02-prompt-engineering-and-structured-generation/AI-T3-001-is-prompt-b-really-better
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
| 1 | `promptlab/` package | R1 to R6 |
| 2 | `tests/test_member_*.py` (at least 12 tests) | Includes calibration and power tests |
| 3 | `experiments.py` | Reproduces the operating-characteristics tables and a figure of detection rate against evaluation size |
| 4 | `REPORT.md` (at most 2,500 words plus tables), from the [template](submission-template/REPORT.md) | Protocol and validity argument for the release board; carries the AI-use declaration |
| 5 | A 5-minute technical defence (live) | Verifies understanding (see §K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion below holds. Criteria marked (T) are checked by the public and hidden test suites; the rest are checked by hand.

1. (T) `pytest` passes the provided tests and your own from a clean environment.
2. (T) R1 to R4 and R6 behave exactly as specified: duplicate seeds rejected, item-level resampling (a cell-level bootstrap fails the width test), exact `required_items` values, leakage matching.
3. (T) **Calibration.** Over 150 simulated cosmetic edits (300 items, 3 seeds, five slices), at most 12% are blocked. *Justification:* the reference blocks about 6.5%; nominal family-wise level is 5%, and a percentile bootstrap under-covers in small slices.
4. (T) **Power.** Removing the guard sentence is blocked in at least 85% of trials and a 160-word bloat in at least 80% (reference 97% and 95%). On a differently parameterised mock the thresholds are 80% and 90% for guard and structured-output removal, with at most 13% false blocks and at most 10% blocks of a pure improvement.
5. (T) **Honesty under thin data.** With 100 items and a real 4-point regression, at most 10% of trials are shipped (`inconclusive` or `block` is acceptable). A subgroup regression hidden by an overall gain is blocked and names the slice.
6. (T) **Slice power.** A Yoruba-only regression of about 9 points is blocked in at least 50% of trials at 900 items (reference 72%). The report must say what it implies for the evaluation budget (use `required_items`).
7. The report contains the three-variant operating-characteristics comparison, an evaluation-budget recommendation, a contamination procedure and a validity section that distinguishes the mock from real models.

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

1. **Create your own private repository** named `clbg-AI-T3-001-<your-github-username>`, copying this assessment's `starter/`, `tests/`, `resources/` and `submission-template/` folders.
2. **Expected structure:** `promptlab/` (your package), `tests/` (provided tests plus your `test_member_*.py`), `resources/` (unchanged), `requirements.txt`, `REPORT.md` (from the template, which includes the AI-use declaration).
3. **Commit as you work.** Your commit history is part of the evidence (see §K).
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing a submission issue using the **Assessment submission** template, with the repository URL and the exact commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines). General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

Optional. They are recognised in feedback but never stand in for the core requirements.

1. **Sequential gate.** Add early stopping with a spending function and verify the false-block rate.
2. **Bayesian alternative.** Compare a hierarchical model across languages with your frequentist gate on the same simulations.
3. **Real model replication.** If you have a local open-weight model, check whether item-difficulty correlation between prompts is as strong as the mock assumes (optional; never graded).

---

## K. Assessment Integrity

**AI tools are permitted** to help you learn, for example to explain a concept or review your code. **They are not permitted to do the assessment for you.** You must be able to explain and change every line you submit.

- **Disclose** all AI assistance in the declaration section of `REPORT.md` (tool, purpose, example prompt). Undisclosed use that becomes apparent at defence is an integrity breach; disclosed, reasonable use is not penalised.
- **Cite** any code adapted from documentation or other sources.
- **Collaboration:** you may discuss general techniques with other members. You may not share code, numbers or report text.
- **How your understanding is verified.** In a 5-minute defence the assessor will (1) ask why resampling cells instead of items makes your intervals too narrow, with the numbers from your experiments; (2) ask what your gate does about five slices versus fifty, and what that costs in power; (3) give an unseen change, such as the Yoruba slice halving in traffic or two prompt candidates compared at once, and ask which part of the protocol must change.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

*This section explains the design of the assessment for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | Applied statistics (intervals, error rates, power) and numpy. No model internals. |
| **New skill developed** | Evaluating an evaluator: stating a gate's false-alarm and detection rates from simulation instead of intuition. |
| **Decisions the member must make** | Resampling unit, slice correction, tolerance and the meaning of inconclusive, evaluation size and seed count, contamination procedure. |
| **What must be investigated independently** | How item correlation, seed noise and slice size interact; where a gate stops being able to protect a small language. |
| **Why it is interesting** | The popular practice (compare two averages on a few examples) blocks about as often as it ships a harmless edit, and misses what matters for minority-language users. |
| **Evidence of competence** | Operating characteristics that hold on a different mock, a defended protocol, and an honest validity section. |
| **Misconceptions exposed** | 'Higher average means better.' 'More seeds replace more items.' 'Significant means safe to ship.' |
| **Preparation for later work** | Leads into AI-03 evaluation methodology, AI-09 safety evaluation and ML-06 evaluation. |

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
