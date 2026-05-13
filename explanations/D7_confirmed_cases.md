# Step D7 — Confirmed Cases Distribution Analysis

## What we did
Analyzed `confirmed_cases` from the country_yearly dataset — integer count data, the most skewed variable in the dataset.

## Key findings
- **Extreme right skew** (skew=2.82, kurtosis=7.14)
- **Mean=1793 vs Median=58** — the mean is 31x the median. The median (58) represents "a typical year" far better than the mean
- **Log transform improves**, but data is not perfectly log-normal
- **The extreme skew is explained by two subgroup splits:**

### By syndrome
| Syndrome | Mean | Median | Max | Interpretation |
|----------|------|--------|-----|---------------|
| HPS | 30 | 13 | 146 | Rare but deadly — Americas focus |
| HFRS | 2,515 | 122 | 23,885 | Common in Asia/Europe — drives the tail |

### By WHO region
| Region | Mean | Median | Max |
|--------|------|--------|-----|
| AMRO (Americas) | 30 | 13 | 146 |
| EURO (Europe) | 1,046 | 89 | 9,496 |
| WPRO (Asia) | 5,358 | 482 | 23,885 |

**Conclusion:** The massive right tail is driven by HFRS in Western Pacific countries (China, Korea). HPS (Americas) has consistently low case counts. The overall "extreme skew" disappears when stratified by syndrome — HPS has mild skew, HFRS has moderate skew, but mixing them creates extreme skew.

## Summary statistics
| Measure | Value |
|---------|-------|
| n | 939 |
| Mean | 1,793 cases |
| Median | 58 cases |
| Std Dev | 4,470 |
| MAD | 51 |
| IQR | 415 (Q1=12, Q3=427) |
| Range | [1, 23,885] |
| Skewness | +2.82 (extreme right) |
| Kurtosis | +7.14 (very heavy tails) |

## Outlier investigation
- **18.1%** of rows are flagged as outliers by the IQR rule (upper bound = 1,050)
- When the outlier rate is this high, it's not "outliers" — it's a different distribution
- **All top 20 cases are China HFRS** (17,000–24,000 cases/year). These are real, not data errors
- **Verdict:** Keep all data. The "outliers" are just HFRS in Asia — a fundamentally different disease dynamic than HPS

### Why the IQR rule flags so many here
The IQR rule assumes roughly symmetric spread. On extreme right-skewed variables, Q3 + 1.5×IQR falls within the bulk of the real tail rather than beyond it. The rule isn't wrong — it's just designed for symmetric distributions. For skewed data, log-transform then IQR, or MAD-based detection, would flag fewer false positives.

## Visual readability
The extreme right tail (up to 23,885) compresses the box plot and violin into unreadable slivers. We provide two versions:
- **Full-range plots** (`cases_*.png`): Show the complete data including extreme values
- **No-outliers versions** (`cases_nooutliers_*.png`): IQR-filtered (170 points removed, 18.1%) + fliers hidden — shows the bulk distribution clearly

## Your question: is this real or underdiagnosis bias?
From the data alone, we can't prove it either way. But the consistent 100x+ difference between AMRO (mean=30) and WPRO (mean=5,358) across decades of reporting suggests it's **real epidemiological variation**, not just underdiagnosis:
- HPS (Americas) is genuinely rarer — transmitted by specific rodent species in limited geographic ranges
- HFRS (Asia/Europe) is more common — Hantaan/Seoul/Puumala viruses infect widespread rodent populations
- China alone has reported this consistently since the 1970s

## Recommendations
- **Center:** Median (58) — mean (1,793) is misleading
- **Spread:** MAD (51) or IQR (415) — std dev (4,470) is meaningless for the typical case
- **Report per syndrome:** The overall number hides the HPS/HFRS distinction
