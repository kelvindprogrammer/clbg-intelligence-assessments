# Agency file formats (as supplied by each agency)

This is everything the desk received from the four agencies about their own files. It is incomplete in places, as real documentation usually is. Where the file and this document disagree, the file is the evidence, and your report must say what you found.

## NGM: Northern Grain Monitor (`data/ngm_prices.json`)

- JSON object with `agency`, `currency`, `price_field`, `note` and `reports`.
- Each report has `market` (an NGM market label), `week_ending` (ISO date) and `items`.
- Each item has `commodity` (an NGM code), `unit` and `price_kobo` (an integer number of **kobo**, 1/100 naira, per `unit`; `null` if not observed).
- From the file's own note: weeks run Monday to Saturday and are labelled by their **last** day.

## CMB: Coastal Markets Bureau (`data/cmb_bulletin.xml`)

- Root `<PriceBulletin currency="NGN" dateFormat="DD/MM/YYYY">` containing `<Market name="...">` elements.
- Each `<Obs>` has `date` (the **Monday** that the survey week starts, DD/MM/YYYY), `item`, `uom`, `price` (naira per `uom`, formatted with thousands separators) and `revision`.
- CMB publishes corrections by appending a new `<Obs>` with a higher `revision` number. The highest revision for a market, item and week is the bureau's current figure.
- Commodities not surveyed in a week are simply absent.

## APC: AgriPrice Cooperative (`data/apc_survey.xlsx`)

- One worksheet per month, plus a `Notes` sheet.
- On each month sheet: `A1` is a title, `A2` is the month, and `A3` states the unit as `Unit: NGN per <unit>`. Row 5 is the header: `Week commencing`, `Commodity`, then one column per market. Data starts on row 6.
- `Week commencing` is a date cell (a Monday). Prices are naira per the sheet's unit. A blank cell or `n.a.` means not observed.

## LSA: Legacy Statistical Archive (`data/lsa_extract.txt`)

Fixed-width text exported from a legacy system, layout version 3. Two header lines (starting `LSA ` and `MKT `), then one record per line, then one trailer line.

| Columns (1-based) | Width | Field | Notes |
|---|---|---|---|
| 1–6 | 6 | Market code | LSA's own 6-letter codes |
| 7–9 | 3 | Commodity code | Numeric, e.g. `101` |
| 10 | 1 | (space) | |
| 11–17 | 7 | Week | ISO 8601 week, `YYYYWww` |
| 18 | 1 | (space) | |
| 19–27 | 9 | Price | Naira per kg with **two implied decimal places**, zero-padded: `000065012` = ₦650.12 |
| 28 | 1 | (space) | |
| 29 | 1 | Quality flag | blank = observed, `E` = estimated by LSA, `M` = missing (the price field is then all zeros) |

Trailer: `TRAILER RECORDS=nnnnnn`, the number of data records in the file. Some tools strip trailing spaces, so a record with a blank flag may be only 28 characters long.

## Desk conversion table (`reference/units.csv`)

The desk has agreed fixed kilogram equivalents for each commodity and unit, including the *mudu*, a traditional measuring bowl whose weight depends on what it holds. Use these factors. Don't invent your own.
