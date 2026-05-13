# Phase C — Outlier Investigation Results

## What we did
Applied the IQR rule (Q1 - 1.5×IQR, Q3 + 1.5×IQR) to every numeric column across all datasets, printed outlier rows with full context (severity, syndrome, country, biome, etc.), and decided keep/remove.

## Results: No data errors found

| Variable | Outliers | % | What they are | Verdict |
|----------|----------|---|---------------|---------|
| incubation_days | 0 | — | — | — |
| hospital_days | 0 | — | — | — |
| icu_days | 432 | 5.7% | Critical patients with 13-15 day ICU stays | Keep |
| avg_temp_c | 1 | 0.1% | Finland winter (-8.8°C), Ostrobothnia region | Keep |
| rainfall_mm | 44 | 4.9% | Valdivian forest monsoon rains (Chile) + Atlantic forest (Brazil) | Keep |
| confirmed_cases | 170 | 18.1% | China HFRS, consistent 1970s–2024 | Keep |
| case_fatality_rate | 9 | 1.0% | HPS in Bolivia, US, Brazil with CFR > 44% | Keep |
| rodent_abundance_index | 0 | — | — | — |
| deforestation_km2 | 0 | — | — | — |

## Key insight
When 18% of a variable is flagged as outliers (confirmed_cases), it's not "outliers" — it's **two different distributions mixed**. China HFRS (17k–24k cases/year) is a separate population from every other country-syndrome combination. This is the same lesson as hospital_days by severity: always check subgroups before calling something an outlier.

### IQR rule limitation on skewed data
The IQR rule assumes roughly symmetric spread. On extreme right-skewed variables like confirmed_cases, the upper fence (Q3 + 1.5×IQR) falls within the bulk of the real tail rather than beyond it. An alternative for skewed data is to log-transform first, then apply IQR, or to use MAD-based outlier detection.

## Conclusion
The dataset is clean. No values were removed. Every flagged extreme is a genuine observation explained by biological, environmental, or epidemiological context.
