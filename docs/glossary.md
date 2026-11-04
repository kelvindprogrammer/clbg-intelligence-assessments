# Glossary

Terms used across the CLBG Intelligence Track repository, in alphabetical order. Where a term has a defining document, it is linked.

| Term | Meaning |
|---|---|
| **Ablation** | An experiment that removes or changes one component to measure its contribution. Expected in Tier 3 work. |
| **Acceptance criteria** | Section G of an assessment: numbered, objectively testable conditions, marked ⚙ (automated) or ✍ (manual), each numeric threshold justified. |
| **Agent** | A system in which a model directs its own process and tool use, as opposed to a workflow on predefined code paths (AI-06, AI-07). |
| **AI_USE_AND_SOURCES.md** | The mandatory disclosure file in every submission: tools used, what for, example prompts and how output was verified ([assessment integrity](assessment-integrity.md)). |
| **Analytic rubric** | A rubric that scores several dimensions separately. CLBG uses a 100-point analytic rubric ([evaluation framework](evaluation-framework.md#2-the-rubric)). |
| **Assessment-specific gate** | A pass/fail gate defined by one assessment, for example privacy, safety or licence compliance. |
| **Assessor kit** | The private repository holding marking guides, reference solutions, hidden tests and private generators ([ADR-005](research/architecture-decisions.md#adr-005-two-repositories)). |
| **Baseline** | A simple reference method that any proposed method must beat by a justified margin. |
| **Bloom's taxonomy (revised)** | Anderson and Krathwohl's framework of cognitive processes (remember to create) and knowledge types, used to write objectives ([competency framework §2](competency-framework.md#2-cognitive-level-by-tier-bloom-and-solo)). |
| **Calibration** | Assessors independently scoring exemplars and resolving differences before marking real work. Also: whether predicted probabilities match observed frequencies. |
| **Calibration exemplar** | A described Exemplary, Proficient or Developing submission used for calibration, especially where no single reference solution exists. |
| **Capstone** | An integrated project within one subtrack, ID `XX-CAP-TN-NN`, in `assessments/<subtrack>/capstones/`. |
| **Catalogue** | The generated index of all assessments (`CATALOGUE.md`, `catalogue.json`, `docs/catalogue/`). Never edited by hand ([ADR-014](research/architecture-decisions.md#adr-014-generated-catalogue-and-indexes)). |
| **Collection** | The metadata field that says whether an assessment is a unit assessment, capstone, cross-disciplinary assessment or Signature Challenge. |
| **Competency statement** | An observable behaviour expected at a unit and tier, cited as `<UNIT>.T<n>` ([competency framework](competency-framework.md)). |
| **Contract test** | A public test (`tests/test_contract.py`, marker `contract`) that must pass on the unmodified starter: checksums, schemas, signatures, generator determinism. |
| **Cooling-off period** | The wait (default 21 days) before retrying a different assessment in the same unit and tier after an N outcome. |
| **Cross-disciplinary assessment** | An assessment combining several subtracks, ID `XD-TN-NNN`, units XD-FND, XD-INT or XD-ADV. |
| **Data contract** | An agreed schema and set of quality rules between data producers and consumers, enforced by validation (DS-11). |
| **Datasheet** | Documentation of a dataset's motivation, composition, collection and recommended uses (Gebru et al.). |
| **Defence** | The live technical conversation in which a member traces, explains and modifies their work. Required for any outcome above N ([defence guide](../assessment-operations/oral-defense/technical-defence-guide.md)). |
| **Difficulty dimensions** | Six independent 1–5 ratings: technical, mathematical, research, engineering, ambiguity, resources ([tier definitions §5](tier-definitions.md#5-multi-dimensional-difficulty)). |
| **Double marking** | A second assessor marking blind to the first. Required for Tier 3, band-boundary scores, appeals and a 10% sample. |
| **DPIA** | Data Protection Impact Assessment, required for high-risk processing (NDPA s.28; GAID Art. 28 and Art. 43). |
| **Drift** | Change over time in input data (data drift) or in the input-output relationship (concept drift) that degrades a model. |
| **Eval (evaluation set)** | A curated set of inputs, including edge and adversarial cases, with graders, used to measure an AI system (AI-10). |
| **Format** | The kind of assessment: implementation, investigation, reverse-engineering, replication, comparative, optimization, system-design, debugging-forensics, open-ended or capstone. |
| **GAID 2025** | The NDPA General Application and Implementation Directive issued by the Nigeria Data Protection Commission. |
| **Gate** | A pass/fail check that overrides the rubric score: integrity, reproducibility, defence and any assessment-specific gate. |
| **GenAIOps** | Operations for generative AI systems: prompt lifecycle, retrieval tuning, output safety, evaluation gates and token-cost governance. |
| **Generator** | A deterministic script (`--out DIR --seed INT`) that produces synthetic data ([ADR-011](research/architecture-decisions.md#adr-011-synthetic-data-policy-and-generator-determinism)). |
| **Grace days** | Three days per academic session that a member may apply to any non-capstone deadline without asking. |
| **Groundedness** | The extent to which a generated answer is supported by the retrieved sources it cites (AI-05, AI-10). |
| **Hidden test** | An assessor-only test on held-out or re-seeded data, kept in the assessor kit. |
| **Holdout** | Data withheld from training and tuning, used once for final evaluation. |
| **Human-in-the-loop** | A design in which a person approves or reviews consequential actions or decisions. |
| **ID allocation** | The pre-assigned list of assessment IDs per unit and tier ([id-allocation.md](../shared/id-allocation.md)). |
| **Leakage** | Information from outside the training data (for example test data, the future or the target itself) entering model training, producing inflated results. |
| **LLM-as-judge** | Using a language model to grade outputs. Must be calibrated against human labels and checked for position and verbosity bias. |
| **Marking guide** | The confidential `MARKING_GUIDE.md` in the assessor kit: strong-work description, common mistakes, hidden-test instructions, defence script and rotation procedure. |
| **MCP (Model Context Protocol)** | An open protocol for connecting model applications (hosts and clients) to servers offering resources, prompts and tools. CLBG cites version 2026-07-28. |
| **Mock** | A deterministic stand-in for a model or service so tests run offline and free. |
| **Model card** | Documentation of a trained model's intended use, evaluation and disaggregated performance (Mitchell et al.). |
| **Moderation** | The end-of-cohort review of score distributions and disagreements, leading to rubric revisions. |
| **NDPA 2023** | The Nigeria Data Protection Act 2023 (Act No. 37). |
| **Outcome** | The result of one assessed submission: M (meets requirements), M− (meets with minor deficiencies), R (requires revision) or N (does not yet demonstrate competence) ([placement framework §2](placement-framework.md#2-assessment-outcomes)). |
| **OWASP LLM Top 10** | The 2025 list of the ten most critical risks for LLM applications, LLM01 Prompt Injection to LLM10 Unbounded Consumption. |
| **PEFT** | Parameter-efficient fine-tuning, for example LoRA, which trains a small number of added parameters (AI-12). |
| **Placement** | The recorded tier of a member in one subtrack, awarded on combined evidence. |
| **Placement record** | The private record of a member's attempts, outcomes and factor judgements. |
| **Prompt injection** | Input that causes a model to ignore its instructions. *Indirect* injection arrives through retrieved documents, tool results or images. |
| **RAG** | Retrieval-augmented generation: retrieving relevant documents and supplying them to a model to ground its answer. |
| **Reference solution** | A complete solution in the assessor kit that passes the requirement and hidden tests. |
| **REFORMS** | A 32-item checklist for ML-based science in eight sections, used for Tier 3 research work. |
| **Reproducibility gate** | The assessor's clean-environment rerun must reproduce the key results within stated tolerances. |
| **Requirement test** | A public sample test (`tests/test_requirements.py`) that fails on the starter and passes on the reference. |
| **Rotation** | Replacing leaked material: new seed, new hidden cases, new checksums and a minor version bump. |
| **Signature Challenge** | A flagship, rigour-weighted challenge, ID `SIG-CAT-NN`, with no single-metric leaderboard ([ADR-015](research/architecture-decisions.md#adr-015-signature-challenges-protocol)). |
| **Slice metrics** | Performance measured separately on data subgroups, to find hidden failures. |
| **SOLO taxonomy** | Biggs and Collis's levels of response structure (pre-structural to extended abstract), used for rubric descriptors. |
| **Standard specification** | The required README sections A–K plus Pedagogical Design ([ADR-004](research/architecture-decisions.md#adr-004-the-standard-assessment-specification)). |
| **Starter** | Scaffolding code without the solution; stubs raise `NotImplementedError("R<n>: …")`. |
| **Structured output** | Model output constrained to a schema. CLBG also requires semantic validation of the values. |
| **Subtrack** | One of Data Science, ML Engineering or AI Engineering. |
| **Synthetic data** | Generated data representing fictional people or events, used to avoid personal-data risk. |
| **Tier** | One of three qualitatively different levels of demonstrated competence ([tier definitions](tier-definitions.md)). |
| **Training-serving skew** | A difference in model performance between training and serving, caused by pipeline mismatch, data change or feedback loops. |
| **Unit** | A named area of competence within a subtrack, for example DS-03 ([units.yaml](../shared/units.yaml)). |
| **Unseen modification** | A small new requirement implemented live during the defence. |
| **Workflow** | A system that orchestrates models and tools through predefined code paths (AI-07). |
