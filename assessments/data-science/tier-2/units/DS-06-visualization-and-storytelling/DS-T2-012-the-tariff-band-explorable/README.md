# DS-T2-012: The Tariff Band Explorable

> *"Band A pays more but gets more light." Build an explorable explanation that lets a non-technical household see the real trade-off between tariff bands, supply hours and generator costs. Then find out, with real people, whether it actually helps them understand.*

![Format: Open-ended](https://img.shields.io/badge/format-open--ended-8e44ad) ![Tier 2](https://img.shields.io/badge/tier-2-fb8c00) ![CPU only](https://img.shields.io/badge/compute-CPU%20%7C%20internet%20for%20research-blue)

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `DS-T2-012` |
| **Title** | The Tariff Band Explorable: Explaining an Electricity Policy Trade-off to Households |
| **Subtrack** | Data Science |
| **Tier** | 2: Applied Engineering and Independent Problem-Solving |
| **Unit** | [DS-06: Data Visualization and Storytelling](../README.md) |
| **Format** | Open-ended (secondary: Investigation) |
| **Difficulty** | Technical 3 · Mathematical 2 · Research 3 · Engineering 3 · Ambiguity 4 · Resources 1 (each out of 5) |
| **Estimated time** | 20–35 hours over 2–4 weeks |
| **Collaboration** | Individual (your usability participants are not collaborators) |
| **Compute** | Any laptop. A browser and a text editor are enough for the explorable. Internet is needed for research and, optionally, a pinned CDN library |
| **Recommended prerequisites** | Python and pandas; basic HTML, CSS and JavaScript (or willingness to learn them); a DS-06 Tier 1 assessment such as [DS-T1-016](../../../../tier-1/units/DS-06-visualization-and-storytelling/DS-T1-016-honest-about-uncertainty/README.md) |
| **Skills developed** | Modelling a policy trade-off simply and honestly; explorable-explanation design; writing for non-specialists; source verification; small-sample usability testing with consent; comparing a design against a baseline |
| **Technologies** | Python, pandas, jsonschema, pytest; HTML, CSS and JavaScript (vanilla, or one pinned library such as D3 or Vega-Lite) |

---

## B. Problem Statement

Nigeria's electricity distribution companies bill many customers under a **service-based tariff** framework. Feeders are grouped into **bands** (A to E) by the minimum hours of supply they are meant to deliver per day, and the higher bands pay higher tariffs per kWh. In 2024, a large increase in the Band A tariff became national news, and many households asked the same questions: *Is Band A worth it? What if my feeder is moved to Band B? What do I really pay once my generator is included?*

The honest answer depends on a trade-off that is hard to see in a table of tariffs:
- a **lower band** has a lower price per kWh **but** fewer guaranteed hours, so more of the household's demand falls on a generator, inverter or other backup, which usually costs far more per kWh;
- a **higher band** costs more per kWh **but** displaces expensive backup power, **if** the promised hours are actually delivered;
- the household's **effective price per kWh** (grid plus backup) can therefore be *lower* in a more expensive band.

A consumer-advocacy group asks you for an **explorable explanation**: a small interactive web page in the tradition of Bret Victor's "Explorable Explanations" and Nicky Case's work, where a reader moves sliders (their band, hours of supply, monthly demand, generator fuel cost) and *sees* the consequences. It must be honest about what is assumed and uncertain. It must work on a phone, because that is how most of the audience will see it. And the group wants evidence that it helps: you will run a small **usability and comprehension study with 3–5 people** and compare the explorable against a **static baseline**, a one-page fact sheet with the same information.

**What makes it hard.**
- **The model must be simple enough to explain and honest enough to trust.** You decide what it includes (uniform demand? time-of-day patterns? partial backup?) and must state every assumption in the interface itself.
- **The numbers must be real and sourced.** Tariffs and band definitions come from the regulator's published orders and change over time. Generator running costs depend on fuel prices. You must find, verify, cite and date every figure. The starter's numbers are placeholders.
- **"Does it help?" is an empirical question.** With 3–5 participants you cannot prove anything statistically, but a well-run protocol (tasks, think-aloud, pre and post comprehension questions, the System Usability Scale, a counterbalanced baseline comparison) reveals real problems, and you must report them honestly.
- **This is policy. Neutrality matters.** The explorable informs, it does not campaign. You must avoid framing that pushes a conclusion.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. **Frame** a policy trade-off as a small, transparent model with explicit assumptions, and test its behaviour.
2. **Research and verify** the parameters from primary sources, recording provenance for every number.
3. **Design** an explorable explanation whose views each answer a stated reader question, documented in machine-readable specs.
4. **Evaluate** a design with real users through a consented, pseudonymous usability protocol, against a static baseline.
5. **Report** what worked and what did not, including negative findings, and revise the design in response.

---

## D. Technical Requirements

### D.1 Mandatory requirements

The contracts in [`starter/`](starter/) are fixed so that the tests can run. The design is yours.

| ID | Requirement |
|---|---|
| **R1** | `data/tariffs.csv` with columns `band, min_supply_hours, ngn_per_kwh, source_url, accessed` (plus optional notes) for bands A–E, taken from the regulator's **current published order** for one distribution company of your choice. Name the company and the order in `SOURCES.md`, with any other parameters (fuel price, generator efficiency) and their sources. `load_tariffs(path)` reads it. |
| **R2** | `model/tariff_model.py::monthly_cost(household, scenario)` returns the keys in `RETURN_KEYS`. Its behaviour must satisfy: zero demand costs nothing; cost never falls as demand rises; grid cost never falls as the tariff rises; when backup is dearer than grid and covers all unmet demand, cost never rises as supply hours rise; energy balances (grid + backup + unserved = demand); the effective price lies between the grid and backup prices when backup covers everything; invalid inputs raise `ValueError`. |
| **R3** | At least **three views**, each with a spec in `specs/<id>.json` valid against [`resources/view_spec.schema.json`](resources/view_spec.schema.json): the question it answers, the reader task, its encoding, its interactions, its data sources (with URL, access date and licence), how it shows uncertainty, alt text, and its assumptions. Each view answers a different question. |
| **R4** | `explorable/index.html` opens directly from disk in a phone browser, under 2 MB, with a `<title>` and a viewport meta tag. Any external script is pinned to an exact version. It runs the same model as R2, either in JavaScript or from data generated by the Python model, and `PARITY.md` shows the two agree on 10 scenarios. It shows assumptions and sources in the page, not only in the repository. |
| **R5** | A **usability protocol** (`usability/PROTOCOL.md`), written **before** testing: participant criteria, consent script, 3–5 tasks, 3–5 comprehension questions (asked before and after), think-aloud instructions, SUS, and a counterbalanced comparison with your static baseline (`baseline/factsheet.pdf` or `.png`) on at least one task. Run it with **3–5 participants** who are not data-science members. Record the results in `usability/sessions.csv` and `usability/sus.csv` exactly as specified in [`resources/usability_schema.md`](resources/usability_schema.md). |
| **R6** | `usability/analysis.py`: `sus_score(responses)` and `summarise_sessions(sessions)` as specified. `FINDINGS.md` reports the results, every observed problem with its severity, the baseline comparison, and **what you changed** in response (a before-and-after screenshot of at least one revision). |

### D.2 Engineering requirements (mandatory)

- **Tests.** Keep the provided tests passing and add at least **8** of your own (`tests/test_member_*.py`), including the JavaScript–Python parity check if your model runs in JavaScript (for example a Python test that runs the same scenarios through exported JSON).
- **Accessibility.** Controls must be reachable by keyboard and labelled. Results update in an `aria-live` region. Colour must not be the only carrier of meaning. Text contrast is at least 4.5:1.
- **No tracking.** The page collects nothing: no analytics, no forms that send data.
- **Dependencies.** Python: [`starter/requirements.txt`](starter/requirements.txt). Front end: vanilla, or at most one pinned library.

### D.3 Ethics, consent and privacy (mandatory)

This assessment involves people. Follow these rules, which reflect the Nigeria Data Protection Act 2023 and ordinary research ethics:
- **Informed consent** from every participant before the session (what you will do, that it takes about 20 minutes, that they can stop at any time without giving a reason, what you will record, and that only pseudonymous results will be published). Keep the signed or recorded consent **outside** the repository.
- **Adults only** (18+). Do not test with people you supervise or assess, where saying no could be awkward.
- **Minimal data.** Participant codes only. No names, phone numbers, ages, addresses, audio or video in the repository. Notes on think-aloud comments are paraphrased and de-identified.
- **No questions about participants' own bills, income or arrears.** Tasks use fictional households.
- **Neutrality.** The explorable must not tell readers which band to lobby for. Have a peer review the wording for bias, and record the review in `FINDINGS.md`.

### D.4 Optional enhancements (not required for full marks)

- A time-of-day demand profile, so that evening outages cost more than daytime ones.
- Uncertainty in delivered hours (for example "promised 20 hours, delivered 14–20") shown as a band.
- A Hausa, Yoruba, Igbo or Nigerian Pidgin version, tested with at least one speaker.

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Tariffs and band definitions** | **Member-sourced** from the Nigerian Electricity Regulatory Commission's published tariff orders (<https://nerc.gov.ng/>), for one distribution company. Record the order name, date, URL and access date. Tariff orders are public regulatory documents, but quote them accurately and cite them. |
| **Backup-power costs** | **Member-sourced**: a fuel pump price from a dated public source, and a generator efficiency assumption with a citation or a stated, tested assumption. Present all of it as an assumption the reader can change. |
| **Schemas** | [`resources/view_spec.schema.json`](resources/view_spec.schema.json), [`resources/usability_schema.md`](resources/usability_schema.md) |
| **Starter** | The model and usability contracts. No data is provided on purpose: finding and verifying it is part of the task. |
| **Licence** | This assessment's materials are CC BY 4.0. Your sourced numbers keep their providers' terms. |

**Known limitations.** Billing practice differs from published orders (estimated billing, meter availability). Delivered hours often differ from band promises, and a single national story hides large differences between distribution companies. Your explorable should say which of these it ignores.

**Setup**

```bash
cd assessments/data-science/tier-2/units/DS-06-visualization-and-storytelling/DS-T2-012-the-tariff-band-explorable
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r starter/requirements.txt
pytest -m contract       # passes immediately
pytest                   # fails until your data, model, specs, page and usability files exist
```

---

## F. Deliverables

| # | Deliverable | Purpose |
|---|---|---|
| 1 | `explorable/index.html` (and assets) | The explorable itself |
| 2 | `model/`, `data/tariffs.csv`, `SOURCES.md`, `PARITY.md` | A tested, sourced model, and proof that the page uses it faithfully |
| 3 | `specs/*.json` (≥ 3) | A record of what each view is for and what it rests on |
| 4 | `baseline/factsheet.(pdf\|png)` | The static comparison condition |
| 5 | `usability/PROTOCOL.md`, `sessions.csv`, `sus.csv`, `analysis.py` | The evaluation, pseudonymous and reproducible |
| 6 | `FINDINGS.md` (at most 1,500 words plus screenshots), using the [template](submission-template/FINDINGS.md) | Results, the baseline comparison, revisions made, and limitations |
| 7 | `tests/test_member_*.py` (≥ 8) | Behavioural tests of the model and the parity check |
| 8 | `AI_USE_AND_SOURCES.md` | Integrity declaration (see §K) |
| 9 | A 10–20 minute defence with a live demo (see §K) | Verifies understanding |

---

## G. Acceptance Criteria

⚙ = automated (public and hidden suites), ✍ = assessor.

1. ⚙ `pytest` passes all provided and member tests in a clean environment.
2. ⚙ **Model behaviour** (R2) holds on randomised hidden scenarios with unseen tariff tables (60 demand sweeps, 40 tariff and supply sweeps, effective-price bounds). *Justification:* these are properties of any physically sensible cost model, whatever its internal design.
3. ⚙ **Provenance and specs:** `tariffs.csv` has a URL and an access date for every band, and every view spec validates against the schema with a distinct question.
4. ⚙ **Usability data:** only the documented columns are present, codes are pseudonymous, consent is recorded for every row, there are 3–8 participants, no email or phone patterns appear anywhere in `usability/`, and `summarise_sessions` agrees with the data. SUS matches the published formula on random responses. *Justification for 3–5 participants:* small formative studies find many of the most serious usability problems (Nielsen & Landauer, 1993). This is a design-improvement study, not a significance test.
5. ⚙ **Portability:** the page is under 2 MB, has a viewport tag and a title, and pins any external scripts.
6. ✍ Every number in the page and model traces to `SOURCES.md` with a date, or is labelled as an adjustable assumption.
7. ✍ The protocol was written before the sessions (commit history), the baseline comparison was counterbalanced, and `FINDINGS.md` reports problems honestly, including any where the static baseline did better.
8. ✍ At least one revision was made in response to findings, shown before and after.
9. ✍ The page is neutral in framing, accessible by keyboard, and states its assumptions on screen.

---

## H. Evaluation Rubric

The full rubric with performance-level descriptors is in **[rubric.md](rubric.md)**. Summary:

| Dimension | Points |
|---|---|
| Problem understanding and technical reasoning | 10 |
| Technical correctness (model, data, parity) | 15 |
| Implementation quality (the explorable) | 15 |
| Methodology: usability protocol and baseline comparison | 20 |
| Testing and evaluation | 10 |
| Documentation and reproducibility (sources) | 10 |
| Critical thinking and limitations | 10 |
| Presentation and communication | 10 |
| **Total** | **100** |

The outcome is decided by the score **and** the gates in the rubric. See the [placement framework](../../../../../../docs/placement-framework.md).

---

## I. Submission Instructions

1. **Create a private repository** named `clbg-DS-T2-012-<your-github-username>` from this assessment's `starter/`, `tests/`, `resources/` and `submission-template/`.
2. **Expected structure:**
   ```text
   clbg-DS-T2-012-<username>/
   ├── README.md                 # what it is, how to open it, how to run the tests
   ├── requirements.txt
   ├── explorable/index.html
   ├── model/                    # tariff_model.py (+ tests import it)
   ├── data/tariffs.csv
   ├── specs/*.json
   ├── baseline/factsheet.pdf|png
   ├── usability/                # PROTOCOL.md, sessions.csv, sus.csv, analysis.py
   ├── tests/
   ├── SOURCES.md  PARITY.md  FINDINGS.md
   └── AI_USE_AND_SOURCES.md
   ```
3. **Commit as you work.** Commit `PROTOCOL.md` **before** your first session. The timestamp is evidence of pre-planning.
4. **Submit** by adding the CLBG assessor account as a read-only collaborator and filing an **Assessment submission** issue with the repository URL and commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** see [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines).
6. General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

1. **Delivered vs promised hours.** Add uncertainty about delivered hours and test whether participants understand the uncertainty display.
2. **Second distribution company.** Show how the trade-off differs between two companies' tariff orders, without overloading the page.
3. **Language.** Produce and test a version in a Nigerian language.
4. **Remote, unmoderated test.** Run a second round with 5 more participants via a shared link and a short form (still no personal data) and compare it with the moderated round.

---

## K. Assessment Integrity

**AI tools are permitted** for learning, for example JavaScript syntax or debugging layout. **They may not write your model, your findings or your interface copy.** You must be able to explain every line of code and every sentence on the page.

- **Disclose** all AI use in `AI_USE_AND_SOURCES.md`. **Cite** every source of numbers, and any code or design you adapted.
- **Collaboration:** you may discuss general approaches. You may not share code, data files, protocols or findings. Your participants must not be other members attempting this assessment.
- **Fabrication** of usability data is a serious integrity breach. Assessors may ask to see your (offline) consent records, and session notes in redacted form, at defence.
- **How your understanding is verified.** In the defence, the assessor will:
  1. ask you to demo the page on a phone and walk through one task as a participant would;
  2. change one parameter in `tariffs.csv` (for example a new tariff order) and ask you to predict how the main view changes before reloading;
  3. ask which finding surprised you most, and what you would test next with five more people.

See [assessment integrity](../../../../../../docs/assessment-integrity.md).

---

## Pedagogical Design

| Question | Answer |
|---|---|
| **Knowledge needed** | Basic modelling, pandas, HTML and JavaScript (or the willingness to learn), and the principles of honest encodings from Tier 1. |
| **New skill developed** | Designing for comprehension and evaluating that design with people: moving from "the chart is correct" to "readers understand it". |
| **Decisions the member must make** | Model scope; which views and interactions; defaults; wording; the baseline design; tasks and comprehension questions; what to revise. |
| **What must be investigated independently** | The tariff framework and current orders; backup-power costs; the explorable-explanation literature; usability-testing practice and SUS. |
| **Why it's interesting** | A real policy tension with a counter-intuitive result (an expensive band can be cheaper overall), real people to test with, and a static baseline that may beat the interactive version. |
| **Evidence of competence** | Randomised property checks on the model; schema-validated specs; pseudonymous, consented data with a reproducible analysis; documented revisions; a live demo with predictions. |
| **Misconceptions exposed** | "Interactive is always better." "A cheaper tariff means a cheaper bill." "Five users is too few to learn anything." "If I can read it, they can." "Sources can be added at the end." |
| **Preparation for later work** | It leads into the DS-T3 perception experiment (rigorous user studies with power and pre-registration), and into product analytics and research communication. |

**Suggested approach** (optional): week 1, research and the model, with tests. Week 2, a paper prototype and then the page. Week 3, the protocol (committed), sessions and revisions. Week 4, findings. Test the paper prototype with one friend before building anything.

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
