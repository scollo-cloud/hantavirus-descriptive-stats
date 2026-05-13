# Step D6 — Rodent Abundance Index Distribution Analysis

## What we did
Analyzed `rodent_abundance_index` — a bounded [0,1] variable that turned out to be the most symmetric variable in the dataset.

## Key findings
- **Shape:** Near-perfect symmetry (skew=0.018) — most symmetric variable analyzed so far
- **Tails:** Thin/flat (kurtosis=-1.12) — distribution is plateau-like, slightly "flat-topped"
- **Center:** Mean=0.673, Median=0.672 — essentially identical
- **Spread:** Std Dev=0.179, IQR=0.298
- **Bounded [0,1] constraints:** The tails clip at the bounds (Q-Q deviates at ±2), but the middle is approximately normal

## Rodent abundance by biome
Unlike rainfall (which varied 10x across biomes), rodent abundance is remarkably consistent:
| Comparison | Rainfall (mm) | Rodent Index |
|-----------|---------------|-------------|
| Desert scrub | 63 | 0.684 |
| Valdivian forest | 630 | 0.679 |
| Range | 63–630 | 0.64–0.72 |

This suggests rodent populations are driven more by local factors (season, food availability) than broad climate zones.
**Caveat:** This assumes comparable sampling protocols across biomes. If trap effort or survey methods differed, the apparent constancy could partly reflect methodological consistency.

## Summary statistics
| Measure | Value |
|---------|-------|
| n | 896 |
| Mean | 0.673 |
| Median | 0.672 |
| Std Dev | 0.179 |
| MAD | 0.149 |
| IQR | 0.298 |
| Range | [0.301, 1.000] |
| Skewness | +0.018 (near zero) |
| Kurtosis | -1.121 (thin/flat) |

## Recommendations
- **Center:** Mean (0.673) — identical to median, so either works
- **Spread:** Std Dev (0.179) — appropriate given symmetry
- Pair with IQR (0.298) to show spread range
