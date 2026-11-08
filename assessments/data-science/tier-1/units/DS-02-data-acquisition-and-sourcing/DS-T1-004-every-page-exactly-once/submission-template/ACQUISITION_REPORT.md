# Acquisition Report: DS-T1-004

**Member:** `<name>`  **Live run date:** `<YYYY-MM-DD>`  **Commit:** `<sha>`

> Limit: 1,200 words plus tables. Every number must be regenerable from `data/` with the code in your repository. Say which script or notebook produces each one.

## 1. What the API actually does
For each behaviour you relied on (error envelope, XML default, paging, metadata types, `null`s, `lastupdated`), give one line of evidence from your live run or from the fixtures.

| Behaviour | Evidence (URL or fixture, and what you saw) | Design decision | Test that pins it |
|---|---|---|---|
| | | | |

## 2. Retry classification
Give one sentence per status (408, 429, 500, 502, 503, 504) explaining why it is retryable. Then explain why 400, 403 and 404 are not, and why the HTTP-200 error envelope is not.

## 3. The live run
- Command(s) used:
- `lastupdated` seen live:
- Pages, requests, retries and cache hits (from `provenance.jsonl`):

## 4. Vintage comparison with the recorded fixture (2026-10-08)
| Country | Year | Fixture value | Live value | Difference |
|---|---|---|---|---|
| | | | | |

If you found no revisions, say so, and show the check.

## 5. Coverage and the cost of `fillna(0)`
- `null` count per country and indicator (total and rural):
- ECOWAS unweighted mean access for one year between 2000 and 2010, computed (a) correctly, ignoring missing values, and (b) with missing values set to 0:
- What this means for the briefing note in §B:

## 6. Limitations
What can your client still not detect or guarantee?

## 7. Attribution
World Bank, World Development Indicators, `<indicators>`, accessed `<date>`, CC BY 4.0.
