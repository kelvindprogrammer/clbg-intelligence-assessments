# DS-T2-001 Comparison Report

**Member:** `<name>`  **Commit:** `<sha>`

At most 2,500 words plus tables and figures.

## 1. Recommendation (one paragraph)

Which engine should the DisCo analytics team use on their 8 GB laptops, and in which regime (data size, memory budget, frequency of reruns) would you recommend something else?

## 2. What was compared

The four engines and any conversion step, in two or three sentences each: the design, and how each honours `memory_limit_mb`. How you established that they compute the same thing.

## 3. Benchmark protocol

Hardware, OS and library versions; dataset sizes; process isolation; repeats; what is timed; how peak RSS is measured; cache handling; and why these choices are fair.

## 4. Results

| Engine | Size | Median time (s) | Range (s) | Peak RSS (MB) | Within budget? |
|---|---|---|---|---|---|

Include conversion costs separately and amortised. Add one figure if it helps (time against rows, or time against memory).

## 5. Why the results look like this

A mechanistic explanation: parsing, string handling, hashing for distinct counts, parallelism, materialisation and spilling. Cite plans, profiles or experiments, not intuition.

## 6. Threats to validity

At least three, and what you did about each.

## 7. Did feeders deliver their band?

Compliance by band for the benchmark quarter, and the sensitivity analysis (40/50/60% thresholds; minimum reporting meters). In which direction do silent meters bias supply hours, and how confident are you in each band's result?

## 8. Responsible handling of real AMI data (one paragraph)

NDPA 2023, aggregation, retention, access, and publication of per-feeder results.
