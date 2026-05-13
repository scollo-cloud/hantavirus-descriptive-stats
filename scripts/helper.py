"""
helper.py — shared utility functions for all analysis scripts
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns; sns.set_theme()
from scipy import stats
import os

np.random.seed(42)

DATA_DIR = "../data"
FIGS_DIR = "../figures"
TABLES_DIR = "../tables"

for d in [FIGS_DIR, TABLES_DIR]:
    os.makedirs(d, exist_ok=True)


def load_csv(filename):
    return pd.read_csv(f"{DATA_DIR}/{filename}")


def iqr_outliers(series):
    np.random.seed(42)
    Q1 = series.quantile(0.25)
    Q3 = series.quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR
    return series[(series < lower) | (series > upper)]


def print_summary(name, series):
    kurt = stats.kurtosis(series.dropna())
    tail_desc = "lighter tails + flatter peak than normal" if kurt < 0 else "heavier tails + sharper peak than normal"
    
    print(f"\n{'='*60}")
    print(f"  {name}")
    print(f"{'='*60}")
    print(f"  Count:      {len(series)}")
    print(f"  Missing:    {series.isna().sum()}")
    print(f"  Mean:       {series.mean():.4f}")
    print(f"  Median:     {series.median():.4f}")
    print(f"  Std Dev:    {series.std():.4f}")
    print(f"  Variance:   {series.var():.4f}")
    print(f"  MAD:        {(series - series.median()).abs().median():.4f}")
    print(f"  IQR:        {series.quantile(0.75) - series.quantile(0.25):.4f}")
    print(f"  Range:      [{series.min():.4f}, {series.max():.4f}]")
    print(f"  Skewness:   {stats.skew(series.dropna()):.4f}")
    print(f"  Kurtosis:   {kurt:.4f} ({tail_desc})")


def normality_check(series, name=""):
    clean = series.dropna()
    n = len(clean)
    stat, p = stats.shapiro(clean)
    
    print(f"\n  --- Normality Check: {name} ---")
    print(f"  Shapiro-Wilk: stat={stat:.4f}, p={p:.4f}")
    
    if n > 5000:
        print(f"  ⚠ n={n} > 5000: Shapiro-Wilk is overly sensitive at this size.")
        print(f"    Any trivial deviation yields p < 0.001. Rely on visual (ECDF/Q-Q)")
        print(f"    and effect size (|skew| < 0.5, |kurtosis| < 1) instead.")
    
    if p > 0.05:
        print(f"  → Cannot reject normality (p > 0.05) — data may be normal")
    else:
        print(f"  → Reject normality (p <= 0.05) — data is NOT normal")


def kurtosis_description(kurt):
    if kurt < 0:
        return "lighter tails + flatter peak than normal"
    elif kurt > 0:
        return "heavier tails + sharper peak than normal"
    else:
        return "similar to normal"


def recommend_center(series):
    np.random.seed(42)
    skew = stats.skew(series.dropna())
    if abs(skew) < 0.5:
        return "mean"
    elif abs(skew) < 1.0:
        return "median (moderate skew)"
    else:
        return "median (strong skew)"


def recommend_spread(series):
    np.random.seed(42)
    clean = series.dropna()
    skew = stats.skew(clean)
    if abs(skew) < 0.5:
        return "standard deviation"
    elif abs(skew) < 1.0:
        return "IQR"
    else:
        return "IQR or MAD"


def savefig(name):
    plt.savefig(f"{FIGS_DIR}/{name}.pdf", bbox_inches="tight", dpi=300)
    plt.savefig(f"{FIGS_DIR}/{name}.png", bbox_inches="tight", dpi=150)
    print(f"  Saved: {FIGS_DIR}/{name}.pdf + .png")
