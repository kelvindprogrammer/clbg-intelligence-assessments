# REPORT: The Slow Meter Report (DS-T2-013)

**Member:** `<name / GitHub username>`  **Commit:** `<sha>`  **Date:** `<date>`

## 1. Why the baselines are slow
Quote `EXPLAIN QUERY PLAN` for two baselines and say what repeats per row.

## 2. My designs
For each of s1-s5: the technique, why it is equivalent (ties, empty days), steps before and after.

| Query | Baseline steps | Mine | Ratio | Technique |
|---|---|---|---|---|

## 3. Indexes
Each index, which queries use it (plan evidence), and its cost on insert.

## 4. Scaling experiment
Table for at least three sizes, interpretation, and one condition where your design stops being fast.

## 5. A case that breaks a wrong rewrite
Show the tie or empty-day rows and the wrong output of the plausible alternative.

## 6. Limits of the metric; privacy (2 sentences)

## 7. AI-use declaration
See `AI_USE_AND_SOURCES.md`. Summarise in two lines, or write "None".
