# DS-T1-015: The Truth Behind the Chart

> *Ten published charts, ten claims. Some are lying, some only look suspicious. Find which is which, measure how badly each one distorts, and redraw it honestly in code that a test can inspect.*

![Format: Debugging & Forensics](https://img.shields.io/badge/format-debugging%20%26%20forensics-6f42c1) ![Tier 1](https://img.shields.io/badge/tier-1-2ea44f) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `DS-T1-015` |
| **Title** | The Truth Behind the Chart: Forensics of Misleading Graphics |
| **Subtrack** | Data Science |
| **Tier** | 1: Foundation and Technical Fluency |
| **Unit** | [DS-06: Data Visualization and Storytelling](../README.md) |
| **Format** | Debugging & Forensics (secondary: Implementation) |
| **Difficulty** | Technical 2 · Mathematical 2 · Research 1 · Engineering 2 · Ambiguity 2 · Resources 1 (each out of 5) |
| **Estimated time** | 10–16 hours over 1–2 weeks |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM. No GPU, no paid services, and no internet after setup |
| **Recommended prerequisites** | Python functions and modules; pandas basics; matplotlib at the level of `plt.subplots`, `ax.bar`, `ax.plot`, `ax.set_ylim`; running `pytest`. Helpful: school-level logarithms and the idea of a least-squares line |
| **Skills developed** | Reading charts critically; Tufte's lie factor; zero baselines and when they matter; dual-axis and window-selection pitfalls; area encodings; perceptual colour spaces (CIELAB) and colormap lightness; inspecting matplotlib Figure objects; writing honest titles |
| **Technologies** | Python 3.10+, pandas, numpy, matplotlib, pytest |

---

## B. Problem Statement

The Communications Integrity Desk of a Nigerian civic-media organisation reviews charts before they are shared on its social channels. Last quarter it reposted a bar chart from a fintech investor deck showing "explosive growth" in an agent network. A reader pointed out that the network had grown by about 5%: the bars only *looked* like they had tripled because the y-axis started at 480,000. The correction got more attention than the original post.

The desk now wants an **automated first-pass auditor**. It has collected a gallery of ten charts from press releases, investor decks, bulletins and sports pages. All the organisations named are fictional, and the data is synthetic but realistic. Each chart comes as a **machine-readable spec** describing how it was drawn, plus the **complete data** the publisher had (which is often more than the chart shows). Your job is to build the tool that:

1. **Diagnoses** each chart against a fixed taxonomy of seven defects, by exact rules;
2. **Quantifies** the distortion where it can be quantified (Tufte's *lie factor*);
3. **Redraws** each chart honestly, as a matplotlib Figure that a test can inspect: zero baselines for bars, a single scale per axis, the full record, area-true sizes, perceptually ordered colour, right-side-up quantities, and a stated source;
4. **Explains** in plain language what a reader of each original would wrongly believe, and what the honest chart supports instead.

**What makes it hard.** The gallery contains **traps in both directions**. Some charts look suspicious but are honest:

- A **line chart with a non-zero baseline** is not lying. Lines encode values by position, and zooming in on a 26–28 °C temperature range is legitimate. Bars encode values by *length*, so a truncated bar axis really does misstate the ratios.
- A **reversed axis** is the norm for league positions (1st at the top). It is a distortion only when the axis holds a *quantity*, such as road deaths drawn so that rising deaths look like falling ones.
- A **short window** is not automatically cherry-picked. The rule in this assessment flags a window only when it covers less than half the record **and** shows the opposite trend to the full record.
- A **log scale** is honest for steady percentage growth, provided the axis says so.

False positives cost the desk credibility just as false negatives do. That's why the hidden tests check your diagnosis *exactly*, on galleries you have never seen.

**Known facts from the desk** (your only documentation, besides the [spec format](resources/SPEC_FORMAT.md)):

- Each chart's CSV holds the complete data, in the order the publisher plotted it.
- The defect rules are fixed (section D, R4). You are implementing the desk's policy, not inventing one, though your report may argue that the policy is incomplete.
- Colours are compared in **CIELAB** (D65), where L* is perceived lightness.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. **Explain**, for each of seven distortion types, *which perceptual channel* is being abused (length, position, area, lightness or orientation) and why it misleads.
2. **Compute** Tufte's lie factor correctly for length- and area-encoded charts, and explain why it is undefined for position-encoded lines.
3. **Implement** an exact, rule-based auditor that makes **no false positives** on honest charts that merely look suspicious.
4. **Convert** sRGB colours to CIELAB and use the lightness profile to decide whether a colormap suits sequential or diverging data.
5. **Produce** honest redraws as matplotlib Figure objects whose properties (limits, labels, artists, colormaps) can be verified programmatically.
6. **Write** a forensic report that states, for each chart, the false belief a reader would form, the size of the distortion, and an honest replacement headline.

---

## D. Technical Requirements

### D.1 Mandatory functional requirements

Implement the `chart_forensics` package in [`starter/chart_forensics/`](starter/chart_forensics/). `io.py`, `render.py` and `__main__.py` are provided plumbing. `colour.py`, `audit.py` and `redraw.py` are yours. The signatures and the constants already in the starter are fixed, because the tests import them.

| ID | Requirement |
|---|---|
| **R1** | `displayed_rows(spec, df) -> DataFrame` returns the rows the published chart shows, with a fresh `0..n-1` index. No `filter` means every row. A filter keeps rows from the first row whose `field` equals `from` to the first row whose `field` equals `to`, inclusive, comparing as strings. Missing or reversed bounds raise `ValueError`. |
| **R2** | `trend_slope(values) -> float` is the ordinary least-squares slope of the values against positions `0..n-1`. Fewer than two values raise `ValueError`. |
| **R3** | `lie_factor(spec, df) -> float` is Tufte's lie factor between the **first and last displayed rows**: *(size of effect shown in the graphic) ÷ (size of effect in the data)*, where an effect is `(last − first) / first`. Data values `v` come from `y.field` (bar and area) or `size.field` (bubble). Graphic sizes `g` are: for bars and areas, `v − b`, where `b` is `y.domain[0]` (or 0 if `domain` is null); for bubbles, `v²` when `size.scale == "radius"` (area grows with the square of the radius) and `v` when it is `"area"`. Any other mark raises `ValueError` (lines encode by position, and the lie factor is a statement about sizes). A zero first value or zero data effect raises `ValueError`. |
| **R4** | `audit(spec, df) -> set[str]` returns exactly the codes from `CODES` that apply: **TRUNCATED_AXIS** if mark is bar or area and `y.domain[0] > 0`. **DUAL_AXIS** if `y2` is present. **CHERRY_PICKED_WINDOW** if a filter exists, the displayed rows are fewer than `WINDOW_COVERAGE_MAX` (0.5) of all rows, and the sign of `trend_slope` over the displayed `y.field` differs from its sign over all rows. **AREA_DISTORTION** if mark is bubble and `size.scale == "radius"`. **MISLEADING_COLORMAP** if mark is heatmap and `colormap_ok(color.scheme, color.scale)` is false. **INVERTED_AXIS** if `y.reverse` is true and `y.type != "rank"`. **MISSING_SOURCE** if `source` is null, empty or whitespace-only. An honest chart returns `set()`. |
| **R5** | `srgb_to_lab(rgb) -> ndarray` converts sRGB in [0, 1] (shape `(..., 3)` or `(..., 4)`, ignoring alpha) to CIELAB, using the standard sRGB transfer function, the sRGB→XYZ matrix and the D65 white point (0.95047, 1.0, 1.08883). It must be vectorised. |
| **R6** | `colormap_ok(cmap, scale) -> bool`. Sample the colormap (a name or a `Colormap`) at `N_SAMPLES` (65) evenly spaced points and compute L*. **Sequential:** L* is monotone, either never falling more than `LIGHTNESS_TOL` (1.0) below its running maximum or never rising more than 1.0 above its running minimum. **Diverging:** let *k* be the index of the maximum L*. The profile rises (within tolerance) up to *k* and falls (within tolerance) after it, *k* lies in 26–38 (the central 20%), and the chroma √(a*² + b*²) of the centre sample (index 32) is at most `CENTRE_CHROMA_MAX` (40). Any other `scale` raises `ValueError`. |
| **R7** | `redraw(spec, df) -> matplotlib.figure.Figure` returns an honest chart that: (a) has a title, and x and y labels on every data axes; (b) contains a text artist starting with `Source:`, saying the source is not stated when the original gave none; (c) shows the **complete, unaltered** data series, all rows, as bars, a line, a filled area or a colour mesh (you may shade the original window); (d) starts every bar and area axis at zero or below; (e) never puts two axes in the same position (no `twinx`); use stacked panels or an indexed single scale instead; (f) gives any scatter markers areas proportional to the values, or replaces bubbles with bars; (g) uses a colormap that passes R6 for the spec's scale; (h) never draws a quantity axis upside down (rank axes may stay reversed). It must not mutate `spec` or `df`. [`tests/figcheck.py`](tests/figcheck.py) shows exactly how each rule is inspected. |
| **R8** | `python -m chart_forensics audit` prints the audit table, and `python -m chart_forensics redraw --out redrawn/` writes one PNG per chart. Both are provided once R3, R4 and R7 work. Commit the PNGs. |

### D.2 Engineering requirements (mandatory)

- **No chart-specific logic.** `audit` and `redraw` must never branch on `spec["id"]`, a title or a field name. Hidden galleries use new ids, fields and colormaps.
- **Inputs are read-only.** Do not modify the gallery files or mutate the `spec` and `df` passed in.
- **Tests.** Keep the provided tests passing and add **at least 10 tests of your own** in `tests/test_member_*.py`. At least three must be *honest-chart* cases that a naive auditor would flag (false-positive guards).
- **Determinism.** `redraw` produces the same Figure properties every time. Don't use random jitter.
- **Dependencies.** Only those in [`starter/requirements.txt`](starter/requirements.txt).

### D.3 Responsible communication

The publishers in the gallery are fictional. Your report still critiques *practices*, so write it as you would about a real organisation: describe what the chart does, not the motives of the people who made it. "The axis starts at 480,000, which makes 5% growth look like 250%" is evidence. "They lied to investors" is an accusation you cannot support from a chart. One paragraph of your report should discuss when a *deliberately* emphatic design (for example a zoomed line chart) is legitimate and how you would disclose it.

### D.4 Optional enhancements (not required for full marks)

- Accept a `--strict` flag that also flags line charts whose y-range hides more than 90% of the scale from zero, and argue in the report whether this belongs in the desk policy.
- Detect a log-scale bar chart (lengths on a log axis are not proportional to values) as an extra code, with your own tests.
- Produce an "honest headline" automatically from the data effect, for example "+5.1% in eight quarters".

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Gallery** | [`resources/gallery/`](resources/gallery/): ten specs (`G01.json`–`G10.json`) and their data (`G01.csv`–`G10.csv`), about 36 KB in total |
| **Format guide** | [`resources/SPEC_FORMAT.md`](resources/SPEC_FORMAT.md) |
| **Provenance** | **Synthetic**, generated by CLBG with a fixed seed. Every organisation, club and number is fictional. The domains (mobile-money agent networks, data prices, grid supply hours, farmer cooperatives, rainfall anomalies, road safety, temperature, instant transfers, football league tables, exam pass rates) were chosen because charts like these circulate widely in Nigerian media. |
| **Licence** | CC BY 4.0 (same as this repository's content) |
| **Integrity** | The contract test checks a SHA-256 over the whole gallery folder. Don't edit the files. A `.gitattributes` file keeps Git from rewriting line endings. |
| **Generator** | Kept in the assessor kit, because it records the ground-truth defects. Hidden tests regenerate fresh galleries with it. |

**Known limitations (by design).** The policy in R4 is deliberately simple. For example, it doesn't catch a line chart zoomed so far that noise looks like a trend, and the 50% window threshold is a convention rather than a law. You implement the policy exactly, and **your report** is where you argue about its blind spots. Why 0.5? A window covering at least half the record cannot hide most of the history, so the desk chose the simplest bar that a reviewer can check by eye.

**Setup**

```bash
cd assessments/data-science/tier-1/units/DS-06-visualization-and-storytelling/DS-T1-015-the-truth-behind-the-chart
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract                   # passes immediately: gallery and scaffold checks
cd starter && python -m chart_forensics render --gallery ../resources/gallery --out ../gallery_png && cd ..
pytest                               # most tests fail until you implement the package
```

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `chart_forensics/` package (the completed starter) | The auditor and redraw logic: the core technical evidence |
| 2 | `tests/test_member_*.py` (≥ 10 tests, ≥ 3 false-positive guards) | Shows you can pin rules down, especially the "looks bad but is honest" cases |
| 3 | `redrawn/G01.png` … `redrawn/G10.png` | The honest charts the desk would actually repost |
| 4 | `FORENSIC_REPORT.md` (at most 1,800 words plus a table), using the [template](submission-template/FORENSIC_REPORT.md) | For each chart: the false belief, the evidence, the lie factor where defined, and an honest headline |
| 5 | `AI_USE_AND_SOURCES.md` | Integrity declaration (see §K) |
| 6 | A 5–10 minute technical defence (live) | Verifies understanding (see §K) |

---

## G. Acceptance Criteria

The submission is **accepted** only when every criterion below holds. ⚙ = checked automatically by the public and hidden suites, ✍ = checked by an assessor.

1. ⚙ `pytest` passes all provided public tests and all of your own tests in a clean environment built from your `requirements.txt`.
2. ⚙ **Exact diagnosis.** On the official gallery **and on two unseen generated galleries** (24 charts each), `audit` returns exactly the ground-truth set for **every** chart. *Justification:* the rules in R4 are deterministic and fully specified, so anything below 100% means a rule was implemented wrongly. The reference implementation scores 58/58.
3. ⚙ **Lie factor** matches the ground truth to a relative tolerance of 1e-4 wherever it is defined, and raises `ValueError` wherever it is not. *Justification:* the tolerance only absorbs floating-point and CSV rounding differences.
4. ⚙ **Colour science.** `srgb_to_lab` agrees with an independent implementation to within 0.001 on random inputs, and `colormap_ok` classifies ten unseen (colormap, scale) pairs correctly, including `Spectral` (an acceptable diverging map whose centre is slightly tinted) and `turbo` (rejected in both roles).
5. ⚙ **Honest redraws.** Every redraw in all three galleries passes every R7 rule as implemented in `figcheck.py`, using the full R6 rule for colormaps.
6. ⚙ No input file is modified (gallery checksum), and `redraw` does not mutate its arguments.
7. ✍ For each of the ten charts, the report states the false belief a typical reader would form, or explains why a suspicious-looking chart is honest. It gives the lie factor where defined, and an honest replacement headline supported by the data (for G01, something like "Active agents grew about 5% in two years", not "Explosive growth").
8. ✍ The committed redraw PNGs match what the code produces, and none keeps a headline that the data contradicts.
9. ✍ The report contains a critical paragraph on at least one limitation of the desk's R4 policy, with a concrete example of a misleading chart it would miss.

---

## H. Evaluation Rubric

The full rubric with performance-level descriptors is in **[rubric.md](rubric.md)**. Summary:

| Dimension | Points |
|---|---|
| Problem understanding and technical reasoning | 10 |
| Technical correctness | 25 |
| Implementation quality | 15 |
| Methodology: evidence for every verdict | 10 |
| Testing and evaluation | 15 |
| Documentation and reproducibility | 5 |
| Critical thinking and limitations | 10 |
| Presentation and communication | 10 |
| **Total** | **100** |

Presentation is weighted higher than the default because this unit is about communication: an honest chart with a misleading title has failed. The outcome is decided by the score **and** the gates in the rubric. See the [placement framework](../../../../../../docs/placement-framework.md).

---

## I. Submission Instructions

1. **Create your own repository** from the starter: copy this assessment's `starter/`, `tests/`, `resources/`, `submission-template/` and `.gitattributes` into a new **private** GitHub repository named `clbg-DS-T1-015-<your-github-username>`.
2. **Expected structure:**
   ```text
   clbg-DS-T1-015-<username>/
   ├── README.md                 # how to run, in 10 lines or fewer
   ├── requirements.txt
   ├── chart_forensics/          # your package (from starter/)
   ├── tests/                    # provided tests + test_member_*.py
   ├── resources/                # unchanged
   ├── redrawn/G01.png … G10.png
   ├── FORENSIC_REPORT.md
   └── AI_USE_AND_SOURCES.md
   ```
3. **Commit as you work.** Your commit history is part of the evidence (see §K).
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing a submission issue in the CLBG assessments repository with the **Assessment submission** issue template. Include the repository URL and the exact commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines).
6. General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

These are optional. They are recognised in feedback but never stand in for the core.

1. **Find one in the wild.** Find a real published chart (with a link and date) that commits one of the seven defects. Write a spec and a CSV for it from the published numbers, and run your auditor on it. Describe the chart's practice neutrally (§D.3).
2. **Colour-vision check.** Extend `colormap_ok` to simulate deuteranopia and report whether the lightness profile still separates the ends of each map.
3. **Lie factor for slopes.** Propose and implement an analogue of the lie factor for line charts (for example the aspect ratio's effect on perceived slope, as in Cleveland's "banking to 45°"), and argue why it is or isn't a fair measure.
4. **Spec linter.** Turn the auditor into a pre-publication check that prints a fix suggestion for each defect.

---

## K. Assessment Integrity

**AI tools are permitted** for learning, for example to explain CIELAB or matplotlib's artist hierarchy. **They may not do the assessment for you.** You must be able to explain and change every line you submit.

- **Disclose** all AI assistance in `AI_USE_AND_SOURCES.md`: the tool, the purpose, an example prompt, and how you checked the output. Disclosed, reasonable use is not penalised. Undisclosed use that becomes apparent at defence is an integrity breach.
- **Cite** any code adapted from documentation or forums, with a link. The CIELAB formulas are standard, so cite where you took them from.
- **Collaboration:** you may discuss *general ideas* (for example "why do bars need a zero baseline?") with other members. You may not share code, verdicts or report text.
- **How your understanding is verified.** In the defence, the assessor will:
  1. show you a chart **you have not seen** (a new spec and CSV) and ask you to predict your auditor's output and lie factor *before* running it;
  2. ask you to explain why G07 (or another honest chart) is not flagged, and what would make it misleading;
  3. give you a small **unseen modification** to implement live, such as a new defect code or a changed coverage threshold, and ask which tests you would add.

See [assessment integrity](../../../../../../docs/assessment-integrity.md) for the full policy.

---

## Pedagogical Design

| Question | Answer |
|---|---|
| **Knowledge needed** | pandas and matplotlib basics, percentages, a least-squares slope, and following a written colour-conversion formula. |
| **New skill developed** | Treating a chart as a *claim about data* that can be checked: map each visual channel to the quantity it encodes, then measure the gap. Also: verifying figures as objects, not by eye. |
| **Decisions the member must make** | How to structure an exact rule engine. How to redraw each mark type honestly (stacked panels or an index for dual axes; bars or area-true bubbles). How to show the original window without hiding the record. What honest headline the data supports. |
| **What must be investigated independently** | Why each rule exists (the perceptual reason), and the honest charts that look guilty. The tests show a sample, not the gallery's verdicts. |
| **Why it's interesting** | The gallery punishes both credulity and over-zealousness. The hidden galleries make guessing impossible, and the 49× lie factor in G01 is a memorable number. |
| **Evidence of competence** | Exact audits on unseen galleries; Figure-level checks on every redraw; a report that names the false belief and an honest headline; live prediction on an unseen chart at defence. |
| **Misconceptions exposed** | "Every axis must start at zero." "Reversed axes are always wrong." "Any short window is cherry-picking." "Rainbow maps are fine if they look nice." "A bigger circle means a proportionally bigger number." "Fix the chart, keep the headline." |
| **Preparation for later work** | It leads into DS-T1-016 (honest uncertainty displays), the DS-T2-011 style system (accessibility checks as code), and DS-T3 work on perception experiments and replicating published graphics. |

**Suggested approach** (optional):

1. Render the gallery and write down, for each chart, what you believe at first glance. Then read the CSV and see how wrong you were.
2. Implement R1, R2, R3 and R5 first. They are small and fully pinned by tests.
3. Write the audit rules one at a time, each with a false-positive guard test.
4. Build `redraw` last, running `figcheck` on every gallery chart after each change.

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
