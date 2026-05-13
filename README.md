# Hantavirus Descriptive Statistics Analysis

A step-by-step application of descriptive statistics and data visualization to real
hantavirus epidemiological data from Kaggle. Built for learning and portfolio purposes.

## What This Project Covers

- **Loading and inspecting** real-world data (missing values, duplicates, data types)
- **Summary statistics** (mean, median, std, MAD, IQR, skewness, kurtosis)
- **Distribution analysis** (box plots, violin plots, histograms, ECDF, Q-Q plots)
- **Outlier detection and investigation** (IQR rule, contextual review)
- **Subgroup discovery** (severity, syndrome, region, biome)
- **Comparative analysis** (violin plots by group)
- **Visualization critique** (why bar charts + error bars hide the truth)
- **LaTeX report** with integrated figures and tables

## Key Findings

| Variable | Shape | Best Center | Best Spread |
|----------|-------|-------------|-------------|
| Incubation Days | Right-skewed | Median (19d) | IQR |
| Hospital Days | 4 severity groups | Median (9d) | IQR |
| ICU Days | Spike-and-slab | Split approach | IQR |
| Temperature | ~Normal | Mean (11.3°C) | Std Dev |
| Rainfall | Right-skewed, heavy tail | Median (195mm) | IQR |
| Rodent Abundance | Symmetric | Mean (0.67) | Std Dev |
| Confirmed Cases | Extreme right skew | Median (58/yr) | IQR |
| Case Fatality Rate | Bimodal by syndrome | Report per syndrome | IQR |

## Mistakes Made and Fixed

This project documents visualization mistakes and corrections:
- ✅ Replaced uninformative beeswarm plots with box + violin
- ✅ Fixed histogram bins for discrete integer data
- ✅ Removed KDE (misleading on bounded data)
- ✅ Q-Q only for unbounded variables
- ✅ Discovered aggregation artifact in hospital_days (bimodal → 4 severity groups)
- ✅ Bar chart critique demonstrates why error bars hide the distribution

See `explanations/D1_mistakes_and_fixes.md` and `explanations/` for full details.
- ✅ Fixed ECDF x-axis starting at -2000 (cases can't be negative)

## Repository Structure

```
├── data/              Raw CSV files
├── scripts/           Python analysis scripts
│   ├── helper.py      Shared utility functions
│   ├── 01_*.py        Data loading and exploration
│   ├── 02_*.py        Summary statistics
│   ├── D1_*.py        Variable-by-variable analysis (D1-D8)
│   ├── D2b_*.py/D3b_*.py  Subgroup investigations
│   ├── C_*.py         Outlier investigation
│   ├── E1_*.py        Comparative violin plots
│   ├── E2_*.py        Bar chart critique
│   └── F_*.py         Summary table generation
├── figures/           Output plots (PDF + PNG)
├── explanations/      Step-by-step docs (B1-B2, C, D1-D8, E1-E2, F)
├── tables/            LaTeX summary tables (preview: tables_preview.pdf)
├── dashboard/         Interactive HTML dashboard (open dashboard/index.html)
└── report/            LaTeX reports (summary + detailed)
```

## How to Reproduce

```bash
pip install -r requirements.txt
python3 main.py
```

This will run the entire analysis pipeline, generate all figures in `figures/`, create the summary tables in `tables/`, and build the interactive dashboard in `dashboard/`.

To manually compile reports:
```bash
cd report
pdflatex detailed_report.tex
```

All scripts use `np.random.seed(42)` for reproducibility.

## Reports

- `report/summary_report.tex` — Concise results (3 pages, compiles to PDF)
- `report/detailed_report.tex` — Full learning journey with figures, tables, mistakes, and fixes (15 pages)

Compile with `pdflatex`.

## Dataset

Source: [Kaggle — Hantavirus Andes Virus Global Epidemiology](https://www.kaggle.com/datasets/zkskhurram/hantavirus-andes-virus-global-epidemiology)

> **⚠️ Disclaimer:** This is a historical Kaggle dataset on hantavirus epidemiology, **not** the 2025 outbreak data. This project focuses on learning descriptive statistics — it is not a study of current events.

## Tools Used

Python (pandas, numpy, scipy, matplotlib, seaborn), LaTeX, Git
