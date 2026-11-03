# Maintenance Guide

This guide lets future CLBG executives run the repository **without rebuilding anything**.

## 1. Roles

| Role | Responsibilities |
|---|---|
| **Track lead** | Owns this repository and the assessor kit. Chairs the Assessment Committee. Approves policy changes. |
| **Subtrack leads** (DS, MLE, AIE) | Own their subtrack's assessments: reviews, approvals, health monitoring, recruiting assessors. |
| **Cohort coordinator** | Registers attempts, assigns assessors, tracks deadlines, runs moderation logistics. |
| **Maintainers** | Merge PRs, keep CI green, run scheduled verification, rotate leaked materials. |

Hand over to the next set of executives with a 1-hour walkthrough of this file, the [authoring guide](AUTHORING_GUIDE.md) and the assessor kit's README. Transfer the GitHub admin roles, then update `CODEOWNERS`.

## 2. Assessment lifecycle

```text
 draft ──(author checks pass + quality scorecard ≥ 32/40)──▶ reviewed
 reviewed ──(named reviewer sign-off; Tier 3 needs 2 reviewers)──▶ approved
 approved/reviewed ──(obsolete, leaked beyond rotation, or superseded)──▶ retired
```

- **Versioning (semver):**
  - **patch** (1.0.**1**): typo, link fix, clarification with no change to the requirements;
  - **minor** (1.**1**.0): dataset rotation, new optional extension, a changed threshold with justification;
  - **major** (**2**.0.0): changed core requirements.
- Add every change to `changelog` in `metadata.yaml`. Members are assessed on the version they registered.
- **Retiring:** set `status: retired`, add a changelog entry with the reason and any successor ID, and leave the folder in place. IDs are **never reused**.

## 3. Scheduled tasks

| When | Task | How |
|---|---|---|
| Every PR | Validator, links, catalogue freshness, contract tests | CI (`.github/workflows/validate.yml`) |
| Monthly | External link check | CI scheduled workflow (`external-links.yml`) plus a manual triage of failures |
| Start of each semester | Re-verify the dataset registry entries older than 12 months: licence, availability, terms | `tools/dataset-validator/validate_datasets.py` lists the entries due, then follow the procedure in [DATASET_REGISTRY.md](../../shared/datasets/DATASET_REGISTRY.md) |
| Start of each semester | Review the assessments whose `next_review` has passed | `python tools/assessment-validator/validate.py --json`, and filter on `next_review` |
| Each cohort | Calibration, moderation, assessment health review | [moderation](../../assessment-operations/moderation/README.md) |
| Annually | Refresh the AI Engineering units' provider-specific details (APIs and model names change fast) | Subtrack lead review |

## 4. Keeping CI green

```bash
pip install -r requirements-ci.txt
python tools/assessment-validator/validate.py
python tools/catalogue-generator/build_catalogue.py --check
python tools/repository-checker/check_links.py
python tools/test-runner/run_tests.py
python tools/dataset-validator/validate_datasets.py
```

If `--check` reports a stale catalogue, run `build_catalogue.py` and commit the result. **Never hand-edit generated files**: `CATALOGUE.md`, `catalogue.json`, `docs/catalogue/*`, the tier and unit READMEs, and the blocks between `CATALOGUE:START/END`.

## 5. When confidential material leaks

1. Confirm what leaked: the reference solution, hidden tests or the marking guide.
2. **Rotate:**
   - regenerate the data with a new seed or variant;
   - change the hidden test cases;
   - update the public checksums and any example IDs;
   - bump the minor version.
   Each kit marking guide has a rotation section.
3. If rotation can't neutralise the leak, retire the assessment and write a successor.
4. Record the incident in the moderation record.

## 6. Adding new assessments

Follow the [authoring guide](AUTHORING_GUIDE.md). Take the next free ID for the subtrack and tier from [shared/id-allocation.md](../../shared/id-allocation.md) and update that file in the same PR. If you add a whole new unit, add it to `shared/units.yaml` first, along with an ADR in [architecture decisions](../research/architecture-decisions.md).
