# Architecture Decisions

This file records the architectural decisions behind the CLBG Intelligence Track assessment ecosystem. Each Architecture Decision Record (ADR) gives the **Context**, the **Decision**, the **Alternatives** considered and the **Consequences**. The evidence behind them is in the [Research and Standards Report](RESEARCH_AND_STANDARDS_REPORT.md).

| Field | Value |
|---|---|
| Owner | CLBG Intelligence Track Assessment Committee |
| Date of record | 2026-11-03 |
| Status of all ADRs below | Accepted |
| How to change | Propose a new ADR (or a superseding one) by pull request; two committee approvals; effective from the next cohort ([assessment policy §1](../assessment-policy.md#1-scope-and-authority)). Superseded ADRs stay in this file, marked *Superseded by ADR-NNN*. |

## Index

| ADR | Title |
|---|---|
| [ADR-001](#adr-001-three-independent-subtracks-with-per-subtrack-placement) | Three independent subtracks with per-subtrack placement |
| [ADR-002](#adr-002-three-qualitatively-different-tiers) | Three qualitatively different tiers |
| [ADR-003](#adr-003-the-unit-architecture) | The unit architecture |
| [ADR-004](#adr-004-the-standard-assessment-specification) | The standard assessment specification |
| [ADR-005](#adr-005-two-repositories) | Two repositories |
| [ADR-006](#adr-006-id-scheme-and-pre-allocation) | ID scheme and pre-allocation |
| [ADR-007](#adr-007-metadata-schema-and-six-dimensional-difficulty) | Metadata schema and six-dimensional difficulty |
| [ADR-008](#adr-008-three-layer-test-design) | Three-layer test design |
| [ADR-009](#adr-009-analytic-rubric-gates-and-defence) | Analytic rubric, gates and defence |
| [ADR-010](#adr-010-selectable-not-sequential-access) | Selectable, not sequential, access |
| [ADR-011](#adr-011-synthetic-data-policy-and-generator-determinism) | Synthetic data policy and generator determinism |
| [ADR-012](#adr-012-accessibility) | Accessibility |
| [ADR-013](#adr-013-integrity-through-verification-not-detection) | Integrity through verification, not detection |
| [ADR-014](#adr-014-generated-catalogue-and-indexes) | Generated catalogue and indexes |
| [ADR-015](#adr-015-signature-challenges-protocol) | Signature Challenges protocol |
| [ADR-016](#adr-016-assessment-lifecycle-and-versioning) | Assessment lifecycle and versioning |

---

## ADR-001: Three independent subtracks with per-subtrack placement

**Context.** The Intelligence Track covers work that industry now treats as distinct roles. Microsoft retired DP-100 and AI-102 in 2026 and re-split the space into AI-300 (MLOps and GenAIOps engineering) and AI-103 (AI apps and agents development). Huyen separates ML engineering (training traditional models) from AI engineering (building on foundation models). Data Science remains the analytical, inferential and communicative discipline (ACM DS 2021; O*NET 15-2051). Members' strengths differ across these areas, and project teams need to know them separately.

**Decision.** Three subtracks: **Data Science (DS)**, **Machine Learning Engineering (ML)** and **AI Engineering (AI)**, defined in [shared/units.yaml](../../shared/units.yaml). Placement is recorded **independently per subtrack**: a member can be Tier 1 in DS, Tier 2 in ML and Tier 3 in AI. Placement in one subtrack implies nothing about another. Contested topics are assigned to an owner by the question asked ([report §6](RESEARCH_AND_STANDARDS_REPORT.md#6-overlaps-and-distinctions-between-the-three-subtracks)).

**Alternatives.**
- *One combined "AI/ML" track with one tier.* Simple, but hides real differences and pushes data scientists towards deployment work that is not their discipline.
- *Two subtracks (data science and ML/AI).* Mirrors older curricula, but does not reflect the 2026 split between model operations and application building.
- *Many narrow specialisations (CV, NLP, MLOps...).* Too many placements for volunteer assessors to maintain.

**Consequences.**
- Each subtrack has its own identity, unit set and competency framework ([competency framework](../competency-framework.md)).
- Overlap areas (evaluation, time series, fairness, serving, GenAIOps) need explicit boundary rules, which reviewers check.
- Cross-disciplinary work needs its own collection (ADR-006) so that it does not blur subtrack evidence.

---

## ADR-002: Three qualitatively different tiers

**Context.** The legacy Novice/Intermediate/Pro bank scaled task *size*, producing a cliff from weekend tasks to multi-month products, with no measurement scale ([legacy audit](LEGACY_REPOSITORY_AUDIT.md#1-executive-summary)). Industry certification levels give useful anchors: AWS AIF-C01 "uses but does not build"; AWS MLA-C01 is associate level and lists end-to-end design, strategy, multi-domain depth and quantisation as out of scope.

**Decision.** Three tiers that ask different questions ([tier definitions](../tier-definitions.md)):
- **Tier 1, Foundation and Technical Fluency:** a correct, explained, reproducible solution to a well-specified problem.
- **Tier 2, Applied Engineering and Independent Problem-Solving:** method choice, comparison against a baseline and justified evaluation on a partially specified problem.
- **Tier 3, Advanced Engineering, Research and System Design:** framing, research-informed methodology, ablations and defended trade-offs on an ambiguous problem.

Calibration: Tier 1 sits above AIF-C01; Tier 2 is roughly MLA-C01 breadth with coding and a defence; MLA-C01's out-of-scope list marks Tier 3. SOLO targets: multistructural→relational, relational, extended abstract.

**Alternatives.**
- *Size-scaled levels.* Rejected: size measures stamina, not competence.
- *Five or more levels.* Finer, but volunteer assessors could not separate them reliably.
- *Two levels.* Too coarse to separate "can apply" from "can research and design".

**Consequences.**
- Authors must make a Tier 2 assessment different in *kind* from Tier 1 ([authoring guide §1.2](../contributing/AUTHORING_GUIDE.md#12-tier-fit)).
- Within-tier variation is captured by six difficulty dimensions (ADR-007), not by more tiers.
- Boundary cases are inevitable, which is one reason Tiers 2 and 3 need two qualifying outcomes ([placement framework §3](../placement-framework.md#3-tier-placement)).

---

## ADR-003: The unit architecture

**Context.** The original proposal had 43 units (DS-01..13, ML-01..15, AI-01..15). Some proposed units assessed components rather than competencies (a vector-database unit, a concepts-only unit), some split one competency progression across several units (MLOps and monitoring; production cost and reliability; research and its reporting), and the evidence showed gaps (responsible ML, recommenders, model adaptation).

**Decision.** Adopt **39 units**, recorded in [shared/units.yaml](../../shared/units.yaml), the single source of truth: **DS-01..12, ML-01..14, AI-01..13**. Each unit has planned targets per tier (232 unit assessments in total) and a `tier_notes` explanation where a tier is reduced or not offered. Principal changes:
- DS-11 and DS-13 merged into **DS-12** Applied Research and Reproducible Communication.
- The stand-alone ensembles unit folded into **ML-02** Supervised Learning and Ensembles.
- ML-14 and ML-15 merged into **ML-13** ML Pipelines, MLOps and Monitoring, following the Google and Microsoft maturity models.
- **ML-10** Recommender and Ranking Systems and **ML-14** Responsible ML added.
- AI-02 (concepts) merged into **AI-01**; AI-07 (vector databases) merged into **AI-05**; AI-14 and AI-15 merged into **AI-13**.
- **AI-12** Model Adaptation added.
- Four cells not offered: DS-01 T3, ML-11 T1, AI-01 T3, AI-12 T1 (reasons in [report §5.3](RESEARCH_AND_STANDARDS_REPORT.md#53-cells-not-offered-and-cells-with-a-single-assessment)).

**Alternatives.**
- *Keep the original 43 units.* More granular, but with thin units that could not support three different assessments.
- *About 20 broad units.* Less authoring overhead, but unfocused assessments and unverifiable coverage.
- *Merge the DS-10/ML-09 time-series pair.* Considered; rejected because the two units ask different questions.

**Consequences.**
- The validator rejects an assessment in a target-zero cell and checks that each unit belongs to its subtrack.
- Unit codes are stable. Adding a unit requires a new ADR and an entry in `units.yaml` first ([maintenance guide §6](../contributing/maintenance.md#6-adding-new-assessments)).
- Coverage can be measured: the generated coverage matrix compares planned with built (ADR-014).

---

## ADR-004: The standard assessment specification

**Context.** Legacy tasks fixed no dataset, contract, acceptance test or rubric, so submissions to the same task were not comparable. Benchmark courses combine a precise specification, an autograded core, written reasoning and an open extension (principles P1–P6 in the [benchmarks](ELITE_EDUCATIONAL_BENCHMARKS.md#3-cross-cutting-synthesis-clbg-design-principles)).

**Decision.** Every assessment README has these level-2 sections, in order: **A** Identification, **B** Problem Statement, **C** Objectives, **D** Technical Requirements, **E** Dataset and Resources, **F** Deliverables, **G** Acceptance Criteria, **H** Evaluation Rubric, **I** Submission Instructions, **J** Extension Challenges, **K** Assessment Integrity, and **Pedagogical Design** (answers to the eight design questions). The specification is defined in the [authoring guide §3](../contributing/AUTHORING_GUIDE.md#3-readme-specification) and enforced by `tools/assessment-validator/validate.py`.

**Alternatives.**
- *Free-form briefs.* Fast to write, impossible to compare or validate.
- *A minimal template (task, data, rubric).* Leaves out integrity rules, objectives and pedagogy, which is where quality problems hide.
- *Copy one university's format.* Not designed for a volunteer-run community without course credit.

**Consequences.**
- Members always know where to find requirements, criteria and integrity rules.
- Mandatory requirements, numbered acceptance criteria with justified thresholds, and section K defence plans make marking consistent.
- Authoring cost rises (1,500–4,000 words per README), mitigated by templates and the reference example DS-T1-006.

---

## ADR-005: Two repositories

**Context.** The legacy bank took submissions as pull requests on a public repository, so every candidate could read earlier solutions, and a completed solution was merged into a starter. Hidden tests and marking guides lose their value once public.

**Decision.** Two repositories:
- **Public member repository** (`clbg-intelligence-assessments`): specifications, metadata, public rubrics, starters without solutions, public data, contract and sample requirement tests, policies, tools and the generated catalogue.
- **Private assessor kit** (`clbg-intelligence-assessor-kit`): per assessment, `solutions/<ID>/` with `MARKING_GUIDE.md` (including a defence script and rotation procedure), `reference/`, `hidden_tests/` and, where it would reveal answers, `generator/`.

Members submit from their own repositories named `clbg-<ID>-<github-username>`, not by pull request to the public repository.

**Alternatives.**
- *One public repository.* Exposes answers.
- *One private repository.* Members could not see specifications or contribute.
- *Private branches or encrypted files in one repository.* Easy to leak by mistake and awkward for volunteers.

**Consequences.**
- Access to the kit is limited to assessors and maintainers. Leaks follow the rotation procedure ([maintenance guide §5](../contributing/maintenance.md#5-when-confidential-material-leaks)).
- Kit CI checks that requirement tests fail on the starter and pass on the reference.
- The two repositories must be kept in step; IDs (ADR-006) are the join key.

---

## ADR-006: ID scheme and pre-allocation

**Context.** Many authors write assessments in parallel. Placement records, the kit and the catalogue all refer to assessments by ID, so IDs must be unique, stable and meaningful.

**Decision.** Four ID patterns, enforced by [assessment.schema.json](../../shared/schemas/assessment.schema.json):

| Collection | Pattern | Example | Location |
|---|---|---|---|
| Unit assessment | `XX-TN-NNN` (XX = DS, ML or AI; N = tier) | `DS-T1-006` | `assessments/<subtrack>/tier-N/units/<UNIT>-<slug>/` |
| Capstone | `XX-CAP-TN-NN` | `ML-CAP-T3-01` | `assessments/<subtrack>/capstones/` |
| Cross-disciplinary | `XD-TN-NNN` (unit XD-FND, XD-INT or XD-ADV) | `XD-T2-001` | `cross-disciplinary/<foundations / integrated-challenges / advanced-challenges>/` |
| Signature Challenge | `SIG-CAT-NN` (CAT = INT, DATA, ML, AIE, RES, SYS, GRAND) | `SIG-RES-01` | `signature-challenges/<category>/` |

Unit-assessment IDs are **pre-allocated** per unit and tier in [shared/id-allocation.md](../../shared/id-allocation.md). New IDs are appended after the highest number used for that subtrack and tier, in the same pull request. **IDs are never reused**, including after retirement. Folders are `<ID>-<kebab-case-slug>`.

**Alternatives.**
- *IDs encoding the unit (e.g. DS-03-T1-01).* Breaks if a unit is renumbered; IDs must outlive unit changes.
- *Sequential global numbers.* Unique, but carries no subtrack or tier information.
- *Allocate on merge.* Causes collisions between parallel authors.

**Consequences.**
- An ID tells a reader the subtrack and tier at a glance.
- Retired IDs leave gaps, which is intended: historical placement records stay unambiguous.
- The validator checks that IDs, folders, collection, subtrack and tier agree.

---

## ADR-007: Metadata schema and six-dimensional difficulty

**Context.** "Difficulty" is not one thing: a project can be mathematically demanding without heavy infrastructure. Members need to filter assessments by compute and time, and tools need machine-readable fields.

**Decision.** Every assessment has a `metadata.yaml` validated against [assessment.schema.json](../../shared/schemas/assessment.schema.json) (template: [metadata.template.yaml](../../shared/templates/metadata.template.yaml)). Required fields include ID, version, status, dates, collection, subtrack, tier, unit, format, domains, technologies, prerequisites, at least three competencies, estimated hours, compute (GPU, internet, paid API, minimum RAM, free alternative), collaboration, datasets and resources. **Difficulty** is rated 1–5 on six independent dimensions: technical, mathematical, research, engineering, ambiguity and resources, with calibration ranges per tier ([tier definitions §5](../tier-definitions.md#5-multi-dimensional-difficulty)).

**Alternatives.**
- *A single 1–10 difficulty score.* Easy, but uninformative and contested.
- *Free-text metadata.* Cannot be validated or aggregated.
- *Front matter inside README.* Mixes data and prose; harder to validate.

**Consequences.**
- The catalogue can filter and the validator can enforce rules (for example, a required GPU or optional paid API needs a `free_alternative`).
- Authors must rate honestly; reviewers check ratings against the calibration ranges.
- Schema changes are breaking changes and need an ADR.

---

## ADR-008: Three-layer test design

**Context.** Benchmark courses give public sanity tests and score with hidden tests (P2), and treat the autograder as evidence rather than the verdict (P3). Hard-coded answers and tuning to visible tests must fail.

**Decision.** Three layers:

| Layer | File | Runs | Must |
|---|---|---|---|
| **Contract** | `tests/test_contract.py`, marker `contract` | Public CI on the unmodified starter | Pass on the starter. Checks data checksums, schemas, API signatures and generator determinism. |
| **Requirement** | `tests/test_requirements.py` | Member's machine; kit CI against the reference | Fail on the starter and pass on the reference. A *sample* of the requirements. |
| **Hidden** | `solutions/<ID>/hidden_tests/` in the kit | Assessor only | Test acceptance criteria on held-out or re-seeded data. |

`conftest.py` locates the code under test via `$CLBG_SUBMISSION_DIR`, then the repository root, then `starter/` ([authoring guide §6.2](../contributing/AUTHORING_GUIDE.md#62-test-conventions)).

**Alternatives.**
- *Public tests only.* Members tune to them, and hard-coding passes.
- *Hidden tests only.* Members get no fast feedback and cannot check the contract.
- *No automated tests.* Shifts all correctness checking to assessors.

**Consequences.**
- Public CI stays green and cheap; correctness evidence remains confidential.
- Every code-based assessment needs a reference solution in the kit.
- Tests are evidence for the rubric, not the outcome (ADR-009).

---

## ADR-009: Analytic rubric, gates and defence

**Context.** Holistic rubrics are quick but "not diagnostic"; analytic rubrics give more consistent scoring (University of Hawaiʻi at Mānoa; Carnegie Mellon). With capable AI tools freely available, an excellent artefact no longer proves understanding. NDPA s.37 limits decisions based solely on automated processing.

**Decision.** Every assessment has a **100-point analytic rubric** (default weights 10/20/15/15/15/10/10/5 across eight dimensions, adaptable but always totalling 100), four performance levels and one line of evidence per dimension. **Pass/fail gates** (integrity, reproducibility, defence, and assessment-specific gates such as privacy or safety) override the score. A **technical defence** (5–10, 10–20 or 20–40 minutes by tier) is required for every outcome above N. Outcomes are M, M−, R or N. Reliability comes from calibration, blind double marking (Tier 3, boundary scores, appeals, a 10% sample) and moderation ([evaluation framework](../evaluation-framework.md)).

**Alternatives.**
- *Holistic grades.* Inconsistent across volunteers.
- *Automated scores only.* Cannot judge reasoning, and conflicts with NDPA s.37 safeguards.
- *Leaderboard rank.* Rewards tuning over validity (ADR-015).

**Consequences.**
- Placement never rests on a single number.
- Assessors need training and calibration time each cohort.
- Rubrics with persistent disagreement are rewritten at moderation.

---

## ADR-010: Selectable, not sequential, access

**Context.** Members arrive with very different backgrounds. Forcing everyone through Tier 1 wastes experienced members' time, and gating by prerequisites makes the system bureaucratic.

**Decision.** Members choose freely: **subtrack → tier → unit → assessment**, in any order ([placement framework §1](../placement-framework.md#1-principles)). Prerequisites are advisory. A member may attempt Tier 2 or 3 directly; if the outcome falls short, the assessor may record lower-tier competence using the lower tier's descriptors. At most two attempts are in progress at once ([assessment policy §3](../assessment-policy.md#3-eligibility-and-choice)).

**Alternatives.**
- *Strict sequence (T1 before T2 before T3).* Predictable, but slow and discouraging for strong members.
- *An entry exam that assigns a starting tier.* A single high-stakes score, contrary to ADR-009.

**Consequences.**
- Members are never penalised for aiming high.
- A non-graded self-check in the [member handbook](../member-handbook.md) helps members choose.
- Assessors need clear lower-tier descriptors, supplied by the [competency framework](../competency-framework.md).

---

## ADR-011: Synthetic data policy and generator determinism

**Context.** NDPA 2023 and GAID 2025 restrict personal and sensitive data; GAID Art. 28(3)(m) makes a filed DPIA mandatory for processing student records. Real datasets carry licence and availability risk. Forensic assessments need planted defects whose truth is known.

**Decision.**
- Prefer **verified public datasets** from the dataset registry, with licence recorded, or **synthetic data**.
- Sensitive domains (health, finance, biometrics) use synthetic or properly licensed de-identified data.
- Synthetic generators run as `python <generator> --out DIR --seed INT`, are **byte-for-byte deterministic** for a fixed seed (checked by `tools/dataset-validator/validate_datasets.py`), create only fictional people (using the reserved `example.ng` domain), and inject defects only where they serve the learning objectives.
- Where a generator would reveal answers, it lives in the kit; the generated data is committed publicly with a checksum and `generator_in_assessor_kit: true`.
- No real member data appears in any assessment.

**Alternatives.**
- *Real personal data with consent.* Legally heavy for a student community and unnecessary for learning.
- *Member-sourced data only.* Incomparable submissions and uncontrolled privacy risk.
- *Non-deterministic generators.* Make reproduction and hidden-test re-seeding unreliable.

**Consequences.**
- Hidden tests can re-seed data so hard-coded answers fail.
- Synthetic data can lack the messiness of reality; authors must design defects carefully and say what is synthetic.
- Leaks are handled by regenerating with a new seed (ADR-016).

---

## ADR-012: Accessibility

**Context.** Members work on laptops with 4–8 GB of RAM, with unreliable power and connectivity, and without budgets for GPUs or paid APIs. Benchmarks warn against heavy GPU dependence.

**Decision.** **CPU first**: every assessment is completable on a 4–8 GB laptop or a free tier (Google Colab or Kaggle notebooks) with a stated path. **No required paid APIs**: hosted LLMs are optional, with a local alternative (for example Ollama or a small Hugging Face model) and a deterministic **mock** on which the tests run. Contract tests never need the network. Metadata records compute needs and the free alternative ([authoring guide §1.4](../contributing/AUTHORING_GUIDE.md#14-accessibility-rules)).

**Alternatives.**
- *Standardise on one cloud provider.* Excludes members without accounts or cards, and ties the track to a vendor.
- *Provide shared GPUs.* Unsustainable for a volunteer community.

**Consequences.**
- Tier 3 work is scoped to CPU scale (for example small models, distillation studies, PEFT on small models).
- Some frontier behaviours cannot be fully observed locally; assessments focus on engineering judgement that transfers.
- Mocks must be maintained as provider APIs change (annual review).

---

## ADR-013: Integrity through verification, not detection

**Context.** AI coding assistants are normal professional tools, and AI-text detectors are unreliable and unfair. Benchmarks combine format-specific AI rules, disclosure and oral checks (P7–P9).

**Decision.** **Disclosure, not prohibition.** Every submission includes `AI_USE_AND_SOURCES.md`. Understanding is **verified** through repository history, clean-environment reproduction, hidden tests, code walkthroughs, tracing, unseen live modification, live debugging and design questioning. CLBG **never uses plagiarism or AI-text detectors as evidence**. Section K of each assessment can set stricter rules. Concerns follow a proportionate, documented process ([assessment integrity](../assessment-integrity.md)).

**Alternatives.**
- *A blanket ban on AI tools.* Unenforceable and misaligned with AI-engineering practice.
- *Unrestricted AI with no verification.* Cannot evidence individual competence.
- *Detector-based policing.* Unreliable and unfair to members writing in a second language.

**Consequences.**
- The defence is central and costs assessor time.
- Members learn to use tools openly and verify their output.
- A single "final" commit is not proof of misconduct, but invites deeper questioning.

---

## ADR-014: Generated catalogue and indexes

**Context.** With 232 planned unit assessments plus capstones, cross-disciplinary and Signature Challenges, hand-maintained indexes would drift out of date.

**Decision.** `tools/catalogue-generator/build_catalogue.py` generates, from metadata, `CATALOGUE.md`, `catalogue.json`, `docs/catalogue/` (coverage matrix, by format, by domain), the tier and unit landing pages, capstone indexes and the blocks between `CATALOGUE:START/END` markers. CI runs it with `--check` and fails if anything is stale. Generated files are never edited by hand.

**Alternatives.**
- *Hand-written indexes.* Drift quickly.
- *A separate website.* More infrastructure than a student community can maintain.

**Consequences.**
- Metadata quality determines catalogue quality, which is another reason for the schema (ADR-007).
- The coverage matrix shows planned versus built per unit and tier, guiding authoring.
- Contributors must run the generator before opening a pull request.

---

## ADR-015: Signature Challenges protocol

**Context.** Competitions motivate members and showcase CLBG, but public leaderboards can be overfitted by repeated queries (Hardt 2015; Blum and Hardt 2015), even if the effect in aggregate is smaller than feared (Roelofs et al. 2019). Leakage errors are widespread in ML-based research (Kapoor and Narayanan). A single metric rewards tuning over validity.

**Decision.** Signature Challenges (`SIG-CAT-NN`, in seven categories: intelligence, data, machine learning, AI engineering, research, systems and optimisation, grand integrated) follow the shared evaluation protocol in [signature-challenges/README.md](../../signature-challenges/README.md):
- **Rigour-weighted scoring.** Each challenge publishes its weights, typically 35% performance on the hidden evaluation, 25% validity and rigour (baselines, ablations, uncertainty, absence of leakage), 15% reproducibility, 15% creativity and insight, and 10% communication.
- **No single-metric leaderboards.** Performance is **banded rather than ranked to the decimal**: results within a confidence interval of the best count as tied. Awards recognise best rigour, best insight and best negative result as well as best performance.
- **Holdout discipline.** Final evaluation uses hidden data that participants never see, rotated each edition, with at most three submissions per team to the hidden evaluation.
- **Reproducibility gate.** Organisers rerun submissions; results they cannot reproduce are not ranked. Leakage traps are planted where appropriate.
- **Defence and double marking.** When a challenge is used as placement evidence it is always double-marked, with two assessors at the defence ([moderation](../../assessment-operations/moderation/README.md)).
- A research-category Signature Challenge with outcome M counts towards Tier 3 placement ([placement framework §3](../placement-framework.md#3-tier-placement)).
- Signature Challenges are the only CLBG assessments with a competitive element ([assessment policy §2](../assessment-policy.md#2-purpose-of-assessment)).

**Alternatives.**
- *Kaggle-style public leaderboard.* Motivating, but rewards adaptive overfitting.
- *No competitions at all.* Loses motivation and visibility.
- *Ladder-style thresholded leaderboard only.* Mitigates overfitting but still scores a single metric.

**Consequences.**
- A well-evidenced negative result can outscore a high but unvalidated number.
- Challenges cost more to run (reproduction, double marking).
- Each challenge states its own window, rules and holdout policy.

---

## ADR-016: Assessment lifecycle and versioning

**Context.** Assessments break (dataset links, API changes), leak, or become outdated. Members must be assessed on a stable version, and placement records must stay interpretable for years.

**Decision.**
- **Status lifecycle:** `draft` → `reviewed` (author checks pass and quality scorecard ≥ 32/40) → `approved` (named reviewer sign-off; Tier 3 needs two) → `retired`. Only `reviewed` or `approved` assessments may be attempted.
- **Semantic versioning:** patch for clarifications, minor for dataset rotation, new optional extensions or justified threshold changes, major for changed core requirements. Every change is logged in `changelog`.
- **Registration fixes the version** the member is assessed on.
- **Reviews:** at `next_review`, or earlier on extreme pass rates (below 20% or above 95% over at least 10 attempts), persistent rater disagreement, broken resources or member reports.
- **Leaks:** rotate (new seed, new hidden cases, new checksums, minor bump); retire if rotation cannot neutralise the leak.
- **Retirement:** `status: retired`, changelog entry with reason and successor ID, folder kept, ID never reused.

See the [maintenance guide §2](../contributing/maintenance.md#2-assessment-lifecycle).

**Alternatives.**
- *Edit in place without versions.* Members registered on an old version would be judged against a new one.
- *Delete retired assessments.* Breaks historical placement records.

**Consequences.**
- History stays auditable; records reference ID plus version.
- Maintainers have scheduled duties (semester reviews, annual AI-engineering refresh).
- The repository grows over time with retired material, which is acceptable.
