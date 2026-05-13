# Step D3 — ICU Days Distribution Analysis

## What we did
Analyzed `icu_days` — a spike-and-slab distribution where 50.3% of patients have 0 days (never admitted to ICU).

## Key finding: ICU admission is purely determined by severity

| Severity | ICU Admission Rate | ICU Days (if admitted) |
|----------|-------------------|----------------------|
| Mild | **0%** | — |
| Moderate | **0%** | — |
| Severe | **100%** | mean=4.5, median=4 |
| Critical | **100%** | mean=11.5, median=12 |

- No Mild or Moderate patient was ever admitted to ICU
- Every Severe and Critical patient was admitted
- The gap at day 7 is the separation between Severe (peak 4-6) and Critical (peak 8-15)

## Data quality notes
- icu_days is integer-valued: {0, 3, 4, 5, 6, 8, 9, 10, 11, 12, 13, 14, 15}
- Missing values: 1, 2, 7 — these are structural (minimum ICU stay is 3 days, gap at 7 is severity split)
- icu_admission flags map perfectly to icu_days > 0

## Q-Q plot interpretation
The Q-Q plot on all data is dominated by the zero spike (flat lower end). The non-zero Q-Q removes the spike and shows the real ICU-stay distribution. Negative theoretical quantiles on the Q-Q are expected — they simply indicate the data is bounded at zero and therefore not normal.

## Decision: Split analysis approach for icu_days
Instead of a single analysis, report two separate questions:
1. **"Who goes to ICU?"** — binary analysis (all patients, icu_admission flag)
2. **"How long do they stay?"** — continuous analysis (non-zero only, split by severity)

This avoids the zero spike biasing the distribution view.

## Summary statistics

| Measure | All patients | Non-zero only |
|---------|-------------|---------------|
| n | 7538 | 3748 |
| Mean | 3.30 | 6.64 |
| Median | 0 | 5 |
| Std Dev | 4.16 | 3.54 |
| IQR | 5 | 5 |
| Skewness | 1.19 (right) | 1.01 (right) |
| Kurtosis | 0.50 (heavy) | -0.35 (thin) |

## Recommendations
- **Overall center:** median (0) — mean (3.3) misrepresents both groups
- **Per-group reporting:** "50% never admitted; of those admitted, median stay = 5 days"
- **Do not smooth:** the gaps at 1, 2, and 7 are structural and informative
