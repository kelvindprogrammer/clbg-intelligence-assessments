# DS-T1-011: The Confident Notebook

> *A polished analytics notebook makes ten confident recommendations to a mobile-money company's leadership. Some are right. Most are wrong, each for a different reason. Audit it before the offsite.*

![Format: Debugging & Forensics](https://img.shields.io/badge/format-debugging%20%26%20forensics-6f42c1) ![Tier 1](https://img.shields.io/badge/tier-1-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `DS-T1-011` |
| **Title** | The Confident Notebook: Auditing the Claims of an Exploratory Analysis |
| **Subtrack** | Data Science |
| **Tier** | 1: Foundation and Technical Fluency |
| **Unit** | [DS-04: Exploratory Data Analysis](../README.md) |
| **Format** | Debugging & Forensics (secondary: Investigation) |
| **Difficulty** | Technical 2 · Mathematical 2 · Research 1 · Engineering 2 · Ambiguity 3 · Resources 1 (each out of 5) |
| **Estimated time** | 10–16 hours over 1–2 weeks |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM. No GPU, no paid services, no internet after setup |
| **Recommended prerequisites** | pandas `merge` and `groupby`; medians and means; conditional probability at the level of "P(A given B)"; what a p-value is; running `pytest` |
| **Skills developed** | Critical reading of analyses; recognising survivorship bias, base-rate neglect, log-scale misreading, confounding, the ecological fallacy, regression to the mean, percentage-point confusion and multiple comparisons; re-analysing data to quantify each error; writing a constructive audit |
| **Technologies** | Python 3.10+, pandas, numpy, scipy, matplotlib, pytest |

---

## B. Problem Statement

**KoboLink** is a fictional mobile-money operator with 2,000 agents (the shops and kiosks where customers cash in and cash out) across 12 Nigerian states. Its Growth Analytics team has written an exploratory notebook, [`resources/flawed_notebook/agent_insights.py`](resources/flawed_notebook/agent_insights.py), for next month's strategy offsite. It makes ten claims, listed with the numbers it printed in [`resources/CLAIMS.md`](resources/CLAIMS.md), and attaches a recommendation to most of them: *suspend every flagged agent automatically*, *train every agent*, *tighten KYC for rural agents*, *coach the bottom quartile every quarter*, *send a retention team to one area*.

Each recommendation costs money or affects livelihoods. Suspending an agent on a false fraud flag cuts off a small business and leaves its customers without cash-out access. Imposing stricter KYC on rural agents because of a statistical artefact is unfair and slows financial inclusion where it is weakest.

The notebook *looks* careful. Its code runs, its numbers are computed correctly from the data it uses, and its charts are tidy. Its problems are in **reasoning**: what was compared with what, what was left out, and what a number can and cannot mean. This is the most common way real analyses go wrong, and it is invisible to anyone who checks only the code.

The Chief Operating Officer has asked you, as an independent analyst, to audit the notebook before the offsite:

> *For each claim: is it supported by the data? If not, what exactly is wrong with it, and what does a correct analysis show?*

**What makes it hard.**

- The flaws are all different. Some come from how the data was filtered, some from how a chart was read, some from comparing the wrong groups, some from what was tested and not reported.
- **Not every claim is wrong.** Declaring everything "unsupported" is not an audit. You must decide, with evidence, which claims stand.
- A claim can be wrong even when its number is computed correctly. You must explain *why the number does not support the conclusion*, then compute the number that would.

**Known facts from KoboLink** (your only documentation):

- `agents.csv` is a full export of every agent ever onboarded, including churned agents. The CRM's "current agents" view, which the notebook partly used, lists only active agents.
- `fraud_confirmed` is the outcome of a full investigation of every agent-month, so it is the ground truth for fraud. `fraud_flagged` is the automatic rules engine's output. The rules engine was changed in July 2025.
- Training (`trained`) was an induction course offered when agents joined. It was offered on request, and urban agents requested it far more often.
- In April 2025, 60 agents chosen **at random** from the 120 agents with the lowest Q1-2025 activity received a coaching call (`coached_q2`).
- The data is **synthetic**. No real operator, agent or customer is described.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. **Read an analysis critically**, separating code that runs correctly from reasoning that holds.
2. **Name the specific flaw** behind a wrong conclusion, using standard vocabulary, and explain the mechanism in plain language.
3. **Re-analyse the data** to compute the quantity a correct analysis would report, exactly as defined.
4. **Recognise correct claims** and say why they survive scrutiny.
5. **Write an audit** that a non-technical executive can act on, replacing each bad recommendation with a defensible one or with "we don't know yet".

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

Implement the `notebook_audit` package in [`starter/notebook_audit/`](starter/notebook_audit/). The loaders, the vocabulary (`FLAWS`, `VERDICTS`, `CLAIM_IDS`) and `validate_audit` are provided. Every corrected-value function takes `(agents, act)` from `load_all` and returns one `float`, computed **exactly** as defined under "Corrected quantity" in [`resources/CLAIMS.md`](resources/CLAIMS.md).

| ID | Requirement |
|---|---|
| **R1** | `c1_cohort_ratio`: the corrected quantity for C1. |
| **R2** | `c2_ppv`: the corrected quantity for C2. |
| **R3** | `c3_value_ratio`: the corrected quantity for C3. |
| **R4** | `c4_stratified_training_ratio`: the corrected quantity for C4. |
| **R5** | `c5_mh_rate_ratio`: the corrected quantity for C5. |
| **R6** | `c6_coaching_difference`: the corrected quantity for C6. |
| **R7** | `c7_float_ratio`: the corrected quantity for C7. |
| **R8** | `c8_relative_flag_rate_change`: the corrected quantity for C8. |
| **R9** | `c9_december_ratio`: the corrected quantity for C9. |
| **R10** | `state_churn_pvalues` (one p-value per `state/lga_type` group, indexed `"<state>/<lga_type>"` and sorted) and `c10_bonferroni_min_p`: the corrected quantity for C10. |
| **R11** | `outputs/audit.json`: a list of ten objects, one per claim, each with `claim_id`, `verdict` (`"supported"` or `"unsupported"`), `flaw` (one label from `FLAWS`; `"none"` exactly when the verdict is `"supported"`), `corrected_value` (your function's output on the official data) and `evidence` (at least one sentence, 15 or more words, stating the mechanism). It must pass `validate_audit`. |
| **R12** | `run_audit.py` or `run_audit.ipynb` (your analysis script at the repository root) that regenerates `outputs/audit.json`'s numbers and every figure in your report, including a corrected version of the C3 chart and at least one figure that *shows* the mechanism behind another flaw (for example the survival of each cohort over time, or the uncoached group's Q1-to-Q2 change). |
| **R13** | `AUDIT_REPORT.md` (at most 1,500 words plus tables and figures), using the [template](submission-template/AUDIT_REPORT.md), written for the COO. For every claim it gives the verdict, the flaw, the corrected number and a **replacement recommendation**. |

### D.2 Engineering requirements (mandatory)

- **No mutation** of the DataFrames passed in.
- **Do not edit** the flawed notebook or the data (checksums are tested). Your work lives in your own files.
- **Tests.** Keep the provided tests passing and add **at least 8 tests of your own** in `tests/test_member_*.py`, each on a small hand-built table where you can compute the answer on paper. At least one must show a case where the notebook's method and the corrected method **disagree**.
- **Dependencies.** Only those in [`starter/requirements.txt`](starter/requirements.txt).

### D.3 Privacy and responsibility

The data is synthetic, but agent-level financial and fraud data is sensitive personal and commercial data under the Nigeria Data Protection Act 2023, and a fraud label can damage a person's livelihood.

- Report aggregates only. Never list individual agent IDs as fraudsters or poor performers in your report.
- In one paragraph, explain what safeguards should apply before any agent is suspended on the basis of an automated flag (human review, notice, appeal), in the light of your C2 finding.

### D.4 Optional enhancements (not required for full marks)

- Bootstrap intervals for the corrected values of C1, C4 and C6.
- A false discovery rate (Benjamini–Hochberg) version of C10, compared with Bonferroni.
- An estimate of the extra investigator workload implied by C8, in agent-months per month.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Data** | [`resources/data/agents.csv`](resources/data/agents.csv) (2,000 rows) and [`resources/data/monthly_activity.csv`](resources/data/monthly_activity.csv) (26,753 agent-months, 2023-01 to 2025-12), about 1.1 MB in total |
| **Artefact under audit** | [`resources/flawed_notebook/agent_insights.py`](resources/flawed_notebook/agent_insights.py) (percent-format notebook: runs as a script, opens in Jupyter or VS Code) and its chart `c3_value_by_state.png` |
| **Claims and definitions** | [`resources/CLAIMS.md`](resources/CLAIMS.md) |
| **Provenance** | **Synthetic**, generated by CLBG with a fixed seed. KoboLink and its agents are fictional. The generator is in the assessor kit because it encodes the answers. |
| **Licence** | CC BY 4.0 |
| **Integrity** | SHA-256 checksums in `tests/test_contract.py` |

**Schema.** `agents.csv`: `agent_id, state, lga_type (urban/rural), onboard_month (YYYY-MM), status (active/churned), churn_month (first month with no activity; blank if active), trained (0/1), q1_bottom_120 (0/1), coached_q2 (0/1)`. `monthly_activity.csv`: `agent_id, month, txn_count, txn_value_ngn, float_balance_avg_ngn, fraud_flagged (0/1), fraud_confirmed (0/1)`, one row per agent per month in which the agent was active.

**Setup**

```bash
cd assessments/data-science/tier-1/units/DS-04-exploratory-data-analysis/DS-T1-011-the-confident-notebook
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract                                  # passes immediately
python resources/flawed_notebook/agent_insights.py  # reproduces the notebook's numbers
pytest                                              # most tests fail until you implement the package
```

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `notebook_audit/` package | The corrected analyses, one function per claim |
| 2 | `tests/test_member_*.py` (≥ 8) | Hand-worked cases, including one where the notebook's method and yours disagree |
| 3 | `run_audit.py` or `run_audit.ipynb` | Regenerates all numbers and figures |
| 4 | `outputs/audit.json` | Machine-readable verdicts, flaw labels and corrected values, graded against the key |
| 5 | `AUDIT_REPORT.md` | The audit for the COO, with replacement recommendations |
| 6 | `AI_USE_AND_SOURCES.md` | Integrity declaration |
| 7 | 5–10 minute defence | Verifies understanding |

---

## G. Acceptance Criteria

⚙ = automated (public and hidden suites); ✍ = assessor.

1. ⚙ `pytest` passes all provided tests and your own in a clean environment.
2. ⚙ Every corrected-value function matches an independent implementation (relative tolerance 1e-6) on the official data **and** on two re-generated datasets. *Justification:* each quantity has a single exact definition in `CLAIMS.md`, so any larger difference is a different computation.
3. ⚙ `outputs/audit.json` passes `validate_audit`, and its corrected values match the official data.
4. ⚙ At least **9 of 10** verdicts and at least **8 of 10** flaw labels agree with the assessment key. *Justification:* each claim has one primary flaw that the defence can probe, and one or two labels are reasonably arguable (the key already accepts more than one label where two descriptions fit), so the margin allows one honest disagreement on the verdicts and two on the labels without rewarding guessing: a uniform answer scores at most 8 verdicts and 2 labels.
5. ✍ Every flaw is explained by its **mechanism** in the data, not just named, and at least two mechanisms are shown with a figure.
6. ✍ The two claims that are correct are identified and defended with evidence.
7. ✍ Every recommendation in the notebook is replaced with a defensible one, or explicitly with "the data cannot tell us yet; here is what would", and the C2 recommendation (automatic suspension) is addressed with the safeguards in §D.3.
8. ✍ The audit is constructive and professional: it criticises reasoning, not people.

---

## H. Evaluation Rubric

Full rubric: **[rubric.md](rubric.md)**.

| Dimension | Points |
|---|---|
| Problem understanding and technical reasoning | 15 |
| Technical correctness | 20 |
| Implementation quality | 10 |
| Forensic methodology | 15 |
| Testing and evaluation | 10 |
| Documentation and reproducibility | 10 |
| Critical thinking and limitations | 15 |
| Presentation and communication | 5 |
| **Total** | **100** |

The outcome depends on the score **and** the gates. See the [placement framework](../../../../../../docs/placement-framework.md).

---

## I. Submission Instructions

1. Create a **private** GitHub repository `clbg-DS-T1-011-<your-github-username>` and copy in `starter/`, `tests/`, `resources/` and `submission-template/`.
2. **Expected structure:**
   ```text
   clbg-DS-T1-011-<username>/
   ├── README.md                 # how to run, in 10 lines or fewer
   ├── requirements.txt
   ├── notebook_audit/
   ├── tests/                    # provided + test_member_*.py
   ├── resources/                # unchanged
   ├── run_audit.py | run_audit.ipynb
   ├── outputs/audit.json
   ├── figures/
   ├── AUDIT_REPORT.md
   └── AI_USE_AND_SOURCES.md
   ```
3. **Commit as you work**; your history is evidence.
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing an **Assessment submission** issue with the repository URL and commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see the [assessment policy](../../../../../../docs/assessment-policy.md).
6. General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

1. **Write the eleventh claim.** Find a claim the notebook *should* have made: a real pattern in the data that it missed. Support it properly.
2. **Uncertainty for every correction.** Add bootstrap intervals to C1, C4, C5 and C6. Which corrections are themselves inconclusive?
3. **A review checklist.** Turn your audit into a ten-item checklist that KoboLink's analysts could run on any future notebook, and test it on one of your own earlier analyses.
4. **FDR versus FWER.** Re-do C10 with Benjamini–Hochberg. When would KoboLink prefer each?

---

## K. Assessment Integrity

**AI tools are permitted** for learning (explaining what regression to the mean is, or how `binomtest` works), **not** to produce the audit. Pasting the notebook into an AI tool and asking "what is wrong with this?" is not permitted, and the defence is designed to expose it.

- **Disclose** all AI use in `AI_USE_AND_SOURCES.md` (tool, purpose, example prompt). Reasonable disclosed use is not penalised.
- **Cite** adapted code with links.
- **Collaboration:** general discussion of the named fallacies is fine. Sharing verdicts, numbers, code or report text is not.
- **How your understanding is verified.** In the defence the assessor will:
  1. pick two claims and ask you to explain each mechanism **without notes**, using the data;
  2. show you a **new, unseen claim** made with the same data (for example a chart or a comparison you have not seen) and ask you to judge it live;
  3. ask you to modify one corrected function live, for example C6 with a different improvement measure, and say whether your verdict changes;
  4. ask which of the notebook's recommendations would do the most harm if implemented, and why.

See [assessment integrity](../../../../../../docs/assessment-integrity.md).

---

## Pedagogical Design

| Question | Answer |
|---|---|
| **Knowledge needed** | pandas basics, conditional probability, medians, p-values. |
| **New skill developed** | Auditing an analysis: separating computation from inference, naming the flaw, and quantifying the correct answer. |
| **Decisions the member must make** | Which claims stand, what the primary flaw is, how to show each mechanism with a figure, and what to recommend instead. |
| **What must be investigated independently** | The flaw behind each claim. `CLAIMS.md` defines what to compute, never why the notebook is wrong. |
| **Why it's interesting** | Every flaw is a classic that working analysts still make, all in one realistic artefact with real consequences for small businesses. Two claims are true, so pattern-matching ("everything is wrong") fails. |
| **Evidence of competence** | Exact corrected values on re-generated data, verdicts and labels graded against a key, mechanism figures, and a live judgement of an unseen claim. |
| **Misconceptions exposed** | "The code runs, so the conclusion holds." "97% accurate means 97% of flags are right." "A taller bar on any chart means proportionally more." "Improvement after an intervention proves it worked." "A state-level correlation describes individuals." "p < 0.05 is significant however many tests you ran." |
| **Preparation for later work** | DS-08 (causal inference and experiments), DS-05 (probability and multiple testing), DS-06 (honest visualisation) and every later assessment that asks the member to defend their own claims. |

**Suggested approach** (optional): run the notebook first and reproduce each number. For every claim, write down in one sentence what was compared with what. Then ask: *what was left out, what else differs between the groups, and what would I expect to see if the claim were false?*

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
