# ScoreWise: Halving Loan Defaults with an Alternative-Data Credit Model

*Technical whitepaper, Q4 2025. ScoreWise Lending Ltd is a fictional company created for this assessment. Its figures are computed from the synthetic file `resources/data/loans.csv`.*

## Summary of findings

ScoreWise introduced a machine-learning credit-scoring model on 1 April 2025. Comparing the quarter before with the quarter after:

1. **The default rate fell from 12.3% to 6.1%, a reduction of 50% (Z-test p < 0.001).**
2. **The model is most effective for farmers**, among whom the default rate fell by 8.8 percentage points (p < 0.0001), the largest reduction of any occupation.
3. **For borrowers with a bureau risk score of 60 or higher the default rate fell by 35% (p = 0.028).** We identified 60 as the point where the model's advantage becomes statistically significant.
4. We recommend that lenders adopt the model across all products and that regulators recognise a 50% reduction in default risk when setting provisioning rules.

## Data and methods

*Cohorts.* The "before" cohort contains all loans originated by ScoreWise between 6 January and 31 March 2025 (1,200 loans). The "after" cohort contains all loans originated between 1 April and 30 June 2025 (1,200 loans), scored by the new model. Both are drawn from the same four regions and the same three occupational groups. Loan products and maturities (30, 60, 90 and 180 days) were the same in both quarters.

*Outcome.* A loan is counted as defaulted if it was not repaid within 30 days of its maturity date. The data cut-off is 30 September 2025. Default rates are computed over loans that had reached maturity by the cut-off; loans still running are excluded because their outcome is not yet known.

*Statistical tests.* Default rates are compared with a two-sample Z-test for proportions (pooled variance). For subgroup comparisons we examined every combination of the variables region, occupation, age band, amount band and risk band and report the most informative results. Risk-score thresholds were scanned between 30 and 90 to find where the model's effect is clearest.

## Results

| Cohort | Matured loans | Defaults | Default rate |
|---|---|---|---|
| Before (no model) | 1,200 | 148 | 12.3% |
| After (model) | 946 | 58 | 6.1% |

Occupation results (default-rate change, after minus before): farmers -8.8 points (p < 0.0001); traders and salaried workers smaller, not highlighted here.

## Conclusion

The model produces a statistically significant and economically large reduction in loan defaults. Because the improvement is significant overall and in most subgroups, we conclude that the model causes the reduction and that the effect is robust. Independent replication is unnecessary.
