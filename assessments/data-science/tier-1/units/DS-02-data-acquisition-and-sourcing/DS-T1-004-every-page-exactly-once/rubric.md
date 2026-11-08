# DS-T1-004 Evaluation Rubric (public)

This rubric is public so you know exactly how you'll be judged. Assessors also use a confidential marking guide with calibration examples, but it never adds criteria that aren't listed here.

## Weighted dimensions

| # | Dimension | Points | What the assessor looks for |
|---|---|---|---|
| 1 | Problem understanding and technical reasoning | 10 | You can explain each real API trap (HTTP-200 errors, XML default, string metadata, `null` gaps, republished vintages) and what your client does about it. The retry classification is argued from HTTP semantics, not copied. |
| 2 | Technical correctness | 25 | Public and hidden tests pass: every record exactly once on unseen page sizes, correct failure classification, bounded jittered backoff, Retry-After in both forms, one cache-bypassing restart on republish, and a byte-identical offline rebuild. |
| 3 | Implementation quality | 15 | One retry loop, not copies of it. Caching happens after successful parsing. No `time.sleep` or `random` calls hidden inside the client. Clear exceptions, type hints and small functions. |
| 4 | Methodology: failure analysis → design → evidence | 10 | The report links each observed API behaviour to a design decision and to a test that pins it. The live run is used to check the fixture's claims rather than assume them. |
| 5 | Testing and evaluation | 15 | At least 10 meaningful member tests, at least 3 new fault scenarios, no real sleeping or network access, and assertions on counts and provenance rather than just "no exception". |
| 6 | Documentation and reproducibility | 10 | The README runs first time. The cache and provenance log from the live run rebuild the CSV offline. The attribution and licence are stated correctly. |
| 7 | Critical thinking and limitations | 10 | The vintage comparison is honest, and the `fillna(0)` error is quantified. You also state what the client still cannot detect, for example a silent revision within one `lastupdated`. |
| 8 | Presentation and communication | 5 | A concise report that the research group's analysts could read, with tables rather than log dumps. |
| | **Total** | **100** | |

## Performance levels

| Level | Share of points | Descriptor |
|---|---|---|
| **Exemplary** | 90–100% | Goes beyond the spec with insight. For example: measures the thundering-herd effect of jitter, discovers and documents an API behaviour not listed in §B, or shows the provenance chain behind a single CSV cell. |
| **Proficient** | 70–89% | All requirements met and justified, with minor gaps in the tests or report that don't affect trust in the data. |
| **Developing** | 50–69% | The client works on the happy path, but some failure classes are mishandled (for example errors cached, or 404 retried), or provenance is incomplete. |
| **Beginning** | 0–49% | Missing or incorrect. For example: `null` becomes 0, retries are unbounded, or the tests sleep for real or need the internet. |

## Gates (pass/fail, independent of points)

1. **Integrity:** `AI_USE_AND_SOURCES.md` is present and consistent with the defence.
2. **Reproducibility:** the assessor's offline rebuild from your submitted cache reproduces `data/ecowas_electricity.csv` byte for byte.
3. **Defence:** you trace a provenance entry to its code path and implement the unseen modification with sound reasoning.
4. **Offline tests:** the test suite passes with the network disabled.

## Automatic deductions

| Issue | Deduction |
|---|---|
| A fixture file was modified (checksum mismatch) | Gate fail until corrected |
| `null` values converted to `0` anywhere in the pipeline | Up to −8 from dimension 2 |
| Tests call the real API or sleep for real | Up to −6 from dimension 5 |
| Missing or incorrect CC BY 4.0 attribution | −2 from dimension 6 |

Outcome bands and placement rules: [placement framework](../../../../../../docs/placement-framework.md).
