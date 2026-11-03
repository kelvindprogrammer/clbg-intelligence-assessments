# Evaluation Framework

This framework explains **how evidence becomes an outcome**, and how CLBG keeps evaluation consistent across assessors, cohorts and subtracks.

## 1. Layers of evidence

```text
 ┌──────────────────────────┐   ┌──────────────────────┐   ┌───────────────────────┐
 │ 1. Automated evidence    │   │ 2. Expert review     │   │ 3. Technical defence  │
 │ public + hidden tests,   │ → │ rubric scoring with  │ → │ trace · explain ·     │
 │ reproduction run,        │   │ marking guide and    │   │ modify live · probe   │
 │ validators               │   │ calibration exemplars│   │                       │
 └──────────────────────────┘   └──────────────────────┘   └───────────────────────┘
                 \__________________________ | ___________________________/
                                   4. Gates + outcome band
                                             |
                                 5. Moderation (sampled / boundary)
                                             |
                                 6. Placement record update
```

1. **Automated evidence** is objective but narrow. It checks correctness on known and hidden data.
2. **Expert review** judges what tests can't: reasoning, methodology, code quality, communication.
3. **The defence** verifies that the evidence reflects the member's own understanding.

No layer is enough on its own, which is why outcomes need all three ([placement framework §2](placement-framework.md#2-assessment-outcomes)).

## 2. The rubric

Every assessment uses a 100-point **analytic rubric**, published in its `rubric.md`. The default dimensions and weights are:

| # | Dimension | Default weight | What it captures |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | Why the problem matters; what makes it hard; whether the member's choices follow from that |
| 2 | Technical correctness | 20 | Does it work, on the hidden cases too? Are methods applied correctly? |
| 3 | Implementation quality | 15 | Structure, readability, robustness, appropriate abstractions |
| 4 | Methodology and experimentation | 15 | Sound process: profiling, baselines, controlled comparisons, valid evaluation design |
| 5 | Testing and evaluation | 15 | Meaningful tests; correct metrics; honest evaluation |
| 6 | Documentation and reproducibility | 10 | Can someone else run it and get the same results? |
| 7 | Critical thinking and limitations | 10 | Threats to validity, failure modes, residual uncertainty |
| 8 | Presentation and communication | 5 | Clarity for the intended audience |

Assessments may adapt the weights. For example, a replication might weight methodology at 25, and a system-design challenge might weight architecture and trade-offs heavily. Any adaptation keeps the same 100-point scale, and every dimension has assessment-specific descriptors.

**Performance levels** inside each dimension:

| Level | Share of points |
|---|---|
| Exemplary | 90–100% |
| Proficient | 70–89% |
| Developing | 50–69% |
| Beginning | 0–49% |

Assessors award whole points and **must write one line of evidence per dimension**. A score with no evidence is invalid.

## 3. Gates

These are pass/fail and override the score:

1. **Integrity:** a declaration is present and consistent with the defence.
2. **Reproducibility:** the assessor's clean rerun reproduces the key results within stated tolerances.
3. **Defence:** satisfactory understanding is shown.
4. **Assessment-specific:** for example privacy (no personal data leaked), safety (agents can't take consequential actions without approval), or licence compliance.

## 4. Reliability: calibration and moderation

| Practice | When | How |
|---|---|---|
| **Assessor calibration** | Before each cohort, and for every new assessor | Each assessor independently scores 2–3 calibration exemplars, then the group compares and discusses differences larger than 5 points per dimension. See [moderation](../assessment-operations/moderation/README.md). |
| **Double marking** | All Tier 3 work; all band-boundary scores (±3 of 50, 65, 80); every appeal; a 10% random sample of everything else | A second assessor marks blind to the first. A total difference of 10 points or more goes to a third assessor. |
| **Moderation meeting** | End of each cohort | Review score distributions per assessment and per assessor, and investigate outliers. Revise rubrics or marking guides that cause disagreement. |
| **Inter-rater statistics** | Each cohort | Track the mean absolute difference per dimension for double-marked work. The target is ≤ 1.5 points per dimension and ≤ 6 points total. Dimensions that keep missing the target need their descriptors rewritten. |

## 5. Interpreting numbers honestly

- **Metric thresholds** in acceptance criteria are always justified by the problem, never arbitrary. Assessors don't reward tiny metric gains won at the cost of validity, such as leakage, tuning on test data or cherry-picked seeds.
- **Rigour over leaderboard position.** In comparative and Signature challenges, a well-evidenced negative result can outscore a high but unvalidated number.
- **Uncertainty.** When results vary with seed or sample, members are expected to report the variation, and assessors check that they did.

## 6. Feedback standards

Feedback is recorded on the score sheet and returned within 10 working days. It must:

1. state the outcome and what drove it;
2. give **at least two specific strengths**, with evidence;
3. give the **most important deficiencies**, each with a concrete next step;
4. for R and N outcomes, list exactly what a resubmission or retry must show;
5. be respectful and about the work, not the person.

Templates: [scoring templates](../assessment-operations/scoring-templates/README.md).

## 7. Continuous improvement

Every assessment is reviewed at its `next_review` date, or earlier if:
- outcomes for it are extreme (pass rate below 20% or above 95% over at least 10 attempts);
- inter-rater disagreement on it is persistently above target;
- its resources break, for example a dataset link or an API change;
- members report ambiguity through the **Assessment feedback** issue template.

Revisions bump the version (see the [maintenance guide](contributing/maintenance.md)).
