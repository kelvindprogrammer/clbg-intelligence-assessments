# DS-T3-018: One Number, Many Clinics

> *Forecasts for twelve clinics, three zones and the whole network that disagree with each other are not a plan. Make them agree, then ask whether agreeing made them better.*

![Format: comparative](https://img.shields.io/badge/format-comparative-6f42c1) ![Tier 3](https://img.shields.io/badge/tier-3-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `DS-T3-018` |
| **Title** | One Number, Many Clinics: Reconciling Hierarchical Forecasts Across a Health Network |
| **Subtrack** | Data Science |
| **Tier** | 3: Advanced Practice and Research-Informed Judgement |
| **Unit** | [DS-10: Time-Series Analysis and Forecasting](../README.md) |
| **Format** | Comparative (secondary: Investigation) |
| **Difficulty** | Technical 4 · Mathematical 4 · Research 4 · Engineering 3 · Ambiguity 4 · Resources 1 (each out of 5) |
| **Estimated time** | 22–34 hours over 3 weeks |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM. No GPU, no paid services, and no internet after setup |
| **Recommended prerequisites** | DS-T2-020 or equivalent (rolling-origin evaluation, forecast error metrics); linear algebra (matrix inverse, projection, least squares); covariance estimation; comfort reading a methods paper. |
| **Skills developed** | Forecast reconciliation (bottom-up, top-down, OLS, WLS, MinT-shrinkage); summing matrices; coherence and unbiasedness; rolling-origin evaluation by hierarchy level; changepoint reasoning; validity arguments about small effects |
| **Technologies** | Python 3.10+, pandas, NumPy, pytest. No forecasting library is required or allowed to do the reconciliation for you. |

---

## B. Problem Statement

A state health ministry plans antenatal-care staffing and commodities at three levels: **each clinic** orders supplies and rosters midwives, **each zone** manages distribution, and the **ministry** sets the state budget. Today every level produces its own weekly forecast of antenatal visits. They never add up: the twelve clinic forecasts sum to one figure, the three zone forecasts to another, and the ministry's number is a third. Each level blames the others, and the budget is argued over rather than planned.

You have `clinic_weekly.csv`: five years (260 weeks) of **synthetic** weekly visit counts for 12 clinics in three zones (North, Central, South). The series have trend, an annual cycle that differs by zone, overdispersed count noise, and **shared zone-level shocks**, such as outbreaks or supply disruptions, that hit every clinic in a zone at once. Somewhere in the history something else may have happened too: a clinic may have **closed or lost its catchment area** and sent some of its patients to a neighbouring clinic in the same zone. Nobody tells you whether, where or when.

Forecast reconciliation fixes the disagreement mathematically: take the incoherent base forecasts and project them onto the set of forecasts that add up. Several ways exist (bottom-up, top-down, and the optimal-combination family of Hyndman et al. 2011 and Wickramasuriya, Athanasopoulos and Hyndman 2019), and each embodies a different assumption about where the information is. The literature reports that reconciliation often helps, but how much depends on the data, and effects can be small relative to noise.

Your assignment is both an implementation and a research question:

1. Build the hierarchy and **implement five reconcilers from first principles**, with the exact definitions given in §D.
2. Evaluate them by hierarchy level with a leak-free rolling-origin design against the unreconciled base.
3. Build a **detector** for patient transfers between sibling clinics, decide what it can and cannot see, and explain what a transfer does to each reconciler. In particular, why top-down is fragile.
4. Write a short methods-and-validity report that states what the evidence supports. In this data, the honest answer to "does reconciliation improve accuracy?" is more subtle than yes or no, and you are assessed on reaching a defensible position, not on claiming a win.

At Tier 3 the specification gives you the mathematics and the interfaces, but the experimental design, the detector, the choice of what to recommend, and the argument about uncertainty are yours.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. Construct a summing matrix and derive coherence for a multi-level hierarchy.
2. Implement bottom-up, top-down, OLS, structural-WLS and shrinkage-MinT reconciliation and prove (by test) their key properties.
3. Estimate a high-dimensional forecast-error covariance with a data-driven shrinkage intensity.
4. Evaluate forecasts by hierarchy level with rolling origins and scale-free errors, without leakage.
5. Detect and characterise a structural change in compositional shares, with a stated false-alarm rate.
6. Quantify uncertainty in a comparison of methods and state a conclusion proportionate to it.

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

Interfaces and definitions are exact; the experimental design and the detector are yours. Implement the `hierfc` package in [`starter/hierfc/`](starter/hierfc/). The function signatures are fixed because the automated tests import them. The internals are yours.

| ID | Requirement |
|---|---|
| **R1** | `build_hierarchy(df) -> Hierarchy`: names `['TOTAL', zones..., clinics...]` (zones sorted; clinics sorted by zone then id), the summing matrix `S` (16 × 12 here: a row of ones, one row per zone, then the identity), and `Y` of shape `(T, 16)` with `Y == Y[:, 4:] @ S.T`. |
| **R2** | `reconcile(base_fc, S, method, resid=None, Y=None, prop_window=None)`: implement `bottom_up`, `top_down` (average historical shares of the total, optionally over the last `prop_window` rows), `ols`, `wls_struct` (`W = diag(S·1)`) and `mint_shrink` (Schäfer–Strimmer shrinkage covariance of the residuals; the exact formula is in the starter docstring). Output is coherent, shape `(h, n_all)`. Unknown method: `ValueError`. Coherent input must be returned unchanged by `ols`, `wls_struct` and `mint_shrink`. |
| **R3** | `run_evaluation(df, h=8, initial=156, step=13, prop_window=None)`: rolling origins; base forecasts from `Y[:k]` only (use the provided `base_forecasts`); RMSSE per node against the in-sample one-step naive scale of `Y[:k]`; averaged over origins and then over the nodes of each level; returns `[method, level, rmsse]` for `base` plus all five methods at levels `total`, `zone`, `clinic`, `all`. |
| **R4** | `detect_transfers(df) -> list[dict]`: find clinics whose share of their zone total changes level persistently. Each dict has `clinic_id`, `week_index` (the first week of the new level) and `direction` (`up` or `down`). Return `[]` when nothing credible exists. The method is yours. |

### D.2 Engineering requirements (mandatory)

- **No leakage.** Base forecasts, residuals, top-down shares and the MinT covariance at origin `k` use `Y[:k]` only.
- **Numerical care.** Solve linear systems rather than forming explicit inverses where you can, and say what you do if the covariance is singular.
- **Determinism and time.** The full evaluation must finish in under 2 minutes.
- **Tests.** Keep the provided tests passing and add **at least 12 tests of your own** in `tests/test_member_*.py`, including edge cases you found yourself.
- **Dependencies.** Use only the packages in [`starter/requirements.txt`](starter/requirements.txt). If you add one, justify it in your report.

### D.3 Privacy and responsibility

The data is **synthetic**; no clinic, patient or ministry is described. Real antenatal-visit counts at small clinics can identify individuals when counts are low and are health data, a special category under the Nigeria Data Protection Act 2023. In your report, add a short note on minimum cell sizes, aggregation before sharing and who should see clinic-level forecasts.

### D.4 Optional enhancements (not required for full marks)

- Compare a second base forecaster (for example seasonal-naive) and show whether reconciliation gains depend on base quality.
- A forecast-error covariance estimated with a different shrinkage target, with evidence on whether it matters.
- Non-negative reconciliation: counts cannot be negative. Implement a simple fix and discuss its bias.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Dataset** | [`resources/data/clinic_weekly.csv`](resources/data/clinic_weekly.csv): 12 clinics × 260 weeks = 3,120 rows × 4 columns (`zone`, `clinic_id`, `week`, `visits`), about 88 KB, UTF-8 |
| **Provenance** | **Synthetic**, generated by CLBG with a fixed seed: zone-specific annual cycles, growth, AR(1) zone shocks shared by all clinics in the zone, and negative-binomial count noise. Whether a transfer event is present is for you to find out. |
| **Licence** | CC BY 4.0, free to reuse with attribution |
| **Integrity** | The contract test checks the SHA-256, so do not edit the file |

**Key references (read before you design the study).** Hyndman, Ahmed, Athanasopoulos and Shang (2011), *Optimal combination forecasts for hierarchical time series*, Computational Statistics & Data Analysis. Wickramasuriya, Athanasopoulos and Hyndman (2019), *Optimal forecast reconciliation for hierarchical and grouped time series through trace minimization*, Journal of the American Statistical Association. Hyndman and Athanasopoulos, *Forecasting: Principles and Practice* (3rd ed., online), chapter on forecast reconciliation. Cite what you use.

**Known limitations (by design).** One simulated process, 12 clinics and 8 backtest origins cannot settle the general question. The hidden tests regenerate the hierarchy with different seeds, with and without a transfer event.

**Setup**

```bash
cd assessments/data-science/tier-3/units/DS-10-time-series-and-forecasting/DS-T3-018-one-number-many-clinics
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract        # should pass immediately: checks data and scaffold
pytest                    # most tests fail until you implement the package
```

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `hierfc/` package (the completed starter) | The core technical evidence |
| 2 | `tests/test_member_*.py` | Shows you can pin behaviour down and think about edge cases |
| 3 | `outputs/evaluation.csv` and a figure of RMSSE by method and level | The central results, regenerated by your script |
| 4 | `analysis.py` or `analysis.ipynb` | Runs the evaluation, the ablations and the uncertainty analysis |
| 5 | Ablation tables (at least: base vs each method; all-history vs windowed top-down; with vs without the detected transfer handled) | Shows which design choice drives which result |
| 6 | `REPORT.md` (from the [template](submission-template/REPORT.md)), with the AI-use declaration inside | Communicates decisions and limits; integrity declaration (see §K) |
| 7 | A 5-minute technical defence (live) | Verifies understanding (see §K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion below holds. Criteria marked ⚙ are checked by the public and hidden test suites, the rest by hand.

1. ⚙ Provided and member tests pass from a clean environment; the evaluation runs in under 2 minutes.
2. ⚙ All five reconcilers return coherent forecasts; `ols`, `wls_struct` and `mint_shrink` leave coherent input unchanged; `mint_shrink` matches the specified shrinkage formula.
3. ⚙ **Not materially worse:** on hidden hierarchies, the overall RMSSE of `ols`, `wls_struct` and `mint_shrink` is **≤ 1.03 × base**. *Justification:* the reference stays within about ±1% of base on all tested seeds; 3% allows implementation variation without permitting a broken projection.
4. ⚙ Top-down with all-history shares is worse than bottom-up at clinic level on hidden data, and `prop_window` changes it.
5. ⚙ **Transfer detection:** on hidden hierarchies with a transfer event, the source clinic is flagged `down` with `week_index` within **±8 weeks** of the true week and no clinic outside the transfer pair is flagged; with no event, the result is `[]`. *Justification:* the source clinic's share falls by 30–50% relative, which is far above noise; ±8 weeks allows for the gradual evidence a changepoint test needs.
6. ✍ The report states clearly whether reconciliation improved accuracy, by how much, with a measure of uncertainty (for example paired per-origin differences with an interval), and does not overclaim.
7. ✍ The report explains, with the transfer evidence, why top-down fails and what a defensible operational recommendation would be.
8. ✍ Limits are stated: one process, few origins, synthetic data, what would be needed to generalise.

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

1. **Create your own private repository** named `clbg-DS-T3-018-<your-github-username>` and copy this assessment's `starter/`, `tests/`, `resources/` and `submission-template/` into it. Your package sits at the repository top level.
2. Commit as you work. Your commit history is part of the evidence (see §K); a single "final" commit will be questioned at defence.
3. Add your outputs and `REPORT.md`, then run `pytest` from a clean environment built from your `requirements.txt`.
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing a submission issue in the CLBG assessments repository, using the **Assessment submission** template. Include the repository URL and the exact commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see the [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines-extensions-and-late-work). General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

Optional. They are recognised in feedback and can strengthen a placement case, but never stand in for the core requirements.

1. **Break-aware evaluation.** Re-estimate shares or residuals only after the detected transfer and show the effect on each reconciler.
2. **Bootstrap the comparison.** A block bootstrap over origins for the difference between `mint_shrink` and `bottom_up`.
3. **Temporal hierarchy.** Add a monthly aggregation of each clinic and reconcile across time as well as across clinics.

---

## K. Assessment Integrity

**AI tools are permitted** to help you learn, for example to explain a concept, suggest an idiom or review your code. **They are not permitted to do the assessment for you.** You must be able to explain and change every line you submit.

- **Disclose** all AI assistance in the declaration section of `REPORT.md`: which tool, what for, an example prompt, and how you verified the output. Undisclosed use that becomes apparent at defence is an integrity breach. Disclosed, reasonable use is not penalised.
- **Cite** any code adapted from documentation or other sources, with a link.
- **Collaboration:** you may discuss *general techniques* with other members. You may not share code, numbers, thresholds or report text.
- **How your understanding is verified.** In the 5-minute defence the assessor will: 
  1. asks you to derive, on a three-node example, why OLS reconciliation leaves coherent forecasts unchanged;
  2. asks how the transfer event changes each reconciler's behaviour and why bottom-up is least exposed;
  3. gives you an unseen modification, for example a fourth zone, a different shrinkage target or a negativity constraint, and asks you to adapt the code and tests live.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

*This section explains the design of the assessment for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | Matrix algebra, least squares, covariance, rolling-origin evaluation (DS-T2-020). |
| **New skill developed** | Turning a research method into code from its mathematics, testing its properties, and then judging whether its benefit is real. |
| **Decisions the member must make** | How to detect a structural change and with what false-alarm rate; which reconciler to recommend; how to quantify uncertainty about a small effect; how to handle the transfer in the evaluation. |
| **What must be investigated independently** | Whether and when a transfer happened, what it does to each method, and whether differences between methods exceed noise. |
| **Why it's interesting** | Health systems really do plan at several levels at once. The data is built so that the textbook story (reconciliation helps) is only partly true, and top-down visibly fails. |
| **Evidence of competence** | Property tests on the algebra, a formula check on the shrinkage covariance, hidden-seed robustness and detection, and a report whose conclusion is proportionate to its evidence. |
| **Misconceptions exposed** | Coherent means accurate. Top-down is safe because the total is easy to forecast. A lower average RMSSE is a real improvement. |
| **Preparation for later work** | Leads to temporal and cross-temporal hierarchies, probabilistic reconciliation, and any ML forecasting system that must aggregate consistently. |

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
