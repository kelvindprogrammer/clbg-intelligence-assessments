# Assessment Authoring Guide

This guide is for anyone writing or revising a CLBG assessment, whether a member, an executive or a maintainer. Follow it, and the validator, the catalogue and the assessors will all work with your assessment without extra effort.

**The reference example is [DS-T1-006: The Registry That Lies](../../assessments/data-science/tier-1/units/DS-03-data-cleaning-and-quality/DS-T1-006-the-registry-that-lies/README.md).** Read it, its tests and its rubric before you write anything.

---

## 1. The design test

Before writing a single requirement, answer the eight pedagogical questions in writing. They become the assessment's `## Pedagogical Design` section:

1. What knowledge does the member need?
2. What new skill will the member develop?
3. What technical decisions must the member make?
4. What must the member investigate independently?
5. What makes the challenge interesting?
6. What evidence will demonstrate competence?
7. What mistakes or misconceptions should the project expose?
8. How does it prepare the member for more advanced work?

Then ask the **final question**: *would this project genuinely challenge someone, teach them something valuable, and provide credible evidence of their ability?* If the honest answer is "sort of", redesign the project.

### 1.1 Interesting, not just correct

Good CLBG assessments have at least one of the following:
- **A hidden twist the data reveals.** Examples: namesakes, a systemic defect, a confounder, a drifted segment.
- **A real tension.** Precision against recall, latency against quality, cost against accuracy, privacy against utility.
- **A question whose answer is not known in advance.** Example: "Does the effect survive controlling for X?"
- **A broken thing to diagnose.** A flawed notebook, a leaky pipeline, an injectable agent.
- **A comparison under controlled conditions,** where the answer depends on the regime.

Avoid generic projects: house-price regression, Titanic, Iris/MNIST as the main task, "build a chatbot", or "make a dashboard" with no question behind it. Familiar datasets are fine as *components*, for example a sanity-check baseline.

### 1.2 Tier fit

Read [tier definitions](../tier-definitions.md). Tier changes the *kind* of competence required, not the size of the task. Check this table against your draft:

| If your assessment… | …then it is probably |
|---|---|
| Fixes interfaces and metrics, and asks for a correct, explained implementation | Tier 1 |
| Fixes the goal and constraints, and leaves method choice, evaluation design and comparison to the member | Tier 2 |
| Leaves framing, methodology and validity arguments to the member, and needs literature, baselines, ablations or architecture trade-offs | Tier 3 |

### 1.3 Formats

Vary the format within each unit. A unit's assessments at one tier must not all use the same format.

`implementation` · `investigation` · `reverse-engineering` · `replication` · `comparative` · `optimization` · `system-design` · `debugging-forensics` · `open-ended` · `capstone`

### 1.4 Accessibility rules

- **CPU first.** Every assessment must be completable on a 4–8 GB RAM laptop, or on a free tier (Google Colab or Kaggle notebooks) with a stated path.
- **No paid APIs required.** Where a hosted LLM API is useful, provide a free or local alternative, such as Ollama, small Hugging Face models, a provider free tier or a deterministic mock, and design the tests to run on the mock.
- **Offline-capable tests.** Contract tests must never need the network.

---

## 2. Directory layout

```text
assessments/<subtrack>/tier-<n>/units/<UNIT>-<unit-slug>/<ID>-<slug>/
├── README.md              # the full specification (sections A–K + Pedagogical Design)
├── metadata.yaml          # validated against shared/schemas/assessment.schema.json
├── rubric.md              # public weighted rubric (must sum to 100)
├── starter/               # optional: scaffolding WITHOUT the solution
├── resources/             # optional: data, reference lists, schemas, generators
├── tests/                 # optional: conftest.py, test_contract.py, test_requirements.py
└── submission-template/   # optional: report templates, AI_USE_AND_SOURCES.md
```

- **IDs and folders** come from the [ID allocation](../../shared/id-allocation.md). The folder is `<ID>-<kebab-case-slug>`.
- **No empty directories.** Only create the folders the assessment needs.
- **Assessor-only material never goes in this repository.** That includes reference solutions, hidden tests, marking notes, defence question banks and any generator that would reveal the answers. It all goes in the private assessor kit under `solutions/<ID>/`.

---

## 3. README specification

The README **must** contain these level-2 headings, in this order, with these exact letters:

```text
# <ID>: <Title>
> one-line hook
## A. Identification
## B. Problem Statement
## C. Objectives
## D. Technical Requirements
## E. Dataset and Resources
## F. Deliverables
## G. Acceptance Criteria
## H. Evaluation Rubric
## I. Submission Instructions
## J. Extension Challenges
## K. Assessment Integrity
## Pedagogical Design
```

The validator enforces minimum substance per section. As a rule of thumb, the full README should be 1,500–4,000 words. Section guidance:

| Section | Must contain |
|---|---|
| **A** | A table with: ID, title, subtrack, tier, unit (linked to `../README.md`), format, the 6-dimension difficulty, estimated time, collaboration, compute, prerequisites, skills and technologies. |
| **B** | A realistic context, why it matters, and what makes it hard. State any "known facts" the member gets. No artificial scenario that exists only to justify a technology. |
| **C** | At least 3 measurable objectives ("you should be able to show that you can…"). |
| **D** | **Mandatory** requirements in a numbered table (`R1`, `R2`, …), engineering requirements, security/privacy requirements, and **optional** enhancements, clearly separated. Fix public interfaces when tests import them. |
| **E** | Data source, direct link, **licence**, format, schema, known limitations, setup commands. For synthetic data: provenance, generator, seed. Use dataset IDs from the [registry](../../shared/datasets/DATASET_REGISTRY.md). |
| **F** | A deliverables table where every deliverable has a stated purpose. |
| **G** | A numbered list of **objectively testable** criteria. Mark the automated ones with ⚙ and the manual ones with ✍. Every numeric threshold must come with a justification, so no arbitrary accuracy bars. Prefer "beats a stated baseline by a margin with a confidence interval", "precision ≥ X *because*…", or behavioural checks. |
| **H** | A summary table and a link to `rubric.md`. |
| **I** | Repository name pattern `clbg-<ID>-<github-username>`, the expected tree, the commit-history expectation, the submission procedure (issue template), deadline and late-policy placeholders, and links to the general guidelines. |
| **J** | 2–5 optional extensions that deepen the work without making the core harder. |
| **K** | Permitted AI use for *this* assessment, the disclosure requirement, collaboration boundaries, and **how understanding is verified**: what will be traced, questioned and modified live at defence. |
| **Pedagogical Design** | A table answering the 8 questions, plus optional "suggested approach" guidance. |

**Links.** All relative links must resolve, and the validator and link checker enforce this. From an assessment folder, the repository root is `../../../../../../`.

---

## 4. `metadata.yaml`

Copy [shared/templates/metadata.template.yaml](../../shared/templates/metadata.template.yaml). Key rules:

- `status` starts as `draft`. It becomes `reviewed` after the quality review ([quality scorecard](../assessment-quality-scorecard.md)), and `approved` only once a named reviewer has signed off.
- `difficulty`: be honest. Calibrate against [tier definitions §5](../tier-definitions.md#5-multi-dimensional-difficulty).
- `compute`: if `gpu` is `required`, or `paid_api` is `optional` or `required`, you must give `free_alternative`.
- `datasets`: registry IDs (`DSET-NNN`), or `synthetic`, `member-sourced` or `none`.
- `ci.heavy: true` if the tests need packages outside the shared CI environment (see `requirements-ci.txt`).

---

## 5. Rubric

Copy [shared/templates/rubric.template.md](../../shared/templates/rubric.template.md). The weighted table's first three columns are `# | Dimension | Points`, and the points must sum to **100**. Start from the default weights:

| Dimension | Default |
|---|---|
| Problem understanding and technical reasoning | 10 |
| Technical correctness | 20 |
| Implementation quality | 15 |
| Methodology and experimentation | 15 |
| Testing and evaluation | 15 |
| Documentation and reproducibility | 10 |
| Critical thinking and limitations | 10 |
| Presentation and communication | 5 |

Adapt the weights when the competency demands it. A research replication might weight methodology at 25. Whatever you change, the "what the assessor looks for" column must be **specific to this assessment**: generic text fails review. Always include the performance-level table and the gates.

---

## 6. Starter code and tests

### 6.1 Starter code: help without answering

- Provide the plumbing (loading, CLI, types, fixed signatures) and leave the thinking to the member.
- Stubs `raise NotImplementedError("R<n>: …")`, with the requirement ID in the message.
- Docstrings say *what* the function must do, never *how*.
- Pin dependencies loosely in `starter/requirements.txt`.

### 6.2 Test conventions

There are two layers of tests:

| File | Marker | Runs where | Must |
|---|---|---|---|
| `tests/test_contract.py` | `pytestmark = pytest.mark.contract` | Public CI, against the **unmodified starter** | Pass on the starter. It checks data integrity (checksums), schema, API signatures and generator determinism. |
| `tests/test_requirements.py` | none | The member's machine; the assessor kit CI against the reference | **Fail** on the starter and **pass** on the reference. It is a *sample* of the requirements, not all of them. |
| `solutions/<ID>/hidden_tests/` (kit) | none | Assessor only | Assess the acceptance criteria on held-out or re-seeded data, so hard-coding fails. |

`tests/conftest.py` must locate the code under test using this search order:
1. `$CLBG_SUBMISSION_DIR`
2. the repository root
3. `starter/`

It must also register the `contract` marker. Copy the conftest from DS-T1-006 and change the package name.

Tests must check **real requirements**. A test that only checks that a file exists is not a test.

### 6.3 Data generators

A synthetic generator must:
- run as `python <generator> --out DIR --seed INT`;
- be **deterministic** for a fixed seed, which the dataset validator checks byte-for-byte;
- create only fictional people, using the reserved `example.ng` domain and random combinations of common names;
- inject defects **only where they serve the learning objectives**, and document each one in the assessor kit (a corruption log is ideal).

Where the generator would reveal the answers, which is usual for forensics assessments, keep it in the kit, commit the generated data publicly with a checksum, and set `resources.generator_in_assessor_kit: true`.

---

## 7. The assessor kit entry (`solutions/<ID>/` in the private repo)

| File | Required | Contents |
|---|---|---|
| `MARKING_GUIDE.md` | ✔ | What strong work looks like (with reference metrics), common mistakes and their scoring impact, how to run the hidden tests, a **defence script** (opening question, trace task, 2–3 unseen modifications, probing questions, red flags), moderation notes, and a rotation procedure if the material leaks. |
| `reference/` | When there is code | A complete reference solution that passes the public and hidden tests. |
| `hidden_tests/` | When automatable | Tests against held-out or re-seeded data. |
| `generator/` | When kept private | The data generator and a truth export. |

For open-ended and research assessments where a single reference solution makes no sense, the marking guide instead gives **calibration exemplars**: short descriptions of an Exemplary, a Proficient and a Developing submission.

---

## 8. Before you open a pull request

```bash
python tools/assessment-validator/validate.py --only <ID>
python tools/test-runner/run_tests.py --only <ID>
python tools/dataset-validator/validate_datasets.py --only <ID>
python tools/catalogue-generator/build_catalogue.py
python tools/repository-checker/check_links.py
```

Then complete the [quality scorecard](../assessment-quality-scorecard.md) in your PR description.
