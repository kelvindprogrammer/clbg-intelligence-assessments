# Output schemas

## Canonical table (every parser, `load_all`, and `canonical.csv`)

One row per **source × market × commodity × week**.

| Column | Type | Rule |
|---|---|---|
| `source` | str | `NGM`, `CMB`, `APC` or `LSA` |
| `market_id` | str | A `market_id` from `reference/markets.csv` |
| `commodity_id` | str | A `commodity_id` from `reference/commodities.csv` |
| `week_start` | str | The ISO date (`YYYY-MM-DD`) of the **Monday** of the ISO week the observation belongs to |
| `price_ngn_per_kg` | float | Naira per kilogram, rounded to 2 decimal places; `NaN` if and only if `flag == "missing"` |
| `flag` | str | `ok`, `estimated` (LSA `E`) or `missing` (a not-observed value that is present in the file: NGM `null`, APC blank or `n.a.`, LSA `M`) |

An observation that is simply **absent** from a file (for example, CMB doesn't list unsurveyed items) produces no row. Rows are sorted by `source, market_id, commodity_id, week_start`.

## `reconciled.csv` (`reconcile`)

| Column | Meaning |
|---|---|
| `market_id`, `commodity_id`, `week_start` | The key |
| `n_sources` | Number of sources with a valid (non-missing) price |
| `median_price`, `min_price`, `max_price` | Over those sources |
| `spread_ratio` | `max_price / min_price` |

## `discrepancies.csv` (`discrepancies`)

`source, market_id, commodity_id, week_start, price_ngn_per_kg, median_price, rel_dev`, where `median_price` is the median of **all** valid prices for the key and `rel_dev = (price − median_price) / median_price`. Only keys with at least `min_sources` valid prices are considered.

## `stale_runs.csv` (`stale_runs`)

`source, market_id, commodity_id, first_week, last_week, run_length, price_ngn_per_kg`: one row per maximal run of at least `min_run` consecutive valid observations (missing weeks are skipped, not counted) whose prices are identical to 2 decimal places.
