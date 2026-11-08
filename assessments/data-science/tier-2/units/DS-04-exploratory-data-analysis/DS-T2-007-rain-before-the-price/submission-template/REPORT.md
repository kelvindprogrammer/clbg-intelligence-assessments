# Rainfall and Food Prices: Exploration and Hypothesis Register

**Member:** `<name / GitHub username>`  **Submission commit:** `<sha>`  **Date:** `<date>`

> Limit: 2,500 words, excluding tables and figures. Audience: the head of a food-security analysis unit who reads statistics but does not do them daily.

## 1. Summary (no more than 200 words)
Which links you consider supported, which are exploratory, and what the unit should and should not do with them.

## 2. What the data looks like (R2)
Coverage and missingness (including whether it relates to price level), seasonality by zone, national co-movement, the 2022 rainfall excess. Figures.

## 3. Method and why (R1)
How you removed common shocks, built rainfall features, searched lags, obtained valid p-values, and controlled the false discovery rate. Tie each choice to section 2.

## 4. Does the method work? (R3)
Your simulator's design (briefly), and recall, FDR and lag accuracy for your method and the naive baseline over at least 5 simulated panels. Include the null-calibration result.

## 5. Baseline comparison on the real panel (R4)

| | Naive baseline | Your method |
|---|---|---|
| Pairs claimed | | |
| Shared claims | | |

At least two pairs the baseline claims and you reject, with evidence.

## 6. Sensitivity (R5)
Which claims survive at least two alternative choices?

## 7. The register
The supported and exploratory rows, with effects in interpretable units (for example "% price rise per standard deviation of deficit") and follow-ups.

## 8. Limitations and responsible use
Association versus causation, informative missingness, what the FDR guarantees, and the risk of acting on exploratory rows.

## 9. Reproduction
```bash
# exact commands that regenerate outputs/ and figures/
```
