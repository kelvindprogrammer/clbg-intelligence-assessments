# DS-T3-001: The Dataset Worth Citing: A Provenance and Licence Audit of a Data Catalogue

> *A research lab's catalogue says everything is open. Prove which datasets can actually be used, reused and sold, and which ones are quietly laundering a licence.*

---

## A. Identification

| Field | Value |
|---|---|
| **Assessment ID** | `DS-T3-001` |
| **Title** | The Dataset Worth Citing: A Provenance and Licence Audit of a Data Catalogue |
| **Subtrack** | Data Science |
| **Tier** | 3: Advanced and Research-Informed |
| **Unit** | [DS-02: Data Acquisition and Sourcing](../README.md) |
| **Format** | Investigation (secondary: system-design) |
| **Difficulty** | Technical 3 · Mathematical 1 · Research 4 · Engineering 3 · Ambiguity 4 · Resources 1 (each out of 5) |
| **Estimated time** | 14-22 hours over 2 weeks |
| **Collaboration** | Individual |
| **Compute** | Any laptop with 4 GB RAM; no GPU; no network required (reading primary licence texts online is part of the work, but not of the tests) |
| **Recommended prerequisites** | Python (dataclasses, recursion or iterative graph traversal); having read at least one Creative Commons licence summary; comfort with `hashlib`. |
| **Skills developed** | Provenance graphs, licence compatibility, integrity auditing, citation practice, stating the limits of an automated legal-style check |
| **Technologies** | Python 3.10+ standard library, pytest |

---

## B. Problem Statement

A university research lab has built an internal **data catalogue** of 24 datasets: regional price surveys, rainfall gauge readings, clinic attendance counts and more. Several are original open datasets from agencies and NGOs, and the rest were **derived** from them by merging, cleaning or aggregating. The lab wants to publish the catalogue, sell a cleaned subset to a Lagos analytics start-up, and cite everything properly in a grant report.

The catalogue file says each dataset has a licence. It does not say whether those declarations are *true*. A derived dataset can only carry a licence its sources allow, and the catalogue was assembled by many hands over several years. Before anything leaves the building you must find out:

- Which datasets **can be used commercially**, and which cannot because a non-commercial source sits somewhere upstream?
- Which derived datasets **dropped a share-alike obligation** or **dropped attribution**?
- Which datasets mix two **incompatible** share-alike licences and therefore cannot be lawfully distributed as declared?
- Which sit on a **proprietary or unlicensed** source, whatever their own label says?
- Which files **no longer match** the checksum or row count the catalogue declares, so the thing being cited is not the thing that was licensed?
- Which provenance chains are **impossible**, because dataset A is derived from B and B from A?
- And for each dataset, what exactly must be credited?

This is a research-informed task. The tests encode a deliberately simplified licence model (§D.1), because tests need one answer. Reality is messier: licences differ in how they treat *facts*, *database rights*, *adaptations* and *collections*, and compatibility between licences is often one-way. Part of your assessment is stating, with primary-source evidence, where the simplified model is a safe approximation and where it would mislead a real publisher. Your tool must be honest about what it can decide and what it must refer to a human.

**Known facts.** Each catalogue entry has `id, title, publisher, declared_license, derived_from, file, sha256, rows, attribution`. `file` is a small CSV with a header row. `attribution` is the credit line the entry shows.

---

## C. Objectives

When you finish, you should be able to show that you can:

1. Model data provenance as a directed graph, detect cycles and compute transitive obligations.
2. Translate licence terms (attribution, share-alike, non-commercial, public-domain dedication) into propagation rules, and test the rules on constructed cases.
3. Detect licence laundering, incompatible mixes and unlicensed upstreams, and avoid cascading duplicate findings.
4. Verify data integrity against declared checksums and row counts.
5. Compile a correct credit list for any dataset in the catalogue.
6. Identify and argue where an automated licence model diverges from the underlying legal instruments, with citations to primary sources, and make a justified reuse decision.

---

## D. Technical Requirements

### D.1 The licence model the tests encode

Licences in the catalogue: `CC0-1.0`, `CC-BY-4.0`, `CC-BY-SA-4.0`, `CC-BY-NC-4.0`, `ODbL-1.0`, and `PROPRIETARY` (no reuse rights granted). A **root** dataset has no `derived_from`. A **derived** dataset has one or more parents.

1. A root's *effective licence* is its declared licence, except that `PROPRIETARY` is `BLOCKED` (nothing may be reused).
2. For a derived dataset, first compute the licence **required** by its parents' effective licences:
   - any parent `UNRESOLVED` (in a cycle) makes it `UNRESOLVED`; any `BLOCKED` parent makes it `BLOCKED`; any `CONFLICT` parent makes it `CONFLICT`;
   - otherwise: a non-commercial parent together with a share-alike parent (`CC-BY-SA-4.0` or `ODbL-1.0`), or two *different* share-alike parents, is a `CONFLICT`; else a non-commercial parent requires `CC-BY-NC-4.0`; else a share-alike parent requires that same licence; else a `CC-BY-4.0` parent requires at least `CC-BY-4.0`; else `CC0-1.0`.
   - A declared licence **satisfies** a requirement if: for `CC-BY-NC-4.0` and share-alike requirements it equals the requirement; for `CC-BY-4.0` it is any of `CC-BY-4.0`, `CC-BY-SA-4.0`, `CC-BY-NC-4.0`, `ODbL-1.0`; for `CC0-1.0` anything satisfies it.
   - If satisfied, the *effective licence* is the declared one (`BLOCKED` if the declared licence is `PROPRIETARY`). If not satisfied, it is the required licence.
3. `can_use(cat, id, "commercial")` is false for `CC-BY-NC-4.0` and for `BLOCKED`, `CONFLICT`, `UNRESOLVED`. `can_use(cat, id, "closed_derivative")` is false for share-alike licences and for `BLOCKED`, `CONFLICT`, `UNRESOLVED`. Any other purpose raises `ValueError`.
4. A dataset must credit the title of every direct parent whose effective licence is not `CC0-1.0`. `required_attribution` is the sorted list of titles of every **transitive** ancestor whose *declared* licence is not `CC0-1.0` (cycle members excluded).

### D.2 Mandatory requirements

| ID | Requirement |
|---|---|
| **R1** | `load_catalogue(root)` reads `<root>/catalogue.json` into the provided dataclasses (`derived_from` as a tuple). |
| **R2** | `effective_license(cat, id)` per §D.1, including `BLOCKED`, `CONFLICT` and `UNRESOLVED`. |
| **R3** | Licence findings in `audit`: `LICENSE_NC_STRIPPED`, `LICENSE_SA_VIOLATION`, `LICENSE_BY_STRIPPED` (declared licence does not satisfy the requirement), `LICENSE_CONFLICT`, `UPSTREAM_UNLICENSED` (a *direct* parent is a root with `PROPRIETARY`). Findings must **not cascade**: a dataset whose problem is inherited from a parent that already carries a finding gets no new finding of its own. |
| **R4** | Integrity findings: `CHECKSUM_MISMATCH` (SHA-256 of the file bytes differs from `sha256`), `ROW_COUNT_MISMATCH` (data rows differ from `rows`, header excluded). |
| **R5** | Provenance findings: `PROVENANCE_CYCLE` for every dataset on a cycle (no licence findings for cycle members or their descendants), and `MISSING_ATTRIBUTION` (a required parent title does not appear in `attribution`; cycle members are skipped). `audit` returns `Finding(dataset_id, code)` objects sorted by `(dataset_id, code)`. |
| **R6** | `can_use` per §D.1. |
| **R7** | `required_attribution` per §D.1. |
| **R8** | `python -m provenance_audit <catalogue_dir> --out findings.json` writes the findings as a JSON list of `{"dataset_id", "code"}`. |

### D.3 Research and design requirements

- `LICENCE_MODEL.md` (at most 1,200 words plus a table): for each of the six licences, summarise the obligations that matter to the model, **citing the primary legal text or official deed** (section numbers, not blog posts). Then list at least **four ways the simplified model in §D.1 can be wrong in practice**, for example: facts and data may not be copyrightable, so a licence may not bind; sui generis database rights in the EU/UK versus what Nigeria's Copyright Act 2022 says about compilations and databases (read it; do not assume); whether an aggregation is an "adaptation"; one-way compatibility, such as CC BY-SA 4.0 and the licences it declares compatible; how attribution must be given; how a user could remedy a violation. For each, state what your tool does about it (flag for human review, ignore, or add a finding) and why.
- Add at least **eight tests** in `tests/test_member_*.py`, including three constructed catalogues you wrote yourself (for example a diamond-shaped provenance, a self-loop, a chain of three derivations through an NC source).
- Write the audit so it is **not quadratic in the number of datasets** for the licence resolution (memoise), and does not recurse unboundedly on cyclic data.

### D.4 Privacy and responsibility

The catalogue is synthetic. For real catalogues, never fetch or redistribute data of unknown licence while auditing, and treat a licence audit as decision support, not legal advice. Under the NDPA 2023, a licence permitting reuse does not permit re-identification or reuse of personal data beyond its original purpose; add one paragraph to `REPORT.md` explaining how you would extend the audit for datasets containing personal data.

### D.5 Optional enhancements

Emit a machine-readable SBOM-style provenance record (for example CycloneDX or PROV-O) for one dataset; add a `--fix` mode that prints suggested corrected licences and attribution lines (never writing to the catalogue).

---

## E. Dataset and Resources

| Item | Details |
|---|---|
| **Catalogue** | [`resources/catalogue/`](resources/catalogue/): `catalogue.json` (24 entries) and `files/<id>.csv` (about 40 KB in total) |
| **Provenance** | **Synthetic**, from a deterministic CLBG generator (seed 2026). Dataset titles echo real survey genres; no real agency, dataset or licence grant is represented. |
| **Licence** | CC BY 4.0 (the catalogue itself, as an exercise), MIT (code) |
| **Integrity** | `catalogue.json` is checked by the contract test. The catalogue's `.gitattributes` disables line-ending conversion so checksums are stable. Do not edit the data files. |
| **Primary sources to read** | The Creative Commons legal codes and deeds for CC0 1.0, CC BY 4.0, CC BY-SA 4.0 and CC BY-NC 4.0; the Open Database Licence 1.0 text (opendatacommons.org); the Nigerian Copyright Act 2022 for its treatment of compilations and databases. You will need these for `LICENCE_MODEL.md`. |

**Known limitations.** Licences are named by SPDX-like identifiers with no versions beyond those listed. Everything is a CSV with a header row. No dates, no jurisdictions and no licence exceptions appear in the catalogue.

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
| 1 | `provenance_audit/` package | The executable audit |
| 2 | `tests/test_member_*.py` (≥ 8 tests, ≥ 3 constructed catalogues) | Evidence you test the semantics, not just the supplied data |
| 3 | `LICENCE_MODEL.md` | Research evidence and honest model limits |
| 4 | `REPORT.md` from the [template](submission-template/REPORT.md) | Findings, reuse decisions for three scenarios, citation lines, privacy paragraph |
| 5 | `AI_USE_AND_SOURCES.md` | Integrity declaration |
| 6 | A 10-minute live defence | Verifies understanding and judgement |

---

## G. Acceptance Criteria

Criteria marked ⚙ are checked by the public and hidden test suites. Criteria marked ✍ are checked by an assessor.

1. ⚙ Public tests: `effective_license`, each finding code, the sorted full findings list, `can_use`, `required_attribution` and the CLI match the expected results for the public catalogue.
2. ⚙ Hidden tests: exact agreement with the oracle on three re-seeded catalogues (different DAGs, licences and defects), and no findings for an unseen, fully compliant mini-catalogue.
3. ⚙ No cascading: a dataset whose only problem is inherited gets no finding of its own (checked through the exact-findings tests).
4. ⚙ The audit completes on a 2,000-dataset generated chain without hitting Python's recursion limit or taking more than a few seconds (member-supplied test).
5. ✍ `LICENCE_MODEL.md` cites section-level primary sources for each licence and lists at least four substantive divergences between the model and the law, each with a tool response.
6. ✍ `REPORT.md` gives a reuse decision for three scenarios (publish the catalogue; sell a subset commercially; build a closed derivative), naming the datasets that block each and the cheapest remedy.
7. ✍ `REPORT.md` shows the credit lines for two datasets, built from `required_attribution`, formatted as a real citation (creator, title, version or date, licence, location).

---

## H. Evaluation Rubric

The full rubric with performance levels is in **[rubric.md](rubric.md)**. Summary:

| Dimension | Points |
|---|---|
| Problem understanding and technical reasoning | 10 |
| Technical correctness | 25 |
| Implementation quality | 10 |
| Methodology and research | 20 |
| Testing and evaluation | 10 |
| Documentation and reproducibility | 10 |
| Critical thinking and limitations | 10 |
| Presentation and communication | 5 |
| **Total** | **100** |

The outcome depends on the score **and** the gates (passing defence, reproducible run, integrity declaration). See the [placement framework](../../../../../../docs/placement-framework.md).

---

## I. Submission Instructions

1. Create a **private** GitHub repository named `clbg-DS-T3-001-<your-github-username>` from this assessment's `starter/`, `tests/` and `resources/` folders and the `submission-template/` files.
2. Expected structure:
   ```text
   clbg-DS-T3-001-<username>/
   ├── provenance_audit/       # your package (from starter/)
   ├── tests/                  # provided tests + your own test_member_*.py
   ├── resources/              # unchanged (catalogue/ with .gitattributes)
   ├── LICENCE_MODEL.md        # your research-based licence model and where it diverges from the law
   ├── REPORT.md               # findings, reuse decisions, AI-use declaration
   └── AI_USE_AND_SOURCES.md
   ```
3. Commit as you work. Your commit history is evidence of authorship (see §K); a single "final" commit will be questioned at defence.
4. Add the CLBG assessor account as a read-only collaborator and file a submission issue using the **Assessment submission** template, with the repository URL and the exact commit SHA.
5. **Deadline:** `<<set by the cohort coordinator>>`. **Late policy:** [assessment policy](../../../../../../docs/assessment-policy.md#7-deadlines-extensions-and-late-work). General guidance: [submission guidelines](../../../../../../docs/submission-guidelines.md).

---

## J. Extension Challenges

Optional. They are recognised in feedback but never replace the core requirements.

1. Emit a PROV-O or CycloneDX provenance document for one dataset and validate it.
2. Implement a `--remedy` analysis giving the minimum set of declared-licence changes that would make the catalogue compliant.
3. Fetch two real datasets' licences from their official pages and run your audit on a mini-catalogue built from them, noting every divergence from the model.
4. Add a model of licence *versions* (BY 3.0 vs 4.0) and explain why it changes compatibility.

---

## K. Assessment Integrity

**AI tools are permitted** to explain concepts, suggest idioms or review your code. They may not do the assessment for you, and you must be able to explain and modify every line you submit.

- **Disclose** all AI assistance in `AI_USE_AND_SOURCES.md` (template in `submission-template/`): tool, purpose and an example prompt. Undisclosed use discovered at defence is an integrity breach; disclosed, reasonable use is not penalised.
- **Cite** adapted code and any papers or documentation you relied on, with links.
- **Collaboration:** discuss *general techniques* only. Do not share code, results or report text.
- **How understanding is verified.** At a 10-minute defence the assessor will (1) pick a derived dataset and ask you to explain its effective licence from the graph; (2) ask which statement in `LICENCE_MODEL.md` you are least sure of and what you would check; (3) set an unseen modification, such as adding a licence `CC-BY-ND-4.0` or making attribution transitive, to be implemented live with a test.

See [assessment integrity](../../../../../../docs/assessment-integrity.md).

---

## Pedagogical Design

| Question | Answer |
|---|---|
| **Knowledge needed** | Python graph traversal; what CC licences require; the idea that a derived work inherits obligations. |
| **New skill developed** | Auditing data provenance rigorously, and knowing the limits of automated compliance checks. |
| **Decisions the member must make** | How to avoid cascading findings; how to treat cycles; how to model efficiency and recursion; which divergences from the law matter; what to refer to a human. |
| **What must be investigated independently** | The primary licence texts, the position of facts and databases, one-way compatibility, citation norms. |
| **Why it is interesting** | Licence laundering is real and costly, and an automated audit that sounds confident is dangerous. The task forces the member to separate what the tool decides from what the law decides. |
| **Evidence of competence** | Exact oracle agreement on unseen catalogues, a robust (non-recursive-limit) implementation, and a research document that cites primary sources and reasons about limits. |
| **Misconceptions exposed** | "Open data means free for everything"; "a derived dataset can choose any licence"; "CC BY-SA and ODbL are compatible"; "a checksum was only for downloads"; "citing the portal is citing the data". |
| **Preparation for later work** | Leads to DS-12 research reproducibility, ML dataset documentation (datasheets), and AI-12 governance work on training-data provenance. |

---

<sub>Version 1.0.0 · Status: reviewed · Maintainer: CLBG Intelligence Track Assessment Committee · See [metadata.yaml](metadata.yaml) · Content licensed CC BY 4.0, code MIT.</sub>
