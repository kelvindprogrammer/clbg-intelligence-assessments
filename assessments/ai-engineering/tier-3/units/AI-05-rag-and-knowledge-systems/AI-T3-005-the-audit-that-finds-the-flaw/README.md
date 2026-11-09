# AI-T3-005: The Audit That Finds the Flaw: Validating a RAG Evaluation Harness with Planted Faults

> *A legal-aid charity wants to know whether its tenancy-rights assistant is safe to expand. Accuracy says 95 percent. Before you trust that number, show that your evaluation can actually find a broken assistant.*

![Format: investigation (secondary: comparative)](https://img.shields.io/badge/format-investigation-6f42c1) ![Tier 3](https://img.shields.io/badge/tier-3-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `AI-T3-005` |
| **Title** | The Audit That Finds the Flaw: Validating a RAG Evaluation Harness with Planted Faults |
| **Subtrack** | AI Engineering |
| **Tier** | 3: Advanced Engineering, Research and System Design |
| **Unit** | [AI-05: Retrieval-Augmented Generation and Knowledge Systems](../README.md) |
| **Format** | investigation (secondary: comparative) |
| **Difficulty** | Technical 4 · Mathematical 3 · Research 5 · Engineering 4 · Ambiguity 5 · Resources 1 (each out of 5) |
| **Estimated time** | 24-34 hours over 3 weeks |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM, CPU only. No GPU, no paid API, no network, no model download. Everything graded runs against a deterministic mock and a small generated corpus; the full test run takes under a minute |
| **Recommended prerequisites** | Resampling statistics, experience with a RAG pipeline (AI-T1-010 and AI-T2-008 are good preparation), comfort reading a small simulator. No model background beyond that |
| **Skills developed** | Evaluation design for RAG; metric attribution through conditioning; bootstrap uncertainty; fault-injection validity studies; power and false-alarm analysis; writing a validity argument |
| **Technologies** | Python 3.10+, pytest (standard library only in your package) |

---

## B. Problem Statement

Tenant Rights Desk (fictional) is a legal-aid charity in Lagos. Its assistant answers tenancy questions from sixteen short provisions: notice periods, deposits, repair deadlines, commission caps and so on. A funder will release money for a wider roll-out if the charity can show the assistant is "accurate and well-sourced". Three vendors have each sent a system, and the charity has one afternoon of volunteer lawyers to build a test set of about 60 questions: 40 the provisions answer and 20 they do not.

The obvious evaluation is to count how many answers contain the right number. That number is nearly useless on its own, for reasons you will have to find:

- A system can score 95 percent **while its retrieval is broken**, because it answers from memorised numbers and cites nothing. It is right today and wrong when the law changes.
- A system can abstain too much for two quite different reasons: it **could not find** the provision (a retrieval problem) or it **found it and refused** (a generation problem). The same abstention rate hides different repairs.
- A system can be wrong because it **contradicted** the provision it retrieved, or because it **trusted the first chunk** and ignored the right one lower in the list. Both are wrong answers; only one is fixed by re-ranking.
- A system can cite sources that were never retrieved, so the citation looks professional and means nothing.
- With 60 questions and background noise, an unlucky clean system will look broken, and a weakly broken one will look fine.

Your task is research-grade: **build an evaluation harness, then show it is valid.** `ragaudit` computes retrieval, answer, citation and abstention metrics, quantifies uncertainty with a bootstrap, and `audit` diagnoses which of seven named flaws a black-box system has. The validity study is the heart of the work: `resources/legalaid.py` provides a zoo of systems with **planted** flaws of adjustable strength and a background noise rate. You must show, with experiments, that your audit flags the planted flaw and nothing else, does not raise false alarms on clean systems, and has known power at realistic sample sizes.

The brief fixes the metric interfaces so that they can be tested exactly. It does **not** tell you which populations each flaw indicator should be measured on, what counts as evidence of a flaw, how to set tolerances, how to treat small denominators, or how large the evaluation set must be. The dependencies are the point: a flaw indicator measured on the wrong population will fire for the wrong system.

> **Why this matters beyond this task.** Most RAG evaluations are never themselves tested. A harness that has not been shown to catch a known fault gives false comfort, and in legal and health settings that comfort is the harm.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. **Design** metrics whose conditioning populations separate retrieval failures from generation failures.
2. **Quantify** uncertainty with a deterministic bootstrap and use it to decide when a flaw is evidenced.
3. **Diagnose** a black-box system by flaw type, including two simultaneous flaws.
4. **Validate** the harness with planted-fault experiments: detection rate by strength and set size, and false-alarm rate on clean systems with noise.
5. **Argue** the limits of a synthetic validity study and what a real deployment would still need.

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

Implement `ragaudit` in [`starter/ragaudit/`](starter/ragaudit/). A result is `{"answer", "cited", "retrieved", "abstained"}` and an item is `{"id", "q", "answerable", "gold_doc", "gold"}`; both are documented in `resources/legalaid.py`. Stubs raise `NotImplementedError("R<n>: ...")`. Numbers in answers are the digit runs found by `\d+`.

| ID | Requirement |
|---|---|
| **R1** | `retrieval_metrics(results, items, k=5) -> {"recall_at_k", "mrr"}` over answerable items; a hit is the gold document within the first `k` retrieved; reciprocal rank uses its position within the top `k`. No answerable items gives zeros. |
| **R2** | `answer_metrics(results, items, kb) -> {"accuracy", "faithful_rate", "citation_valid_rate", "uncited_rate"}`. *accuracy*: over answerable items, the share answered with the gold number among the answer's numbers. *faithful_rate*: over **answered** results, the share whose every number appears in the text of some retrieved document (1.0 if none answered). *citation_valid_rate*: over answered results that cite something, the share whose citations are all retrieved (1.0 if none). *uncited_rate*: over answered results, the share citing nothing (0.0 if none answered). |
| **R3** | `abstention_metrics(results, items) -> {"over_abstain_rate", "under_abstain_rate", "answered_on_miss_rate"}`. *over_abstain_rate*: among answerable items whose gold was retrieved, the share abstained. *under_abstain_rate*: among unanswerable items, the share answered. *answered_on_miss_rate*: among answerable items whose gold was not retrieved, the share answered. Empty populations give 0.0. |
| **R4** | `bootstrap_ci(values, n_boot=1000, seed=0, alpha=0.05) -> (lo, hi)`: `rng = random.Random(seed)`; each replicate is the mean of `rng.choices(values, k=len(values))`; sort the replicates; return the elements at indices `int(alpha/2*n_boot)` and `int((1-alpha/2)*n_boot) - 1`. `ValueError` on empty input. |
| **R5** | `paired_compare(a, b, n_boot=1000, seed=0) -> {"diff", "ci", "significant"}` on per-item differences `a - b` using R4; significant when the interval excludes zero. |
| **R6** | `audit(system, kb, items, seed=0) -> {"metrics", "flags", ...}`: call `system(item["q"])` for each item, compute R1 to R3 into `metrics` (keys as above), and return `flags`, a sorted list drawn from the seven names in `FLAWS`. Which populations, tolerances, minimum sample sizes and intervals you use are yours to design and defend. |

The seven flaws are: `retrieval_miss` (gold document not retrieved), `unfaithful` (answer contradicts the retrieved gold document), `parametric_leak` (answers correctly from memory when retrieval missed), `citation_forgery` (cites documents that were not retrieved), `position_bias` (ignores a gold document that is not ranked first), `over_abstain` (refuses although gold was retrieved) and `under_abstain` (answers an unanswerable question). A leaking system is only observable when retrieval misses, so the zoo's leaking systems also miss retrieval: the correct diagnosis is the pair `["parametric_leak", "retrieval_miss"]`.

**Validity study (mandatory, in `experiments.py` and the report).** At minimum: (a) the confusion table of planted flaw against flags at strength 0.4 over at least 10 seeds; (b) detection rate of each flaw as strength varies from 0.1 to 0.5; (c) the false-alarm rate of clean systems at noise 0.03 and 0.06; (d) the effect of evaluation-set size (30, 60, 120 answerable items) on both; (e) at least one case where plain accuracy would have missed a flaw your audit found. You choose the additional experiments that best test your own design.

### D.2 Engineering requirements (mandatory)

- Deterministic: no wall-clock time, no global random state, no network. Every resample takes an explicit seed.
- At least **12 tests of your own** in `tests/test_member_*.py`, including exact tiny-case checks for each metric, a case where two flaws interact, and a clean-system false-alarm test.
- Treat `system` as an opaque callable: do not read attributes of the zoo objects, import underscore-prefixed names, or inspect `make_system` to infer which flaw is planted.
- `REPORT.md` (from the [template](submission-template/REPORT.md)) carries every number you cite, reproducible with one documented command.

### D.3 Responsibility

A legal-aid assistant advises people who often cannot check the answer. In the report, write one paragraph on what a roll-out decision should require beyond this audit (human review of unanswerable and abstained questions, logging without storing tenants' identities under the Nigeria Data Protection Act 2023, a complaints route), and say who is accountable if a funder relies on an audit that missed a flaw. State plainly what a clean audit does and does not license.

### D.4 Optional enhancements

- Replace per-flaw tolerances with a sequential rule that stops early and compare its error rates to the fixed-sample rule.
- Add a flaw to the zoo yourself (for example, stale provisions) and extend the audit to detect it without breaking the other seven.
- Report an effect-size-based flag (rate above tolerance by a margin) alongside the interval-based one and compare power.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Knowledge base** | [`resources/legalaid.py`](resources/legalaid.py): `make_kb(seed)` returns 16 fictional tenancy provisions with one number each |
| **Items** | `make_items(seed, n_answerable=40, n_unanswerable=20)`; 20 unanswerable templates are available |
| **System zoo** | `make_system(flaws, seed, strength, noise, k, n_answerable, n_unanswerable)` returns a deterministic black-box system; `FLAWS` lists the seven flaws; `noise` is a background probability at which every flaw fires even when not planted |
| **Provenance** | **Synthetic** provisions and numbers; Lagos neighbourhood names are used only as labels; no real statute, tenant or case |
| **Licence** | CC BY 4.0 (content), MIT (code) |
| **Size** | Nothing committed beyond a 10 KB module |
| **Model access** | None. No network, key, GPU or download |

Hidden tests use new seeds and strengths, larger evaluation sets, flaw pairs, higher noise, and systems wrapped in plain functions so that attributes are unavailable. They also check R4 against an independent implementation of the stated algorithm.

**Setup**

```bash
cd assessments/ai-engineering/tier-3/units/AI-05-rag-and-knowledge-systems/AI-T3-005-the-audit-that-finds-the-flaw
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
| 1 | `ragaudit/` package | R1 to R6 |
| 2 | `tests/test_member_*.py` (at least 12 tests) | Exact metric checks and adversarial audit cases |
| 3 | `experiments.py` | Reproduces the validity study (a) to (e) with one command |
| 4 | `REPORT.md`, at most 2,200 words plus tables and figures, from the [template](submission-template/REPORT.md) | Research report with a validity argument; carries the AI-use declaration |
| 5 | A 10-minute technical defence (live) | Verifies understanding (see §K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion below holds. Criteria marked (T) are checked by the public and hidden test suites; the rest are checked by hand.

1. (T) `pytest` passes the provided tests and your own from a clean environment.
2. (T) R1 to R5 return the exact values in the public tests and in an independent oracle for R4.
3. (T) At strength 0.45 and noise 0.03, `audit` returns exactly the planted flaw (or the leak pair) on three unseen seeds for each of the seven flaws, and exactly the planted pair for three unseen flaw pairs. *Justification:* the reference does this on every tested seed; the margin reflects binomial noise at about 20 to 40 relevant items.
4. (T) At noise 0.04 the audit returns no flags on 15 unseen clean systems. *Justification:* the reference has zero false alarms; background noise at this level produces on average one or two incidental events per indicator.
5. (T) With 80 answerable items, a planted `unfaithful` flaw at strength 0.25 is exactly diagnosed on at least 7 of 8 unseen seeds.
6. The report's validity study covers items (a) to (e), states how tolerances were chosen without using the hidden-style seeds, and shows at least one case where accuracy alone misses a flaw the audit finds.
7. The report states what the study cannot show: at least three differences between the planted-fault zoo and real RAG systems, and how each could invalidate the conclusion.

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

1. **Create your own private repository** named `clbg-AI-T3-005-<your-github-username>`, copying this assessment's `starter/`, `tests/`, `resources/` and `submission-template/` folders.
2. **Expected structure:** `ragaudit/` (your package), `tests/` (provided tests plus your `test_member_*.py`), `resources/` (unchanged), `requirements.txt`, `REPORT.md` (from the template, which includes the AI-use declaration).
3. **Commit as you work.** Your commit history is part of the evidence (see §K).
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing a submission issue using the **Assessment submission** template, with the repository URL and the exact commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines). General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

Optional. They are recognised in feedback but never stand in for the core requirements.

1. **Sequential audit.** Stop evaluating as soon as the evidence is sufficient and measure the expected number of questions saved.
2. **Mutation score.** Define a mutation score for evaluators (share of planted faults caught) and compare three designs by it.
3. **Real systems.** Apply the harness to a RAG pipeline you built earlier, treating its flags as hypotheses to confirm by inspection (optional; never graded).

---

## K. Assessment Integrity

**AI tools are permitted** to help you learn, for example to explain a concept or review your code. **They are not permitted to do the assessment for you.** You must be able to explain and change every line you submit.

- **Disclose** all AI assistance in the declaration section of `REPORT.md` (tool, purpose, example prompt). Undisclosed use that becomes apparent at defence is an integrity breach; disclosed, reasonable use is not penalised.
- **Cite** any code adapted from documentation or other sources.
- **Collaboration:** you may discuss general techniques with other members. You may not share code, numbers or report text.
- **How your understanding is verified.** In a short defence the assessor will (1) ask why `over_abstain_rate` is conditioned on the gold document having been retrieved, and what would be diagnosed wrongly otherwise; (2) ask what your audit reports for a system with `position_bias` strength 1.0 and retrieval that always ranks gold first; (3) give an unseen change, such as halving the evaluation set, and ask which flags lose power first and how you would know.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

*This section explains the design of the assessment for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | Bootstrap intervals, conditional rates, and a working picture of a RAG pipeline. |
| **New skill developed** | Validating an evaluator, not only using one: planted faults, detection power and false-alarm control. |
| **Decisions the member must make** | Populations for each indicator, tolerances, minimum denominators, interval method, experiment design and set sizes. |
| **What must be investigated independently** | Why accuracy hides a leak, why abstention needs conditioning, how interacting flaws change the apparent rates, and where power runs out. |
| **Why it is interesting** | The central question is meta: how do you know your test of an AI system can fail? |
| **Evidence of competence** | Exact diagnoses on unseen seeds and pairs, a clean-system false-alarm table, and a validity argument that names its own threats. |
| **Misconceptions exposed** | 'High accuracy means a safe system.' 'Abstention rate is one number.' 'A metric that moves is a metric that means something.' |
| **Preparation for later work** | Leads into AI-09 safety evaluation and AI-12 research methods, and underpins any evaluation of agents (AI-T3-007). |

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
