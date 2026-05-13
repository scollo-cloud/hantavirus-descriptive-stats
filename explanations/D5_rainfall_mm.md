# Step D5 — Rainfall Distribution Analysis

## What we did
Analyzed `rainfall_mm` — continuous, right-skewed environmental data spanning desert to tropical forest biomes.

## Key findings
- **Shape:** Strongly right-skewed (skew=1.80), heavy-tailed (kurtosis=5.05)
- **Center:** Mean=253mm, Median=195mm — large gap, median is the honest choice
- **Spread:** Std Dev=218mm (inflated by extremes), IQR=237mm, MAD=109mm — IQR is best
- **Log transform:** Noticeably improves symmetry (continuous data, so no integer artifacts)
- **Biome differences explain much of the spread:** Desert scrub (mean=63mm) vs Valdivian forest (mean=630mm)

## Rainfall by biome
| Biome | Mean (mm) | Median (mm) |
|-------|-----------|-------------|
| Desert scrub | 63 | 61 |
| Boreal/temperate | 117 | 123 |
| Forest steppe | 127 | 123 |
| Warm temperate | 151 | 143 |
| Boreal taiga | 156 | 155 |
| Temperate mixed | 184 | 167 |
| Temperate forest | 206 | 203 |
| Pampa grassland | 253 | 282 |
| Temperate rain | 258 | 252 |
| Cerrado | 309 | 291 |
| Temperate deciduous | 345 | 304 |
| Mediterranean scrub | 350 | 308 |
| Atlantic forest | 390 | 403 |
| Valdivian forest | 631 | 608 |

## Summary statistics
| Measure | Value |
|---------|-------|
| n | 896 |
| Mean | 252.8 mm |
| Median | 195.4 mm |
| Std Dev | 217.8 mm |
| MAD | 108.6 mm |
| IQR | 237.1 mm |
| Range | [0, 1673.2] |
| Skewness | +1.80 (strong right) |
| Kurtosis | +5.05 (heavy tails) |

## Recommendations
- **Center:** Median (195mm) — mean (253mm) is pulled by Valdivian forest extremes
- **Spread:** IQR (237mm) — std dev (218mm) is similar here because the tail is very long but has few extreme values
- **Log transform** is appropriate for modeling but raw median+IQR is better for reporting
