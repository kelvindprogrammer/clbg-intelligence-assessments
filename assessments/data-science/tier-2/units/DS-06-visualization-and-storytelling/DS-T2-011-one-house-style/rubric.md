# DS-T2-011 Evaluation Rubric (public)

This rubric is public so you know exactly how you'll be judged. Assessors also use a confidential marking guide with calibration examples, but it never adds criteria that aren't listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | You can explain why CVD simulation is done in linear RGB, why ΔE formulas disagree for saturated colours, and why chart images (mostly white) break photographic hashes. |
| 2 | Technical correctness | 20 | Hidden suite: independent palette audit (ΔE2000 ≥ 10 under all three CVD types, contrast ≥ 3:1); WCAG and ΔE match independent formulas; CVD properties; regression rules on all five charts; palette consistency. |
| 3 | Implementation quality (API and engineering) | 20 | A coherent, typed, documented API; `theme()` leaks no state (including after exceptions); annotation helpers work on any chart; deterministic rendering; colour science implemented, not imported. |
| 4 | Methodology: comparisons against baselines | 15 | The three R10 comparisons: the palette vs tab10 and a published CVD-safe palette; your ΔE vs an alternative on ≥ 10 pairs; your signature vs a naive hash, with distances on all charts. |
| 5 | Testing and evaluation (incl. tolerance calibration) | 15 | At least 12 member tests including per-chart regression and theme-after-exception. The tolerance is chosen from measured benign and meaningful distances, with false-alarm and miss rates reported. |
| 6 | Documentation and reproducibility | 5 | The usage example runs. Baseline updates are separate commits with reasons. |
| 7 | Critical thinking and limitations | 10 | Says what the checks miss (anomalous trichromacy, print, low vision, screen readers) and how real-reader validation would be done ethically. |
| 8 | Presentation and communication | 5 | The report charts are clean and directly labelled, and the one-page style guide works for an analyst who hasn't read the code. |
| | **Total** | **100** | |

## Performance levels

| Level | Share of points | Descriptor |
|---|---|---|
| **Exemplary** | 90–100% | Exceeds the requirement with insight. For example, a severity sweep, a cross-version regression measurement, or a reader study. |
| **Proficient** | 70–89% | Fully meets the requirement with minor gaps. |
| **Developing** | 50–69% | Partly meets the requirement. For example, a tolerance picked without measurement, or comparisons that are qualitative only. |
| **Beginning** | 0–49% | Missing, incorrect or unexplained. For example: colour science imported from a library, or a palette that fails the organisational check. |

## Gates (pass/fail, independent of points)

1. **Integrity:** `AI_USE_AND_SOURCES.md` is present and consistent with the defence.
2. **Reproducibility:** tests pass and `build_report` reproduces the committed baselines within tolerance in a clean environment.
3. **Defence:** the member explains their CVD method and correctly predicts the outcome of an unseen perturbation.
4. **Organisational palette rule:** the palette passes the independent check (AC2).

## Automatic deductions

| Issue | Deduction |
|---|---|
| Colour science imported from a library in the package | Up to −10 from dimension 3 |
| `TOLERANCE` with no measured justification | Up to −6 from dimension 5 |
| Baselines regenerated in the same commit as an unexplained code change | Up to −3 from dimension 6 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
