# Chart spec format (DS-T1-015)

Every chart in `gallery/` is two files: `<id>.json` (the spec, which describes how the publisher drew the chart) and `<id>.csv` (the **complete** data the publisher had, in meaningful row order). Hidden galleries use exactly this format.

| Key | Type | Meaning |
|---|---|---|
| `id` | string | Chart identifier. Never use it in your logic. |
| `data` | string | CSV file name, relative to the spec. |
| `title`, `claim` | string | The publisher's headline, and the claim the chart was used to support. |
| `mark` | `"bar"` · `"area"` · `"line"` · `"bubble"` · `"heatmap"` | The drawn mark. |
| `x` | object | `field`, `type` (`"ordinal"`, `"temporal"` or `"nominal"`) and `label`. Rows are drawn in CSV order. |
| `y` | object or `null` | `field`, `type` (`"quantitative"`, `"rank"` or `"ordinal"`), `label`, `domain` (`[lo, hi]` or `null`, which means automatic, and for bars and areas that means starting at 0), `reverse` (bool: the axis is drawn upside down), optional `scale` (`"linear"` by default, or `"log"`). `null` for bubbles. |
| `y2` | object, optional | A second series on an independent right-hand axis: `field`, `label`, `domain`. |
| `size` | object, bubble only | `field` and `scale`: `"area"` (circle area ∝ value) or `"radius"` (circle radius ∝ value). |
| `color` | object, heatmap only | `field`, `scheme` (a matplotlib colormap name), `scale` (`"sequential"` or `"diverging"`) and `label`. |
| `filter` | object, optional | `field`, `from` and `to`: the publisher showed only the rows from the first row where `field == from` to the first row where `field == to`, inclusive (compare as strings). |
| `source` | string or `null` | Attribution text. `null`, `""` and whitespace-only all mean "no source given". |

The provided renderer (`chart_forensics/render.py`) draws a spec faithfully, distortions included. Run `python -m chart_forensics render --out gallery_png` to see what readers saw.
