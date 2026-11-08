# DS-T2-011: One House Style

> *Build the chart style system a research desk will use for years: an accessible palette proven under colour-vision deficiency, a theme and annotation API, and a visual-regression check that catches real changes but ignores rendering noise. Then justify every choice against a baseline.*

![Format: Implementation](https://img.shields.io/badge/format-implementation-0366d6) ![Tier 2](https://img.shields.io/badge/tier-2-fb8c00) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20offline-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `DS-T2-011` |
| **Title** | One House Style: An Accessible, Regression-Tested Chart Style System |
| **Subtrack** | Data Science |
| **Tier** | 2: Applied Engineering and Independent Problem-Solving |
| **Unit** | [DS-06: Data Visualization and Storytelling](../README.md) |
| **Format** | Implementation (secondary: Comparative) |
| **Difficulty** | Technical 3 · Mathematical 3 · Research 3 · Engineering 3 · Ambiguity 3 · Resources 1 (each out of 5) |
| **Estimated time** | 20–35 hours over 2–3 weeks |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM. No GPU, no paid services, and no internet after setup |
| **Recommended prerequisites** | Confident matplotlib (rcParams, artists, `savefig`); numpy; colour spaces at the level of [DS-T1-015](../../../../tier-1/units/DS-06-visualization-and-storytelling/DS-T1-015-the-truth-behind-the-chart/README.md); `pytest` fixtures |
| **Skills developed** | Colour-vision-deficiency simulation; colour-difference metrics; WCAG contrast; designing a palette under constraints; theme and annotation APIs; visual regression testing and tolerance calibration; design rationale writing |
| **Technologies** | Python 3.10+, numpy, pandas, matplotlib, pytest |

---

## B. Problem Statement

**Naira Ledger Research** (fictional) publishes a quarterly mobile-money report read by regulators, banks and journalists. Its charts are made by five analysts, each with their own matplotlib habits. The result is inconsistent colours, legends in random corners, and charts that fail for readers with colour-vision deficiency (CVD). Roughly 1 in 12 men of Northern European descent have a red–green CVD, and prevalence varies by population. The desk also had an embarrassing incident: a library upgrade silently changed a chart's colours *after* sign-off, and nobody noticed until a bank complained.

The head of research wants **one house style, enforced by code**:

1. a categorical palette that remains distinguishable under protan, deutan and tritan simulation and has enough contrast against the white page;
2. a `theme()` and a small annotation API (`annotate_source`, `label_lines`, `highlight`) so that every analyst's chart looks the same and labels data directly instead of using legends;
3. a **visual-regression check** that compares each report chart with a committed baseline image and fails when something meaningful changes;
4. the five charts of the next report rebuilt with the system.

**This is a Tier 2 task: the goal and the constraints are fixed, the methods are yours.** The contract (function names and return types) is fixed so that it can be tested, but you choose and justify:

- **which CVD simulation** to implement (for example Brettel, Viénot & Mollon 1997; Viénot, Brettel & Mollon 1999; or Machado, Oliveira & Fernandes 2009), and at what severity;
- **which colour-difference formula** (CIE76, CIE94 or CIEDE2000), and why it suits small chart marks;
- **which palette**, which must beat matplotlib's default `tab10` on the audit, so you must show by how much;
- **which image signature and tolerance** for regression testing. This is the hardest decision. A naive perceptual hash either fires on harmless rendering noise or misses a recoloured series. You must **measure** false alarms and misses on deliberately perturbed charts and choose a tolerance from evidence.

**Fixed by the organisation** (not negotiable):
- Every palette colour has a contrast of at least **3:1** against the background (WCAG 2.x success criterion 1.4.11, non-text contrast).
- Under the desk's own checker, every pair of palette colours differs by **ΔE2000 ≥ 10** under each of protan, deutan and tritan simulation (Machado 2009, severity 1.0). The desk chose 10 because a just-noticeable difference is about 1–2 units for large patches, and thin lines and small markers need a wide safety margin. A palette satisfying both rules exists (the assessor's reference reaches about 20), and `tab10` fails badly (about 1.3 under protan).

---

## C. Objectives

When you finish, you should be able to show that you can:

1. **Implement** a published CVD simulation and a colour-difference formula, and validate them against known properties and reference values.
2. **Design** a categorical palette under multiple constraints (contrast, CVD distinguishability, size), and **compare** it quantitatively against a baseline palette.
3. **Engineer** a reusable theme and annotation API with clean state handling (no leaked rcParams).
4. **Design and calibrate** a visual-regression check: define benign and meaningful perturbations, measure both, and justify a tolerance with the trade-off made explicit.
5. **Communicate** design decisions in a rationale that another analyst could follow and challenge.

---

## D. Technical Requirements

### D.1 Mandatory requirements (the contract)

Implement `housestyle` in [`starter/housestyle/`](starter/housestyle/). The names, signatures and return types in the starter are the contract. Everything inside is your design.

| ID | Requirement |
|---|---|
| **R1** | `contrast_ratio(fg, bg) -> float`: the WCAG 2.x contrast ratio (relative luminance from linearised sRGB). Accepts hex strings or RGB in [0, 1]. Symmetric. |
| **R2** | `simulate_cvd(rgb, kind) -> array` for `kind` in `"protan"`, `"deutan"`, `"tritan"` (anything else raises `ValueError`): a published dichromacy simulation, implemented by you (not imported from a colour library), on any array of shape `(..., 3)` in [0, 1]. Output is the same shape and in [0, 1], and greys stay grey. Set `CVD_METHOD` to its name and citation. |
| **R3** | `delta_e(c1, c2) -> float` using the formula named in `DELTA_E_METHOD` (`"CIE76"`, `"CIE94"` or `"CIEDE2000"`), via CIELAB under D65. White against black must be 100 (within 0.1). |
| **R4** | `audit_palette(colors, background, min_delta_e, min_contrast) -> PaletteReport` with `min_delta_e` and `worst_pair` for each of `"normal"`, `"protan"`, `"deutan"`, `"tritan"`, plus `min_contrast` and `passes`. |
| **R5** | `PALETTE`: at least 6 distinct hex colours that pass your audit **and** the organisation's checker (§B). |
| **R6** | `theme()`: a context manager that applies the house rcParams (including `PALETTE` as the colour cycle) and restores the previous rcParams on exit, even after an exception. |
| **R7** | `annotate_source(target, text)` adds a figure text starting `Source:` (`target` is a Figure or an Axes) and returns it. `label_lines(ax)` removes the legend and adds a text label for each labelled line near its last point, in the line's colour. `highlight(ax, label)` keeps one line coloured and mutes the others to a single grey, raising `ValueError` for an unknown label. |
| **R8** | `image_signature(img)`, `signature_distance(a, b) -> int` and `compare_to_baseline(img, baseline_png, tolerance=TOLERANCE) -> (ok, distance)`, where `img` may be a Figure, a PNG path or an RGB(A) array. Re-rendering a chart gives distance 0. **Benign** perturbations (Gaussian pixel noise with σ = 0.02, a 1-pixel horizontal shift) must stay within `TOLERANCE` on all five report charts. **Meaningful** changes (shortening a bar by 30%, recolouring a series to another palette colour, scaling the main line by 25%) must exceed it. The perturbations are in [`tests/perturb.py`](tests/perturb.py). |
| **R9** | `make_chart(name, data_dir) -> Figure` for each name in `CHARTS`, and `build_report(data_dir, out_dir) -> list[Path]` writing `<name>.png`. Every chart uses the theme, labels its axes, has a `Source:` line, and uses only palette colours or greys. Commit the five PNGs as `baselines/<name>.png`. |
| **R10** | `DESIGN_RATIONALE.md` contains three **comparisons against a baseline**: (a) your palette vs `tab10` (and one published CVD-safe palette, such as Okabe–Ito) on the full audit; (b) your colour-difference formula vs one alternative on at least 10 colour pairs, showing where they disagree; (c) your signature vs a naive alternative (for example an average or difference hash), with a table of benign and meaningful distances on all five charts and the false-alarm and miss rates at your tolerance. |

### D.2 Engineering requirements (mandatory)

- **Implement the colour science yourself.** No `colorspacious`, `colour-science` or similar for R1–R3 (you may use them in a test to cross-check, if you add them to a separate `requirements-dev.txt`).
- **No state leaks.** Importing `housestyle` must not change global rcParams. Only `theme()` does, and only inside the block.
- **Deterministic rendering.** Fixed figure size and DPI, and no timestamps in the images.
- **Tests.** Keep the provided tests passing and add at least **12** tests of your own in `tests/test_member_*.py`, including a regression test for every chart and a test that `theme()` restores state after an exception.
- **Package quality.** Type hints on the public functions, docstrings stating units and ranges, and a short `README.md` showing a 10-line usage example.

### D.3 Accessibility and responsibility

- Accessibility here is a requirement, not a polish item. Record in the rationale what your checks do **not** cover: anomalous trichromacy at lower severities, monochrome printing, low-vision zoom, and screen readers (you could suggest alt-text conventions).
- Simulation is a model. One paragraph should say how you would validate the palette with real readers who have CVD, with consent and without collecting medical data beyond a self-reported type.

### D.4 Optional enhancements (not required for full marks)

- A sequential and a diverging colormap that pass the DS-T1-015 lightness rules, added to the theme.
- An `alt_text(fig)` helper that drafts a description from the chart's artists.
- A `housestyle check` CLI that audits every PNG in a folder against its baseline and prints a table.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Data** | [`resources/data/`](resources/data/): `channel_value.csv` (6 channels × 20 quarters), `provider_failures.csv` (6 anonymised providers × 20 quarters), `agents_by_zone.csv` (6 geopolitical zones), `fraud_reports.csv` (20 quarters). About 10 KB. |
| **Provenance** | **Synthetic**, from [`resources/generate_data.py`](resources/generate_data.py) `--seed 2026`. "Naira Ledger Research", the providers and the "verification rule" are fictional, and every number is invented. |
| **Licence** | CC BY 4.0 |
| **Integrity** | The contract tests check each file's SHA-256 and the generator's determinism. |
| **Perturbations** | [`tests/perturb.py`](tests/perturb.py): the benign and meaningful changes used by the public and hidden tests |

**References to start from** (find and cite them yourself): WCAG 2.2 (contrast ratio and SC 1.4.11); Machado, Oliveira & Fernandes (2009), *A physiologically-based model for simulation of color vision deficiency*; Viénot, Brettel & Mollon (1999); Sharma, Wu & Dalal (2005) on CIEDE2000 implementation, including test data; Okabe & Ito, *Color Universal Design*.

**Setup**

```bash
cd assessments/data-science/tier-2/units/DS-06-visualization-and-storytelling/DS-T2-011-one-house-style
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract       # passes immediately
pytest                   # fails until you implement the contract
```

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `housestyle/` package | The style system, the core engineering evidence |
| 2 | `tests/test_member_*.py` (≥ 12) | Shows the system is pinned down, including regression tests per chart |
| 3 | `baselines/*.png` (5) and `report/` (the built report PNGs) | The committed visual contract and the output |
| 4 | `DESIGN_RATIONALE.md` (at most 2,000 words plus tables), using the [template](submission-template/DESIGN_RATIONALE.md) | The three baseline comparisons (R10) and every justified choice |
| 5 | `STYLE_GUIDE.md` (at most 1 page) | What an analyst on the desk reads: how to use the theme, when to highlight, how to label |
| 6 | `AI_USE_AND_SOURCES.md` | Integrity declaration (see §K) |
| 7 | A 10–20 minute defence (live) | Verifies understanding (see §K) |

---

## G. Acceptance Criteria

⚙ = automated (public and hidden suites), ✍ = assessor.

1. ⚙ `pytest` passes all provided and member tests in a clean environment.
2. ⚙ **Organisational palette check.** An independent checker (Machado 2009 at severity 1.0, CIEDE2000) finds min ΔE ≥ 10 under protan, deutan and tritan for your `PALETTE`, and every colour has a contrast of at least 3:1 against white. *Justification:* see §B. The thresholds are reachable, since the reference palette gives about 20.
3. ⚙ **Colour functions.** `contrast_ratio` matches WCAG to a relative tolerance of 1e-6 on 50 random pairs. `delta_e` matches an independent implementation of your declared method to 0.2% on 40 random pairs. Greys survive CVD simulation within 2 L* units, and known confusion pairs collapse (and known safe pairs do not) under your simulation.
4. ⚙ **Regression on every chart.** For all five charts, benign perturbations stay within `TOLERANCE` and every meaningful change exceeds it. *Justification:* the perturbations bracket what a CI re-render plausibly changes (noise, sub-pixel layout) against the changes the desk must catch (data, colour).
5. ⚙ **Style consistency.** Every line and bar in the report uses a palette colour or a grey (chroma below 8), and every chart has a `Source:` line.
6. ✍ The rationale's three comparisons (R10) are present, quantitative and honest, and the tolerance comes from measured distances with false-alarm and miss rates stated.
7. ✍ The limits paragraph (§D.3) is specific: what the checks miss, and how real-reader validation would work ethically.
8. ✍ `STYLE_GUIDE.md` is usable by an analyst who has not read the code.

---

## H. Evaluation Rubric

The full rubric with performance-level descriptors is in **[rubric.md](rubric.md)**. Summary:

| Dimension | Points |
|---|---|
| Problem understanding and technical reasoning | 10 |
| Technical correctness | 20 |
| Implementation quality (API and engineering) | 20 |
| Methodology: comparisons against baselines | 15 |
| Testing and evaluation (incl. tolerance calibration) | 15 |
| Documentation and reproducibility | 5 |
| Critical thinking and limitations | 10 |
| Presentation and communication | 5 |
| **Total** | **100** |

The outcome is decided by the score **and** the gates in the rubric. See the [placement framework](../../../../../../docs/placement-framework.md).

---

## I. Submission Instructions

1. **Create a private repository** named `clbg-DS-T2-011-<your-github-username>` from this assessment's `starter/`, `tests/`, `resources/`, `submission-template/` and `.gitattributes`.
2. **Expected structure:**
   ```text
   clbg-DS-T2-011-<username>/
   ├── README.md               # usage example, how to run
   ├── requirements.txt
   ├── housestyle/
   ├── tests/
   ├── resources/              # unchanged
   ├── baselines/*.png
   ├── report/*.png
   ├── DESIGN_RATIONALE.md
   ├── STYLE_GUIDE.md
   └── AI_USE_AND_SOURCES.md
   ```
3. **Commit as you work.** Baseline updates must be separate commits with a message saying why the baseline changed. That is how the desk would work.
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing an **Assessment submission** issue with the repository URL and commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines-extensions-and-late-work).
6. General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

1. **Severity sweep.** Plot your palette's minimum ΔE against CVD severity (0 to 1) for each type, and compare with `tab10` and Okabe–Ito.
2. **Greyscale print.** Add a monochrome check (min L* difference) and redesign if needed. Discuss the trade-off with CVD distinguishability.
3. **Cross-version regression.** Render the baselines under two matplotlib minor versions in separate virtual environments and report the real-world benign distances against your synthetic ones.
4. **Reader study.** With consent, ask 3–5 readers (including at least one with self-reported CVD, if someone volunteers) to identify series in the `provider_failures` chart under both palettes. Report the results without identifying anyone.

---

## K. Assessment Integrity

**AI tools are permitted** to explain papers or debug code. **They may not design the system for you.** You must be able to explain and modify every line, and defend every number in the rationale.

- **Disclose** all AI use in `AI_USE_AND_SOURCES.md`. **Cite** the papers whose methods you implemented, and any palette you adapted.
- **Collaboration:** you may discuss general ideas. You may not share code, palettes, tolerances or rationale text.
- **How your understanding is verified.** In the defence, the assessor will:
  1. ask you to explain your CVD simulation step by step (which colour space, and why the matrix is applied there);
  2. introduce a new **benign** and a new **meaningful** perturbation live (for example a 2-pixel shift, or one category's colour swapped with another) and ask you to predict whether your check fires, then run it;
  3. ask you to defend your tolerance against an analyst who complains about false alarms, and against a manager who wants zero misses.

See [assessment integrity](../../../../../../docs/assessment-integrity.md).

---

## Pedagogical Design

| Question | Answer |
|---|---|
| **Knowledge needed** | Colour spaces, matplotlib's artist model and rcParams, test design. |
| **New skill developed** | Engineering accessibility and visual consistency as testable properties, and calibrating a fuzzy check (image similarity) from measured evidence. |
| **Decisions the member must make** | CVD model and severity; ΔE formula; palette; signature design and tolerance; API shape for annotations; what goes into the style guide. |
| **What must be investigated independently** | The CVD and ΔE literature; why naive perceptual hashes fail on mostly white chart images; how other organisations publish style guides. |
| **Why it's interesting** | A real tension sits at the centre: a regression check that never raises a false alarm misses recolouring, and one that catches everything fires on noise. Members discover that hashes designed for photographs behave badly on charts. |
| **Evidence of competence** | An independent palette audit; regression checks on all five charts with perturbations the member didn't design; quantitative baseline comparisons; a live predict-then-run defence. |
| **Misconceptions exposed** | "Colourblind-safe means avoiding red and green." "Any perceptual hash will do." "A tolerance is a magic number." "Accessibility is a final polish step." "Global rcParams are fine." |
| **Preparation for later work** | It leads into the DS-T3 perception experiments (does the palette actually help readers?), ML-engineering CI practices, and any team analytics platform. |

**Suggested approach** (optional): implement and validate the colour science first (week 1), then design the palette with a small search or by hand plus the audit. Build the report charts next, then the regression signature, measuring before you choose anything. Write the rationale as you go, not at the end.

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
