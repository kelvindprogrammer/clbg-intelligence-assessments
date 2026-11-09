# DS-T3-003: The Garden of Forking Paths

> *Did solar mini-grids raise village businesses' revenue? It depends on how you clean the data, and that is the finding. Specify the space of defensible cleaning choices, run every path, and report how robust the conclusion really is.*

![Format: Open-ended research](https://img.shields.io/badge/format-open--ended%20research-b60205) ![Tier 3](https://img.shields.io/badge/tier-3-d73a4a) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `DS-T3-003` |
| **Title** | The Garden of Forking Paths: A Multiverse Study of Cleaning Choices |
| **Subtrack** | Data Science |
| **Tier** | 3: Advanced Engineering, Research and System Design |
| **Unit** | [DS-03: Data Cleaning and Data Quality](../README.md) |
| **Format** | Open-ended (research) (secondary: Investigation) |
| **Difficulty** | Technical 3 · Mathematical 4 · Research 4 · Engineering 3 · Ambiguity 5 · Resources 1 (each out of 5) |
| **Estimated time** | 35–60 hours over 3–5 weeks |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM. A thousand-universe run takes a few minutes on a CPU. No GPU, no paid services, and no internet after setup |
| **Recommended prerequisites** | Panel-data regression (fixed effects, difference-in-differences) and clustered standard errors; data cleaning at DS-T1/T2 level; comfort reading methods papers. [DS-T2-005](../../../../tier-2/units/DS-03-data-cleaning-and-quality/DS-T2-005-same-patient-two-registers/README.md) is good preparation for the research-design mindset. |
| **Skills developed** | Specifying an estimand before analysing; turning researcher degrees of freedom into an explicit decision space; multiverse and specification-curve analysis; attributing variation in results to decisions; separating defensible from indefensible paths; reporting fragile findings honestly |
| **Technologies** | Python 3.10+, pandas, NumPy, SciPy, PyYAML, pytest; matplotlib for figures. Optional: statsmodels or linearmodels for estimation (declare them) |

---

## B. Problem Statement

A rural electrification programme connected 30 of 60 villages in four North Central states to solar mini-grids between 2024 and 2025. An evaluation team surveyed micro-enterprises (shops, food vendors, tailors, salons, grinding mills and phone-charging kiosks) in all 60 villages three times: at baseline (early 2024), midline (early 2025) and endline (early 2026). The funder wants one sentence for its annual report: **"Mini-grid connection increased enterprise revenue by X%."**

The panel is messy in the way real field data is. Revenue was reported per week or per month, and sometimes nobody wrote down which. Some figures have an extra zero. Some interviews were entered twice. Businesses closed between rounds. Six villages were connected late, between midline and endline. Inflation ran at around 25–30% a year, and endline interviews did not happen at the same time in every village.

For each of these problems there is more than one defensible way to proceed, and the analyst usually picks one without noticing that a choice was made. Gelman and Loken called this the *garden of forking paths*. **Multiverse analysis** (Steegen, Tuerlinckx, Gelman and Vanpaemel, 2016) and the closely related **specification-curve analysis** (Simonsohn, Simmons and Nelson, 2020) make those choices explicit: you define the set of reasonable analyses, run all of them, and report the distribution of results instead of one.

**Your task is to answer the funder's question honestly.** That means:

1. Saying precisely *what* effect you are estimating (on whom, on what scale, compared with what).
2. Building a decision space of defensible cleaning and analysis choices, and arguing for each option and against the paths you exclude.
3. Running the multiverse reproducibly.
4. Analysing which decisions drive the results, and whether the funder's sentence survives.

There is no single right answer to this assessment, but there are wrong ones: a decision space stuffed with indefensible options to manufacture fragility; one so narrow it is robust by construction; or results pooled across estimates on incomparable scales.

**What you know:**

- The programme selected villages before baseline. Assignment was not randomised, but the two arms looked similar at baseline on observed characteristics. Treat the design as a difference-in-differences with the usual parallel-trends caveats.
- `cpi_index.csv` is an **illustrative synthetic monthly price index** supplied with the data, not an official statistic. Use it as if it were the relevant index.
- The questionnaire's default revenue period was "per month".
- Enumerators recorded an enterprise as `closed` when the business had ceased trading, and as `not_found` when it couldn't be located.

---

## C. Objectives

You should be able to show that you can:

1. **Frame** the research question as a precise estimand, and explain how some cleaning decisions change the estimand rather than only the estimate.
2. **Specify** a decision space of at least six decisions, with defensible options and stated exclusions, grounded in the data and the literature.
3. **Implement** a reproducible pipeline in which any universe can be rerun from the raw files.
4. **Analyse** the multiverse: a specification curve, an attribution of variation to decisions, and robustness statements that respect scale differences between outcomes.
5. **Argue validity**: which universes estimate what, which threats remain (parallel trends, selection through closure, measurement error), and what the funder may and may not say.
6. **Communicate** a fragile finding without either overselling it or dismissing it.

---

## D. Technical Requirements

### D.1 Research requirements (mandatory)

| ID | Requirement |
|---|---|
| **R1** | **Estimand and model.** State the target estimand(s) and the estimator applied in every universe. If some decisions change the estimand (for example dropping closed businesses gives an effect on survivors), say so and organise your analysis around it. |
| **R2** | **Decision space.** At least **six** decisions, each with at least two options and a written rationale (a source, an argument, or evidence from the data). List excluded combinations and why they are excluded. The full space must contain **at least 100** universes. Every option must be one you would defend to a reviewer. Including an option only to show it fails is not allowed; discuss such options separately. |
| **R3** | **Pipeline.** `multiverse.run_universe(choices, data_dir=None)` runs one universe from the raw CSVs to a result dict with at least `estimate, se, ci_low, ci_high, p_value, n_obs`. It must respect `data_dir`: the assessors run it on a re-generated panel. |
| **R4** | **Results.** `multiverse/spec.yaml` (estimand, model, decisions with options and rationale, exclusions, and the `default` universe you would have run without a multiverse) and `multiverse/results.csv` (one row per valid universe: `universe_id`, one column per decision in spec order, then the statistics). Use the format in [`starter/multiverse/spec.example.yaml`](starter/multiverse/spec.example.yaml). |
| **R5** | **Analysis.** At minimum: (a) a specification curve, or an equivalent display, for each outcome scale; (b) an attribution of result variation to decisions (for example the variance explained by each decision and pairwise interactions, or the shift in median estimate per option); (c) the share of universes supporting each qualitative conclusion (significantly positive, null, significantly negative) **within** comparable estimands; and (d) where your default universe sits in the distribution. |
| **R6** | **Inference about robustness.** Go beyond counting significant results. For example, use a permutation-based or bootstrap test of the whole curve (as in Simonsohn et al.), or argue explicitly why such a test is or isn't meaningful here. |
| **R7** | **Validity and limits.** Threats to validity for the design and for the multiverse itself (the space is your choice: how could it be biased?). Include at least one **ablation**: show how the conclusions change if one decision is fixed or removed from the space. |
| **R8** | **Recommendation.** One paragraph the funder could publish, with its caveats, plus a one-paragraph note to the evaluation team on what data to collect differently next time. |

### D.2 Engineering requirements

- The whole multiverse regenerates with one command, documented in your README, in under 15 minutes on a laptop.
- Cleaning steps are separate, testable functions. **At least 10 tests of your own** (for example period harmonisation, duplicate handling, deflation, and the estimator on a tiny constructed panel with a known effect).
- The public tests in [`tests/test_requirements.py`](tests/test_requirements.py) must pass: they check that the spec and results agree and that results reproduce.
- Bounded dependencies in `requirements.txt`.

### D.3 Research ethics and responsible reporting

The data is **synthetic** and describes no real village or business. Multiverse methods can be misused in both directions: to manufacture apparent robustness, or to manufacture doubt about an inconvenient result. In your report, state how you guarded against both, for example by fixing the decision space before looking at results (with commit history as evidence) or by documenting every revision to the space and why. Programme evaluations affect funding for real communities, so explain how your recommendation avoids overstating certainty.

### D.4 Optional enhancements

- Effect heterogeneity by enterprise type within the multiverse. Does the pooled estimate hide opposite effects?
- A pre-registration-style document committed before your first full run.
- Sensitivity of the conclusions to the clustering choice or to a wild-cluster bootstrap with 60 clusters.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Data** | [`enterprise_panel.csv`](resources/data/enterprise_panel.csv) (4,608 interview records, about 330 KB) · [`villages.csv`](resources/data/villages.csv) (60 villages) · [`cpi_index.csv`](resources/data/cpi_index.csv) (monthly illustrative index, January 2024 to June 2026) |
| **Provenance** | **Synthetic**, generated by CLBG with a fixed seed from a model of enterprise revenue with known effects and documented data-quality problems. State names are real; villages, enterprises and the price index are fictional. The generator and true effects are kept in the assessor kit. |
| **Licence** | CC BY 4.0 (same as this repository's content) |
| **Integrity** | SHA-256 values are checked by `tests/test_contract.py`. |

**Codebook: `enterprise_panel.csv`** (all text)

| Column | Meaning |
|---|---|
| `record_id` | Interview record ID (unique) |
| `enterprise_id` | Enterprise, stable across rounds |
| `village_id` | Village (join to `villages.csv`) |
| `round` | 0 baseline, 1 midline, 2 endline |
| `interview_date` | ISO date |
| `enterprise_type` | `shop`, `food_vendor`, `tailor`, `salon`, `grinding_mill`, `phone_charging` |
| `owner_sex` | `F` / `M` |
| `status` | `operating`, `closed`, `not_found` |
| `grid_connected` | Whether the village was connected on the interview date |
| `revenue` | Reported revenue in naira, or empty |
| `revenue_period` | `week`, `month`, or empty (not recorded) |
| `hours_open_per_day`, `employees` | Recorded for operating enterprises |

**`villages.csv`**: `village_id`, `state`, `programme_arm` (`treatment`/`control`), `connection_date` (empty for control), `distance_to_town_km`.

**Known limitations.** The design is observational difference-in-differences with 60 clusters. Revenue is self-reported. The price index is illustrative. Some problems are deliberately not fully identifiable from the data (which revenues have an extra zero; which unrecorded periods were weekly). That is what makes them forks.

**Setup**

```bash
cd assessments/data-science/tier-3/units/DS-03-data-cleaning-and-quality/DS-T3-003-the-garden-of-forking-paths
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract      # passes immediately
pytest                  # requirement tests pass once spec.yaml, results.csv and run_universe agree
```

**Key reading** (find and read these; cite what you use):
- Steegen, S., Tuerlinckx, F., Gelman, A., and Vanpaemel, W. (2016). Increasing transparency through a multiverse analysis. *Perspectives on Psychological Science*, 11(5).
- Simonsohn, U., Simmons, J. P., and Nelson, L. D. (2020). Specification curve analysis. *Nature Human Behaviour*, 4.
- Gelman, A., and Loken, E. The garden of forking paths (essay, 2013; later version in *American Scientist*, 2014).
- Any standard treatment of difference-in-differences with clustered standard errors, and of the inverse hyperbolic sine transformation and its scale dependence.

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `multiverse/` package with `spec.yaml` and `results.csv` | The decision space and its results, reproducible universe by universe |
| 2 | `tests/` (provided plus ≥ 10 of your own) | Evidence the cleaning steps and estimator do what you claim |
| 3 | `analysis.py` or `analysis.ipynb` | Regenerates every figure and table in the report |
| 4 | `MULTIVERSE_REPORT.md` (3,000–5,000 words plus figures), from the [template](submission-template/MULTIVERSE_REPORT.md) | Technical report: estimand, space, results, attribution, validity, recommendation |
| 5 | `AI_USE_AND_SOURCES.md` | Integrity declaration |
| 6 | 30-minute defence | Defend the space and the conclusions (see §K) |

---

## G. Acceptance Criteria

⚙ = automated; ✍ = assessor judgement. At Tier 3, most of the evidence is in the reasoning.

1. ⚙ Public tests pass: the spec has at least six decisions with rationales and a default; the results cover exactly the valid space (at least 100 universes); statistics are sane; and five sampled universes reproduce from raw data.
2. ⚙ Hidden tests: 25 further random universes reproduce (estimate and SE to a relative 10⁻⁶), every option appears in the results, and `run_universe` runs on a re-generated panel through `data_dir` and gives a different estimate from the public file. *Justification:* exact reproducibility is what makes a multiverse auditable. A pipeline that ignores `data_dir` is hard-coded to the public file.
3. ✍ **Estimand discipline:** the report says which universes estimate what, and never pools estimates from different outcome scales or estimands into one curve or one share without justification.
4. ✍ **Space quality:** every option is defensible; the exclusions are argued; the space is neither padded nor narrowed to force a conclusion; and revisions to the space are documented.
5. ✍ **Attribution:** a quantitative decomposition identifies the decisions that matter, and the report explains *why* they matter in terms of the data-generating problem (for example, what dropping closed businesses does).
6. ✍ **Inference and ablation:** R6 and R7 are addressed with a method, not just an assertion.
7. ✍ **Recommendation:** the funder paragraph is honest about fragility and scope, and the data-collection note follows from the analysis.

---

## H. Evaluation Rubric

Full rubric: **[rubric.md](rubric.md)**.

| Dimension | Points |
|---|---|
| Problem framing and estimand | 15 |
| Technical correctness and reproducibility | 15 |
| Implementation quality | 10 |
| Research methodology (decision space, multiverse design) | 20 |
| Analysis, inference and ablation | 15 |
| Documentation | 5 |
| Validity, critical thinking and limitations | 15 |
| Communication (report and recommendation) | 5 |
| **Total** | **100** |

---

## I. Submission Instructions

1. A private repository named `clbg-DS-T3-003-<your-github-username>`, built from this assessment's `starter/`, `tests/`, `resources/` and `submission-template/`.
2. Expected structure:
   ```text
   clbg-DS-T3-003-<username>/
   ├── README.md                 # how to regenerate everything, in 10 lines or fewer
   ├── requirements.txt
   ├── multiverse/               # package + spec.yaml + results.csv
   ├── tests/
   ├── resources/                # unchanged
   ├── analysis.py | analysis.ipynb
   ├── figures/
   ├── MULTIVERSE_REPORT.md
   └── AI_USE_AND_SOURCES.md
   ```
3. **Commit as you work, and commit `spec.yaml` before your first full run.** The history is part of the evidence that the space was not tuned to the results (D.3).
4. Submit through the **Assessment submission** issue template with the repository URL and commit SHA, and add the assessor account as a read-only collaborator.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines). General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

1. **Heterogeneity multiverse.** Run the multiverse separately by enterprise type. Do some types show robust effects of opposite sign that the pooled estimate hides?
2. **Joint inference.** Implement the permutation test for the specification curve (re-assign treatment at the village level and recompute the whole curve), and report the share of permuted curves at least as extreme as the observed one.
3. **Bayesian multiverse.** Replace the per-universe estimates with a hierarchical model that pools across universes, and explain what that pooling assumes.
4. **Designing the next survey.** Use your attribution results to propose the two questionnaire changes that would remove the most consequential forks.

---

## K. Assessment Integrity

**AI tools are permitted** for learning (for example to explain fixed-effects estimation, the inverse hyperbolic sine or specification curves), for reviewing your code, and for editing prose. **They are not permitted to design your decision space, choose your estimand or write your analysis.** Disclose every use in `AI_USE_AND_SOURCES.md`.

- **Cite** every methodological source.
- **Collaboration:** you may discuss the literature and general techniques. You may not share decision spaces, code, results or report text.
- **How understanding is verified (30 minutes):**
  1. **Defend the space (10 minutes).** The assessor picks two of your decisions and asks you to defend each option against an alternative they propose, and to justify one exclusion.
  2. **Trace a universe (5 minutes).** The assessor picks a row of `results.csv`. You rerun it live and explain each cleaning step's effect on the sample size and the estimate.
  3. **Unseen fork (10 minutes).** The assessor proposes a new decision (for example treating `not_found` enterprises as closed, or a different deflation month). Before running anything, you predict which universes it would move and in which direction. Then you add it and rerun a subset.
  4. **Critique (5 minutes).** "Your colleague says the multiverse proves the programme failed. What do you say?"

See [assessment integrity](../../../../../../docs/assessment-integrity.md).

---

## Pedagogical Design

*This section explains the design of the assessment for members, mentors and assessors.*

| Question | Answer |
|---|---|
| **Knowledge needed** | Panel regression with fixed effects, clustered inference, data cleaning, and reading methods papers. |
| **New skill developed** | Treating analytic flexibility as an object of study: making the choices explicit, measuring their influence, and stating a conclusion whose robustness is known. |
| **Decisions the member must make** | The estimand(s); the decisions and options; the exclusions; how to compare across scales; how to attribute variation; what inference to draw about robustness; what to tell the funder. |
| **What must be investigated independently** | Each data problem and its plausible fixes; the literature on multiverse and specification-curve analysis; why some forks change the estimand; what the closures are doing. |
| **Why it's interesting** | The headline sentence the funder wants is supported by some defensible paths and contradicted by others, and the decisive fork is not an obvious "cleaning" step. A member who looks carefully finds that a conclusion can be robust within one estimand and fragile across estimands, which is a more useful finding than either "robust" or "fragile". |
| **Evidence of competence** | A reproducible multiverse verified on held-out data; an argued decision space; a quantitative attribution; a validity analysis and a recommendation that survive a 30-minute defence. |
| **Misconceptions exposed** | "Cleaning choices are neutral." "Robust means most universes are significant." "Estimates on log, IHS and level scales can be pooled." "Dropping closed businesses is just handling missing data." "A bigger multiverse is a better multiverse." |
| **Preparation for later work** | It leads into any research or evaluation role where results must be defended, into ML evaluation (where preprocessing choices create the same forking paths), and into the reproducibility and research-integrity work expected at research level. |

**Suggested approach** (optional): profile the data and write down every fork you notice *before* reading the multiverse papers; then read them and revise. Write the estimand first. Build and test the cleaning functions individually. Commit the spec. Run a small multiverse first, inspect it, and only then run the full space, documenting any change you make to it.

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
