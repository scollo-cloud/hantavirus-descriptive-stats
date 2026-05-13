# Step D8 — Case Fatality Rate Distribution Analysis

## What we did
Analyzed `case_fatality_rate` from country_yearly data — a proportion bounded [0, 0.46] that turned out to be strongly bimodal by syndrome.

## Key findings
- **Overall:** Mean=0.092, Median=0.018 — large gap, not representative of either group
- **By syndrome (the real story):**
  - HPS: mean=28.1%, median=29.0% (deadly — 1 in 4 die)
  - HFRS: mean=1.4%, median=0.6% (much milder)
- HPS is ~20x more lethal than HFRS

## Why the overall distribution is bimodal
The overall histogram has two peaks: one at ~0% (HFRS) and one at ~30% (HPS). This is not an artifact — it's two fundamentally different diseases being averaged together.

## Summary statistics

| Measure | All | HPS Only | HFRS Only |
|---------|-----|----------|-----------|
| n | 939 | 273 | 666 |
| Mean | 9.2% | 28.1% | 1.4% |
| Median | 1.8% | 29.0% | 0.6% |
| IQR | 17.4% | — | — |
| Skewness | 1.28 | — | — |

## Recommendations
- **Never report CFR as a single number** for data mixing HPS and HFRS
- Report per syndrome: "HPS kills ~29% of patients; HFRS kills ~0.6%"
- The overall 9.2% represents neither group
- **Note:** CFR differences may partly reflect healthcare access or time-to-treatment, not just virology. If data on these factors existed, stratifying by them would strengthen the analysis.
