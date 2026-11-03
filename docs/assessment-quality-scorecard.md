# Assessment Quality Scorecard

Every assessment is reviewed against this scorecard before its status moves from `draft` to `reviewed`, and again before `approved`. Paste the completed table into the pull request.

A technically correct but dull, repetitive or poorly designed assessment does **not** pass. Neither does a creative assessment with unclear requirements. Approval needs both rigour and engagement.

## Criteria

Score each criterion from 1 to 4: **1** inadequate · **2** weak · **3** good · **4** excellent.

| # | Criterion | The reviewer asks | Minimum to approve |
|---|---|---|---|
| 1 | **Educational value** | Does it assess the intended competency of its unit, and will the member learn something they couldn't fake? | 3 |
| 2 | **Originality and engagement** | Is there a twist, a tension or an open question? Would a member think "I want to solve this"? Is it distinct from every other assessment in the unit? | 3 |
| 3 | **Technical correctness** | Is everything technically correct: methods, metrics, claims, code, thresholds? | **4** |
| 4 | **Tier appropriateness** | Does the *kind* of competence required match the [tier definitions](tier-definitions.md)? Not just the size. | 3 |
| 5 | **Clarity of requirements** | Could two members read it and build things that the same tests can judge? Are mandatory and optional requirements separated? | 3 |
| 6 | **Realism** | Is the scenario credible, and not invented just to use a technology? | 3 |
| 7 | **Evaluation reliability** | Would two assessors score the same submission within ±5 points? Are the acceptance criteria objective and the thresholds justified? | 3 |
| 8 | **Resource accessibility** | Can it be completed on a student laptop or a free tier, with no required paid services? | 3 |
| 9 | **Documentation quality** | Is everything a member needs written down, and do all the links work? | 3 |
| 10 | **Reproducibility** | Do the data, starter and tests run from a clean environment, deterministically? | 3 |

## Approval rule

- **Every** criterion meets its minimum, **and** the total is **≥ 32/40**.
- **Tier 3 and Signature Challenges:** at least **two independent reviewers**, at least one of whom did not author or co-author the assessment. If their scores differ by more than 6 points in total, they meet and reconcile.
- **Any criterion scored 1** blocks approval, whatever the total.

## Review record

```markdown
| # | Criterion | Score | Notes |
|---|---|---|---|
| 1 | Educational value | | |
| 2 | Originality and engagement | | |
| 3 | Technical correctness | | |
| 4 | Tier appropriateness | | |
| 5 | Clarity of requirements | | |
| 6 | Realism | | |
| 7 | Evaluation reliability | | |
| 8 | Resource accessibility | | |
| 9 | Documentation quality | | |
| 10 | Reproducibility | | |
| | **Total** | /40 | |

Reviewer: ____  Date: ____  Decision: approve / revise / reject
```

## Red flags (automatic "revise")

- Any "the model should perform well" criterion, or a threshold with no justification.
- A starter that contains the solution, or tests that only check whether files exist.
- A required GPU or paid API with no free path.
- Personal data that isn't synthetic or properly licensed.
- A near-duplicate of another assessment: same problem shape, different dataset.
