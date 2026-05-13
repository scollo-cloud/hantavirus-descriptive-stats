# Phase F — Summary Tables

## What we did
Generated 10 LaTeX-ready summary tables from all analysis results, saved to `tables/`.

## Tables created

### 1. Master Summary (`master_summary.tex`)
All 8 numeric variables with: n, mean, median, std, IQR, MAD, skewness, kurtosis, best center, best spread.

### 2. Incubation by Severity (`incubation_by_severity.tex`)
n, mean, median, std, IQR per severity level. Source: D1.

### 3. Hospital by Severity (`hospital_by_severity.tex`)
Shows the clean separation between 4 severity groups. Source: D2.

### 4. ICU by Severity (`icu_by_severity.tex`)
ICU admission rate and stay length per severity. Source: D3.

### 5. CFR by Syndrome (`cfr_by_syndrome.tex`)
HPS vs HFRS — the 20x CFR difference. Source: D8.

### 6. Cases by Region (`cases_by_region.tex`)
AMRO vs EURO vs WPRO — WPRO (China) dominates. Source: D7.

### 7. Incubation by Groups (`incubation_by_groups.tex`)
By syndrome (HPS/HFRS) and outcome (Recovered/Deceased).

### 8. Environmental by Biome (`environmental_by_biome.tex`)
Temperature, rainfall, rodent index, NDVI per biome.

### 9. Mistakes Summary (`mistakes_summary.tex`)
Table of what went wrong, why, and what replaced it.

### 10. Outlier Summary (`outlier_summary.tex`)
All flagged outliers with counts, percentages, and verdict.

## Script
`F_summary_tables.py`
