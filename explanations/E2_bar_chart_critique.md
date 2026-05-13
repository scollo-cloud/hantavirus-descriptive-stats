# Phase E2 — Bar Chart Critique

## What we did
Created a side-by-side comparison of the same data shown two ways:
- **Left:** Bar chart with error bars (mean ± 1 SE) — the "standard" scientific figure
- **Right:** Violin plot with box overlay — the honest version

## Why bar charts + error bars are misleading

### 1. Sample size is hidden
Both bars look equally reliable regardless of whether n=10 or n=1000.
Mild has n=1121, Critical has n=1142 — same bar size, different precision.

### 2. Distribution shape is hidden
Each severity group has a different shape:
- Mild: tight peak at 2, right tail to ~5
- Moderate: peak at 6, some spread
- Severe: peak at 13, wider spread  
- Critical: peak at 21, widest spread

The bar chart shows none of this.

### 3. Outliers are hidden
Critical has patients with 5-day stays and patients with 27-day stays.
The bar erases this variation into a single mean.

### 4. Multimodality is hidden
If any group were bimodal (two peaks), the bar chart would look identical.
Only the violin reveals the true shape.

### 5. Mean may not be representative
The bar centers on the mean by default. But for skewed data, the median is often better.
Critical's mean (20.6) is pulled by the tail; the median (21) is more representative.

## How the error bar is calculated
SEM = std / sqrt(n)

This assumes the data is normal and symmetric. Hospital_days violates both assumptions.

## Bottom line
A bar chart tells you 2 numbers (mean, SE).
A violin + box tells you: n, min, Q1, median, Q3, max, shape, skew, tails, multimodality.

Bar charts are not "cleaner." They are less honest.

## Script
`E2_bar_chart_critique.py`
