# Step B2 — Summary Statistics for Every Numeric Column

## What we did
For every numeric column across all datasets, we computed: count, mean, median, standard deviation, variance, MAD (Median Absolute Deviation), IQR, range, skewness, and kurtosis.

## The numbers — and what they teach us

### Key concept 1: Mean vs Median tells you about symmetry

Compare these three variables:

| Variable | Mean | Median | Skewness | What it means |
|----------|------|--------|----------|---------------|
| avg_temp_c | 11.3 | 11.7 | -0.15 | Near zero → **symmetric**, mean ≈ median |
| incubation_days | 20.4 | 19.0 | +0.47 | Positive → **moderate right skew**, mean > median |
| confirmed_cases | 1793 | 58 | +2.82 | Large positive → **extreme right skew**, mean >> median |

**The rule:**
- Mean ≈ Median → symmetric distribution (use mean to describe center)
- Mean > Median → right-skewed (median describes the "typical" case better)
- Mean < Median → left-skewed

*confirmed_cases* is the most dramatic: the mean (1793) is **31 times larger** than the median (58). That's because a few countries (China, Korea) report tens of thousands of cases while most report under 100. The mean is pulled up by those extremes — it doesn't represent "a typical year" at all.

### Key concept 2: Median = 0 but Mean > 0

| Variable | Mean | Median | Skewness | What's happening |
|----------|------|--------|----------|-----------------|
| icu_days | 3.3 | 0 | +1.19 | Half of patients never go to ICU (median=0), but those who do stay several days |
| human_to_human_cases | 0.16 | 0 | +7.01 | Most years have zero H2H transmission, but a few have up to 9 cases |

This is a **spike-and-slab** pattern: a pile of zeros plus a spread of positive values. The mean doesn't represent anyone — it's a compromise between "zero" and "some positive number." The median is more honest here: "most patients don't go to ICU."

### Key concept 3: Which spread measure tells the truth?

Look at confirmed_cases:

| Measure | Value | Robust to outliers? |
|---------|-------|-------------------|
| Std Dev | 4470 | **No** — pulled up by extremes |
| IQR | 415 | Yes — ignores top/bottom 25% |
| MAD | 51 | Yes — based on median |
| Range | 23884 | No — just min and max, tells you nothing about the middle |

For symmetric, near-normal data (like avg_temp_c):
- Std Dev = 7.2, IQR = 9.7 → similar magnitude, both useful
- `mean ± 1 std` covers about 68% of the data (if normal)

For skewed data (like confirmed_cases):
- Std Dev = 4470, but most values are below 500
- `mean ± 1 std` would give a negative lower bound! Meaningless.
- IQR or MAD is much more informative

### Key concept 4: Variables that look nearly normal

| Variable | Mean ≈ Median? | Skewness near 0? | Notes |
|----------|---------------|-------------------|-------|
| avg_temp_c | Yes | -0.15 | Good candidate for normal distribution |
| rodent_abundance_index | Yes (0.67 vs 0.67) | +0.02 | Surprisingly symmetric for a bounded [0,1] variable |
| ndvi | Yes | -0.03 | Also near-symmetric |
| deforestation_km2 | Yes (3.43 vs 3.36) | +0.07 | Also near-symmetric |

These will contrast nicely with the skewed variables when we make histograms and Q-Q plots.

### Key concept 5: Small n warning

**hantavirus_outbreaks.csv** (20 rows):
- Mean cases = 621, Median = 32 — an enormous gap
- With n=20, even the median is unreliable
- We'll still analyze it, but every conclusion comes with "small sample" caveat

## How this connects to the next steps (Phase C & D)

These numbers are our **baseline**:
- In C1, we'll use IQR to find outliers — we already know from IQR which columns will have many
- In D1-D8, when we make histograms, we'll compare what we *see* to what these numbers *say*
- The skewness values tell us which variables will look symmetric and which will look lopsided in the plots

Next step (C1) is outlier detection, where we investigate the extreme values that are pulling those means away from the medians.
