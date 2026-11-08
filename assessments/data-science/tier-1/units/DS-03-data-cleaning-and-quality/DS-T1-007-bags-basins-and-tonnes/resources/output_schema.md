# DS-T1-007 Output Schema

All files are UTF-8 with a header row, `\n` line endings, and an empty string for null values.

## `harmonised.csv`

There is exactly **one row per input record**, sorted by `record_id`. No record is ever dropped.

| Column | Type | Rule |
|---|---|---|
| `record_id` | string | Copied from the input. |
| `crop` | enum | `maize`, `sorghum`, `cowpea`, `rice_paddy` (copied). |
| `quantity` | float (3 dp) or empty | `parse_quantity(harvest_qty)`. |
| `unit` | enum or empty | `normalize_unit(harvest_unit)`: one of `kg`, `tonne`, `bag_100`, `bag_50`, `basin`, `mudu`, `paint_bucket`. |
| `kg`, `kg_low`, `kg_high` | float (3 dp) or empty | From `to_kg`. Empty whenever the conversion is impossible. |
| `conversion_grade` | `A`, `B`, `C` or empty | The grade of the factor used. |
| `area_ha` | float (4 dp) or empty | `parse_area_ha(plot_area, area_unit)`, set empty if above 50 ha (sampling-frame limit). |
| `yield_kg_ha` | float (1 dp) or empty | `kg / area_ha` when both are known, otherwise empty. |
| `flags` | string | `;`-separated, alphabetically sorted subset of the flag vocabulary below. Empty if no flag applies. |
| `usable` | `True`/`False` | `True` exactly when `kg` and `area_ha` are known **and** the only flag (if any) is `zero_harvest`. |

### Flag vocabulary

| Flag | Raised when | Blocks `usable`? |
|---|---|---|
| `missing_quantity` | `harvest_qty` is a missing token | yes |
| `invalid_quantity` | `harvest_qty` is present but `parse_quantity` returns `None` | yes |
| `unknown_unit` | `normalize_unit` returns `None` | yes |
| `no_conversion_factor` | the unit is recognised but the table has no factor for this crop | yes |
| `missing_area` | `plot_area` is a missing token | yes |
| `invalid_area` | `plot_area` is present but cannot be parsed, is not positive, has an unrecognised unit, or exceeds 50 ha | yes |
| `domain_high` | `yield_kg_ha` exceeds the crop's `max_plausible_kg_ha` in `crop_limits.csv` | yes |
| `robust_outlier` | `mad_flags` (k = 3.5) on yields **within the same crop** returns `True` | yes |
| `zero_harvest` | `quantity == 0` (a reported crop failure) | **no** |

## `issues.csv`

One row per flag raised on a record, plus one `normalized_unit` row for every record whose raw `harvest_unit` string differs from its canonical code. Sorted by `record_id`, then `column`, then `issue_type`.

| Column | Type | Rule |
|---|---|---|
| `record_id` | string | The input record. |
| `column` | string | `harvest_qty`, `harvest_unit` or `plot_area`, or `*` for yield-level flags (`domain_high`, `robust_outlier`). |
| `issue_type` | string | A flag name from the vocabulary above, or `normalized_unit`. |
| `original_value` | string | The raw value, verbatim (empty for `*` rows). |
| `action` | string | A short description, e.g. `mapped 'kwano' -> 'basin'`, `kg not computed: no factor for rice_paddy/mudu`. |

## `totals.csv`

One row per (crop, scenario), for each of the four crops and for `ALL`. 20 rows in total.

| Column | Type | Rule |
|---|---|---|
| `crop` | string | A crop or `ALL`. |
| `scenario` | enum | See below. |
| `n_records` | int | Records contributing to the total. |
| `total_kg`, `total_kg_low`, `total_kg_high` | float (1 dp) | Sums of `kg`, `kg_low`, `kg_high` over contributing records. |

| Scenario | Contributing records and value |
|---|---|
| `unit_blind` | Every record with a parsed `quantity`; sums the raw quantity as if every unit were kg. Low = central = high. It exists to show how wrong a unit-blind total is. |
| `all_converted` | Every record with a known `kg`, regardless of flags. |
| `usable_only` | Records with `usable == True`. |
| `imputed` | Usable records with their own `kg`, **plus** every non-usable record that has a known `area_ha`, valued at *its crop's median usable yield × `area_ha`*. Imputed values have low = central = high. |
