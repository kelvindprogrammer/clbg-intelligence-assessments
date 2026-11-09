# DS-T3-009: The Perception Experiment: Which Chart Do People Read Most Accurately?

> *Everyone repeats that bars beat pies and circles. Build the experiment, plan its sample size, render stimuli that do not lie, and see whether your data agrees.*

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `DS-T3-009` |
| **Title** | The Perception Experiment: Which Chart Do People Read Most Accurately? |
| **Subtrack** | Data Science |
| **Tier** | 3: Advanced and Research-Informed |
| **Unit** | [DS-06: Data Visualization and Storytelling](../README.md) |
| **Format** | Replication (secondary: system-design) |
| **Difficulty** | Technical 3 · Mathematical 3 · Research 4 · Engineering 3 · Ambiguity 4 · Resources 1 (each out of 5) |
| **Estimated time** | 16-24 hours over 2 weeks |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM; matplotlib runs headless (Agg); no GPU or network after setup |
| **Recommended prerequisites** | matplotlib (artists, patches), pandas, and the percentile bootstrap. Familiarity with Cleveland and McGill's hierarchy of elementary perceptual tasks helps but is part of what you read. |
| **Skills developed** | Honest encodings, perceptual error measurement, balanced randomised design, participant-level inference, power simulation, pre-registration |
| **Technologies** | Python 3.10+, matplotlib (Agg backend), pandas, numpy, pytest |

---

## B. Problem Statement

A state ministry's health-communication unit prints posters on immunisation coverage and sends monthly infographics to local government offices. Designers keep choosing between bars, pies and "proportional" circles, and each choice is defended with a sentence like *"people read bars more accurately"*. The unit head asks the data-science team: **is that actually true, how large is the difference, and how would we find out cheaply?**

The classic evidence is Cleveland and McGill (1984), who asked people to judge what percent one value was of another, shown in different encodings, and measured the error as `log2(|judged - true| + 1/8)`. They proposed a ranking of elementary perceptual tasks (position on a common scale first, area near the bottom). Others have criticised or refined it. You are not asked to believe the ranking; you are asked to build the machinery that can *test* it and to understand how much data it takes.

Recruiting hundreds of participants is not possible before the next print run. So you will work with **simulated observers** whose accuracy is controlled by a documented model (`perception_lab/observer.py`): each encoding has a noise level and an exponent that compresses perceived ratios (Stevens-style). That gives you ground truth for your analysis pipeline, as a pilot gives a study its dry run. The point is not to learn about people from a simulation. It is to make sure that when real data arrives, your design, rendering and analysis are already correct, and to know how many participants you will need.

Four things must be right, and each hides a trap:

1. **The stimuli must not lie.** A circle whose *radius* is proportional to the value shows an area ratio that is the square of the data ratio. A graphic that exaggerates cannot be used to measure how well people read graphics. You must render honest stimuli and *measure* their lie factor from the drawn artists, not from your inputs.
2. **The design must be balanced and randomised.** Every participant sees every encoding and ratio equally often, in shuffled order, with the larger value on the left half the time. Otherwise order, side and encoding effects are confounded.
3. **The unit of analysis is the participant.** Trials from one person are not independent. Bootstrapping trials gives intervals that are too narrow.
4. **The ranking must come from the data.** The hidden checks run your analysis on a differently parameterised world, in which a circle (area) is *more* accurate than a bar with unaligned baselines and a pie is worst. If your code quietly bakes in the literature's order, it will fail.

You will also commit a **pre-registration** before looking at results, then report honestly whether the data matched your predictions.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. Render position, length, angle and area stimuli whose displayed ratios provably equal the data ratios, and quantify any distortion with a lie factor.
2. Design a balanced, randomised, counterbalanced and seeded perception experiment.
3. Analyse errors at the participant level with bootstrap intervals, including a signed-bias analysis that reveals compression effects.
4. Estimate by simulation the number of participants needed to recover the true ranking, and show how power changes with participants and repeats.
5. Pre-register hypotheses and an analysis plan, and report results (including contradictions of the literature) without post-hoc rescue.
6. Turn perceptual evidence into a conditional design guideline for non-specialist designers.

---

## D. Technical Requirements

### D.1 Mandatory requirements

Implement the package in [`starter/perception_lab/`](starter/perception_lab/). `observer.py` is provided and must not change (hash-checked). A participant is asked "what percent is the smaller of the larger?"; `true_pct = 100 * min(a, b) / max(a, b)`; `ratio` is smaller/larger.

| ID | Function | Requirement |
|---|---|---|
| **R1** | `render_stimulus(encoding, a, b, honest=True)` | Return a matplotlib `Figure` with one `Axes`. `bar_common`: two rectangles on a common baseline (bottom 0), heights `a`, `b`. `bar_unaligned`: two rectangles with different baselines, heights `a`, `b`. `pie_angle`: two `Wedge` patches with the same degrees per unit of value. `circle_area`: two `Circle` patches with area proportional to the value when `honest`; when `honest=False`, radius proportional to the value (the lie). Unknown encoding raises `ValueError`. |
| **R2** | `displayed_ratio(fig, encoding)`, `lie_factor(encoding, a, b, honest=True)` | Measure from the drawn artists: bar heights, wedge angles (`theta2 - theta1`), circle areas. `lie_factor = displayed_ratio / (min/max of the data)`. `lie_factor` must close the figure it creates. |
| **R3** | `make_design(n_participants, ratios, repeats, seed, encodings=ENCODINGS)` | DataFrame with columns `participant, trial, encoding, ratio, a, b, larger_side, true_pct`. Every participant sees each (encoding, ratio) cell exactly `repeats` times, in random order that is not blocked by encoding; within each cell the larger value is on the left in half the trials (plus or minus one); deterministic given `seed`. |
| **R4** | `log_abs_error(judged_pct, true_pct)` | `log2(|judged - true| + 1/8)`, elementwise. |
| **R5** | `analyze(responses, B=2000, seed=0)` | Per participant and encoding, average the errors; bootstrap **participants** with replacement (seeded, `B` draws) for a 95% percentile interval of each encoding's mean log error. Return a DataFrame sorted by `rank` with columns `encoding, mean_log_error, ci_low, ci_high, mean_signed_error, rank`. `mean_signed_error` is the mean of `judged_pct - true_pct`. |
| **R6** | `ranking_recovery_rate(n_participants, repeats, reps, seed, ratios, true_order, params)` | Simulate whole experiments (design, `simulate_responses`, analysis with `B=200`) and return the fraction whose estimated ranking equals `true_order`. Deterministic given `seed`. |

### D.2 Study requirements (assessed in the report)

- **`PREREGISTRATION.md`**, committed before the final analysis: your predicted ranking with reasons, a predicted direction for the signed bias of each encoding, the primary analysis (what comparison, which interval), your sample-size justification from `ranking_recovery_rate`, and the rule for declaring two encodings "different" (for example non-overlapping intervals, or a bootstrap difference interval excluding zero). Your commit history must show it predates the results.
- A **stimulus gallery** figure with the lie factor annotated for each encoding at three ratios.
- A **results figure** (mean log error with intervals per encoding) and a **bias figure** (signed error against true percent, by encoding), each titled with its finding.
- A **power curve**: recovery rate against number of participants (for at least five values) for the default world, plus one curve for a world of your own design where two encodings are close; explain what drives the difference.
- A **deviation log** in `REPORT.md`: every place the analysis differed from the pre-registration, and why.
- Add at least **six tests** of your own in `tests/test_member_*.py`, including one that your renderer's honesty holds for random value pairs.

### D.3 Privacy and responsibility

The study uses simulated participants. A real study with people needs informed consent, the right to withdraw and anonymised participant IDs (NDPA 2023 applies to the response data and any device metadata). In two sentences in `REPORT.md`, state what you would collect, what you would not (no names, no IP addresses) and how long you would keep raw responses. Also state who might be harmed by a misleading chart in your health-poster setting, and how your honesty checks protect them.

### D.4 Optional enhancements

Add a mixed-effects model (random participant intercept) and compare its interval with your bootstrap; add stimuli for colour lightness or a 3-D bar and show that the lie factor rises; add a Bayesian ranking probability for each encoding.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Data** | None is distributed. Responses are generated by [`starter/perception_lab/observer.py`](starter/perception_lab/observer.py) from the design you build |
| **Observer model** | `judged ratio = true_ratio ** exponent * exp(participant_effect + noise)`. Default noise SD: bar_common 0.04, bar_unaligned 0.07, pie_angle 0.10, circle_area 0.18; exponents 1.0, 1.0, 0.95, 0.70; participant effect SD 0.03. Callers may pass `params` for other worlds |
| **Provenance** | Synthetic; parameters are chosen for teaching, not estimated from people |
| **Licence** | CC BY 4.0 (text), MIT (code) |
| **Integrity** | `observer.py` is hash-checked by the contract test |
| **Reading** | Cleveland and McGill (1984), "Graphical Perception: Theory, Experimentation, and Application to the Development of Graphical Methods", *Journal of the American Statistical Association* 79(387); Tufte, *The Visual Display of Quantitative Information* (lie factor); Heer and Bostock (2010), "Crowdsourcing Graphical Perception", CHI 2010 |

**Known limitations.** A simulation proves your pipeline works, not that people behave this way. Two values per trial only; no colour, no animation, no screen-size effects; participants are exchangeable; no learning or fatigue.

**Setup**
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract
pytest
```

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `perception_lab/` package | Renderer, design, analysis and power simulation |
| 2 | `tests/test_member_*.py` (≥ 6) | Independent verification including a randomised honesty property |
| 3 | `PREREGISTRATION.md` (committed early) | Evidence of hypothesis discipline before results |
| 4 | `study.py`/notebook and `figures/` | Reproducible figures: gallery, results, bias, power curve |
| 5 | `REPORT.md` from the [template](submission-template/REPORT.md) (≤ 1,800 words plus figures) | Findings, deviation log, design guideline, limits |
| 6 | `AI_USE_AND_SOURCES.md` | Integrity declaration |
| 7 | A 10-minute live defence | Verifies understanding and the ability to adapt the experiment |

---

## G. Acceptance Criteria

Criteria marked ⚙ are checked by the public and hidden test suites. Criteria marked ✍ are checked by an assessor.

1. ⚙ Public tests pass: renderer geometry (common baseline, different baselines, proportional wedge angles, area-proportional circles), lie factor 1.0 for honest stimuli and 0.5 for the radius-scaled circle at ratio 0.5, design balance/randomisation/seeding, error values, ranking and intervals, participant-level bootstrap width, and power rising with sample size.
2. ⚙ The participant-level interval for pie_angle matches 1.96 x SE across participants within 25% (a trial-level bootstrap would be several times too narrow).
3. ⚙ Power: with 24 participants and 6 repeats the default ranking is recovered in at least 90% of 30 simulated experiments (reference 1.0), and with 2 participants and 1 repeat in at most 80% (reference about 0.45). *Justification:* the default noise levels give best-to-worst gaps of many standard errors at 24 participants and a gap of about one SE at 2.
4. ⚙ Hidden tests: in a re-parameterised world (circle_area more accurate than bar_unaligned; pie_angle worst and compressed) your analysis recovers that world's ranking on three seeds, finds the bias sign from the data, and the recovery rate in that world is at least 0.85 for 30 participants; the lie factor is 1 for other value pairs and the dishonest circle shows the squared ratio.
5. ✍ `PREREGISTRATION.md` predates the results in the commit history, states a decision rule, and the deviation log is complete.
6. ✍ The report states where the data confirmed the literature's ordering and where it did not, and does not rescue a failed prediction post hoc.
7. ✍ The design guideline for poster designers is conditional (which encoding for which task), quantified (error in percentage points, with intervals) and honest about the simulation's scope.

---

## H. Evaluation Rubric

The full rubric with performance levels is in **[rubric.md](rubric.md)**. Summary:

| Dimension | Points |
|---|---|
| Problem understanding and technical reasoning | 10 |
| Technical correctness | 20 |
| Implementation quality | 10 |
| Methodology and experimentation | 25 |
| Testing and evaluation | 10 |
| Documentation and reproducibility | 5 |
| Critical thinking and limitations | 15 |
| Presentation and communication | 5 |
| **Total** | **100** |

The outcome depends on the score **and** the gates (passing defence, reproducible run, integrity declaration). See the [placement framework](../../../../../../docs/placement-framework.md).

---

## I. Submission Instructions

1. Create a **private** GitHub repository named `clbg-DS-T3-009-<your-github-username>` from this assessment's `starter/` and `tests/` folders and the `submission-template/` files.
2. Expected structure:
   ```text
   clbg-DS-T3-009-<username>/
   ├── perception_lab/         # your package (from starter/); observer.py unchanged
   ├── tests/                  # provided tests + your own test_member_*.py
   ├── PREREGISTRATION.md      # written BEFORE you run the analysis (commit it early)
   ├── study.py | study.ipynb  # the experiment, figures and power curve
   ├── figures/                # stimulus gallery, results, power curve
   ├── REPORT.md               # results, recommendation, AI-use declaration
   └── AI_USE_AND_SOURCES.md
   ```
3. Commit as you work. Your commit history is evidence of authorship (see §K); a single "final" commit will be questioned at defence.
4. Add the CLBG assessor account as a read-only collaborator and file a submission issue using the **Assessment submission** template, with the repository URL and the exact commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines). General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

Optional. They are recognised in feedback but never replace the core requirements.

1. Add a mixed-effects analysis and compare its inference with your bootstrap.
2. Add stimuli for colour lightness and 3-D bars, with their lie factors.
3. Design the real study: recruitment, attention checks, exclusion rules and how they change the analysis.
4. Replicate Heer and Bostock's finding that crowd data reproduce the lab ranking, using a different observer model you justify.

---

## K. Assessment Integrity

**AI tools are permitted** to explain concepts, suggest idioms or review your code. They may not do the assessment for you, and you must be able to explain and modify every line you submit.

- **Disclose** all AI assistance in `AI_USE_AND_SOURCES.md` (template in `submission-template/`): tool, purpose and an example prompt. Undisclosed use discovered at defence is an integrity breach; disclosed, reasonable use is not penalised.
- **Cite** adapted code and any papers or documentation you relied on, with links.
- **Collaboration:** discuss *general techniques* only. Do not share code, results or report text.
- **How understanding is verified.** At a 10-minute defence the assessor will (1) ask you to explain why trials cannot be the bootstrap unit and what would happen to your intervals; (2) hand you a chart on screen and ask you to compute its lie factor; (3) set an unseen modification, such as adding a fifth encoding or changing the ratios, to be run live with your pre-registered criteria.

See [assessment integrity](../../../../../../docs/assessment-integrity.md).

---

## Pedagogical Design

| Question | Answer |
|---|---|
| **Knowledge needed** | matplotlib artists, pandas, bootstrap; the idea of encoding magnitude. |
| **New skill developed** | Running a controlled experiment on charts, including honest stimuli, balanced design, participant-level inference and power. |
| **Decisions the member must make** | How to measure honesty from the drawn graphic; how to counterbalance; the unit of analysis; the decision rule; sample size. |
| **What must be investigated independently** | The original experiment's design, why log2(|e| + 1/8), Stevens' compression, and what a lie factor measures. |
| **Why it is interesting** | The folk wisdom about charts becomes a testable claim; a hidden world in which the folk wisdom is false checks that the analysis is honest. |
| **Evidence of competence** | Stimuli whose geometry is verified from artists, a design that survives balance checks, an analysis that finds an unfamiliar ranking, and a pre-registration that predates results. |
| **Misconceptions exposed** | "Bars are always best"; "proportional circles are fine"; "trials are independent"; "a significant difference is a big one"; "a simulation tells us how people see". |
| **Preparation for later work** | Leads to DS-08 experimental design, DS-12 research methods and any evaluation of dashboards and decision aids. |

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
