# Step D4 — Average Temperature Distribution Analysis

## What we did
Analyzed `avg_temp_c` from the environmental dataset — a continuous, near-normal variable spanning cold (Finland) to warm (Brazil) climates.

## Key findings
- **Shape:** Approximately symmetric (skew = -0.15) with one mode
- **Tails:** Thin/light (kurtosis = -0.25)
- **Center:** Mean = 11.3°C, Median = 11.7°C — nearly identical
- **Spread:** Std Dev = 7.2°C, IQR = 9.7°C
- **Normality:** Visually close (ECDF follows normal line, Q-Q deviates only at extremes). Shapiro-Wilk technically rejects (p=0.0035) but at n=896, the test is very sensitive — visual assessment is more useful here.

## Outlier investigation
- One outlier flagged by IQR: **-8.8°C** in Ostrobothnia, Finland (Boreal taiga biome, Q1 2012)
- This is a real value — Finnish winter. **Keep it.** It's not an error, just a cold climate data point.

## Comparison with previous variables
| Variable | Skew | Normal? | Best Center | Best Spread |
|----------|------|---------|-------------|-------------|
| incubation_days | +0.47 | No | Median | IQR/MAD |
| hospital_days | +0.60 | No | Median | IQR/MAD |
| icu_days | +1.19 | No | Median (split approach) | IQR/MAD |
| **avg_temp_c** | **-0.15** | **~Yes** | **Mean** | **Std Dev** |

Temperature is the **first variable where mean and std dev are appropriate** — because the distribution is symmetric and approximately normal.

## Summary statistics
| Measure | Value |
|---------|-------|
| n | 896 |
| Mean | 11.26°C |
| Median | 11.70°C |
| Std Dev | 7.18°C |
| IQR | 9.70°C (Q1=6.2, Q3=15.9) |
| Range | [-8.8, 29.7] |
| Skewness | -0.15 |
| Kurtosis | -0.25 |

## Questionnaire results
| Question | User observed | Numbers confirmed? |
|----------|---------------|-----------------|
| Q1, median, Q3 | 6, 12, 16 | ✅ Close (6.2, 11.7, 15.9) |
| Symmetric? | Yes, one peak, slight left skew | ✅ Skew=-0.15 |
| Mean vs median | Very close | ✅ Diff=0.44°C |
| Tails | Thin | ✅ Kurtosis=-0.25 |
| ECDF | Normal | ✅ Visually, p=0.0035 technically |
| Q-Q | Normal, deviates only at ±2.5 | ✅ |
