# Design Rationale: DS-T2-011

## 1. Colour science
- CVD simulation: method, citation, colour space, severity, and how you validated it.
- Colour difference: formula and why it suits chart marks.

## 2. Comparison A: palettes
| Palette | min ΔE normal | protan | deutan | tritan | min contrast | passes |
|---|---|---|---|---|---|---|
| tab10 | | | | | | |
| Okabe–Ito (or another published one) | | | | | | |
| Ours | | | | | | |

How you designed the palette (search, by hand, adapted) and its weaknesses.

## 3. Comparison B: colour-difference formulas
At least 10 pairs, your formula vs an alternative. Where do they disagree, and does it matter for the audit?

## 4. Comparison C: regression signatures
| Chart | Benign: noise | Benign: 1-px shift | Meaningful: data | Meaningful: recolour |
|---|---|---|---|---|

For your signature and a naive hash. The chosen tolerance, with false-alarm and miss rates.

## 5. API decisions
Theme, annotation helpers, state handling.

## 6. What the checks do not cover, and how real readers would validate the palette
