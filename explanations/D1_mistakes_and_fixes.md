# Step D1 — Mistakes, Fixes, and Lessons Learned

## The Goal
Visualize the distribution of incubation_days (how many days between infection and symptom onset) for hantavirus patients.

## Round 1 — What we did wrong

### Mistake 1: Beeswarm plot (uninformative)
**What we used:** `sns.stripplot()` with jitter but no vertical spread — all points on a single horizontal line.
**Why it failed:** Beeswarm plots need to spread points vertically to show density. Without that, they just show a horizontal band of overlapping dots. They also don't show quartiles, median, or distribution shape clearly.
**Status: OBSOLETE — replaced with Box Plot + Violin Plot**

### Mistake 2: Too many histogram bins
**What we used:** `bins = int(sqrt(7538)) ≈ 86 bins`
**Why it failed:** incubation_days is recorded as whole numbers (7, 8, 9, … 42). The range is only 35 days. 86 bins means each bin is ~0.4 days wide. Integer data at 0.4-day intervals creates empty bins between integers — a "comb" pattern that looks like noise and hides the actual shape.
**The lesson:** The square root rule gives the number of bins, but it doesn't consider whether the data is **discrete** or **continuous**. For integer data, bins should align with the actual values, not split between them.
**Status: OBSOLETE — replaced with integer-aligned bins + FD rule histogram**

### Mistake 3: KDE on discrete data
**What we used:** `sns.kdeplot()` with bandwidth comparison
**Why it fails:** KDE assumes data is continuous. incubation_days is discrete integers. The KDE produces density below 0 (impossible — you can't have negative incubation days) and creates artificial smoothing between integers. The bandwidth choice (bw_adjust=0.5 vs 1.0 vs 2.0) is subjective with no clear answer.
**Status: OBSOLETE — replaced with Log-Transformed Histogram (better for skewed incubation data)**

### Mistake 4: Q-Q Plot with discrete plateaus
**What we used:** `stats.probplot()` — standard Q-Q plot
**Why it fails:** Q-Q plots also assume continuous data. With integer data, multiple patients share the exact same value (e.g., 100 patients with exactly 14 days), creating horizontal plateaus in the plot. These "steps" make it harder to assess normality.
**Status: KEPT with caveat** — Q-Q is still useful for detecting skew and tails, but we now note the plateaus in the interpretation.

## Round 2 — What we replaced them with

| Old (obsolete) | New replacement | Why better |
|----------------|----------------|------------|
| Beeswarm plot | **Box plot** + **Violin plot** | Box shows median/IQR/outliers in one glance; Violin adds density shape |
| 86-bin histogram | **Integer-aligned histogram** + **FD-rule histogram** | Left: no empty bins, shows real frequencies. Right: smooth shape for overall pattern |
| KDE | **Log-transformed histogram** | Incubation data is often log-normal; log transform can make it normal for analysis |
| KDE bandwidth comparison | **Log Shapiro-Wilk test** | Instead of guessing bandwidth, we test if log(data) is normal — objective |
| Old Q-Q (no context) | **Q-Q with discrete-data note** | Same plot, but we now explain the plateaus |

## What we kept that worked
- **ECDF (cumulative histogram):** Works well even with discrete data because it accumulates properly
- **Shapiro-Wilk test:** Valid test, but note warns it's unreliable for n > 5000
- **Log-normal CDF overlay on ECDF:** Added alongside the normal CDF to check if the data follows a log-normal distribution (common for incubation periods)

## Final corrected visualization set (for each variable)

| Figure | File | Purpose |
|--------|------|---------|
| Box Plot | `boxplot.png/pdf` | Median, IQR, outliers at a glance |
| Violin + Box | `violin.png/pdf` | Distribution shape + summary stats combined |
| Histogram | `histogram.png/pdf` | Integer bins (left) + FD smooth (right) |
| Log-Histogram | `log_histogram.png/pdf` | Assess log-normality |
| ECDF | `ecdf.png/pdf` | Cumulative proportion vs normal |
| Q-Q Plot | `qq.png/pdf` | Tail and skew detection (with caveats) |

## What this taught us about descriptive statistics
1. **Know your data type before you plot:** discrete integers vs continuous floats → different visualization choices
2. **Default rules (sqrt bins) are starting points, not gospel:** adjust for the actual data structure
3. **KDE is not a magic wand:** it misbehaves on bounded or discrete data
4. **Every plot has assumptions:** beeswarm needs jitter, histogram needs right bin width, Q-Q needs continuity
5. **Log transforms are powerful:** many biological/medical measurements (incubation periods, viral loads, antibody titers) are log-normal
