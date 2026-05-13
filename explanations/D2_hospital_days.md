# Step D2 — Hospital Days Distribution Analysis

## What we did
Loaded `hospital_days` from the clinical dataset and analyzed its distribution: box plot, violin, histogram (integer + FD bins), log-histogram, ECDF, Q-Q plot.

## The bimodal discovery
The overall histogram of hospital_days showed **two peaks** with dips at day 4 and day 9 — suggesting a bimodal distribution. We investigated four possible causes:

### Hypothesis testing

| Factor | Does it explain the shape? | Evidence |
|--------|---------------------------|----------|
| **Severity** ✅ | **Yes — perfectly** | Mild (mean=2.5), Moderate (mean=6.5), Severe (mean=13.5), Critical (mean=20.6) — each has a distinct, non-overlapping center |
| Outcome ❌ | No — weak effect | Deceased (mean=15.4) vs Recovered (mean=9.7) — tracks severity, doesn't explain peaks |
| Syndrome ❌ | No — no effect | HPS (mean=10.3) vs HFRS (mean=10.5) — nearly identical |
| Age Group ❌ | No — no effect | All groups ~10.4 — no separation |

### Conclusion
The "bimodal" shape is an **aggregation artifact** (a form of Simpson's paradox). Mixing four severity groups with different centers creates the appearance of multiple peaks. The dip at day 9 is the gap between Moderate (~6 days) and Severe (~13 days) distributions.

**Lesson:** Always check subgroups before describing a distribution. A unimodal shape might hide group differences; a bimodal shape might be an artifact of group mixing.

## Summary statistics
| Measure | Value |
|---------|-------|
| n | 7538 |
| Mean | 10.46 |
| Median | 9.00 |
| Std Dev | 6.18 |
| MAD | 4.00 |
| IQR | 9.00 (Q1=6, Q3=15) |
| Range | [2, 27] |
| Skewness | +0.60 (right-skewed) |
| Kurtosis | -0.42 (thin tails) |
| Shapiro-Wilk | p ≈ 0.000 (not normal) |

## Recommendations
- **Center:** Median (9 days) — the mean (10.5) is pulled right by Critical/Severe cases
- **Spread:** IQR (9 days) or MAD (4 days) — Std Dev assumes symmetry
- **But the real story is:** no single number describes "typical hospital stay" because severity groups are fundamentally different. Always report per-group statistics.

## Decision: Do NOT smooth the histogram
The "bumps" at days 4 and 9 are not noise — they are real signal from four non-overlapping severity subgroups. Smoothing would hide this finding and create a single broad hump that doesn't represent any actual patient group.

**Instead:** The split-by-severity histogram (hospital_by_severity.png) is the primary figure. The aggregated histogram is only shown as secondary reference with the caveat: *"Appears multimodal due to severity subgroups — each subgroup is unimodal on its own."*
## Note
 >Decision: Do NOT smooth the histogram. The "bumps" are real signal from four severity subgroups. Smoothing would hide the finding. Instead, show the split-by-severity histogram as the main figure and use the aggregated histogram only as secondary reference with the caveat: "appears multimodal due to severity subgroups."
