"""
helper.py — shared utility functions for all analysis scripts
"""
from pathlib import Path
from typing import Optional
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns; sns.set_theme()
from scipy import stats

# Thresholds based on Bulmer (1979) guidelines
SKEW_SYMMETRIC = 0.5
SKEW_MODERATE = 1.0
LARGE_N_SHAPIRO = 5000

# Use absolute paths based on script location
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
FIGS_DIR = PROJECT_ROOT / "figures"
TABLES_DIR = PROJECT_ROOT / "tables"

for d in [FIGS_DIR, TABLES_DIR]:
    d.mkdir(parents=True, exist_ok=True)


def load_csv(filename: str) -> pd.DataFrame:
    """Load CSV from data directory with error handling."""
    path = DATA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Data file not found: {path}")
    if path.stat().st_size == 0:
        raise ValueError(f"File is empty: {path}")
    return pd.read_csv(path)


def iqr_outliers(series: pd.Series) -> pd.Series:
    """Flag outliers using IQR rule (1.5 * IQR)."""
    Q1 = series.quantile(0.25)
    Q3 = series.quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR
    return series[(series < lower) | (series > upper)]


def print_summary(name: str, series: pd.Series) -> None:
    """Print key summary statistics for a numeric series."""
    c = series.dropna()
    skew_val = stats.skew(c)
    kurt_val = stats.kurtosis(c)
    kurt_desc = kurtosis_description(kurt_val)

    print(f"\n{'='*60}")
    print(f"  {name}")
    print(f"{'='*60}")
    print(f"  Count:      {len(c)}")
    print(f"  Missing:    {series.isna().sum()}")
    print(f"  Mean:       {c.mean():.4f}")
    print(f"  Median:     {c.median():.4f}")
    print(f"  Std Dev:    {c.std():.4f}")
    print(f"  Variance:   {c.var():.4f}")
    print(f"  MAD:        {(c - c.median()).abs().median():.4f}")
    print(f"  IQR:        {c.quantile(0.75) - c.quantile(0.25):.4f}")
    print(f"  Range:      [{c.min():.4f}, {c.max():.4f}]")
    print(f"  Skewness:   {skew_val:.4f}")
    print(f"  Kurtosis:   {kurt_val:.4f} ({kurt_desc})")


def normality_check(series: pd.Series, name: str = "") -> None:
    """Run Shapiro-Wilk test with n > 5000 caveat."""
    clean = series.dropna()
    n = len(clean)
    stat, p = stats.shapiro(clean)

    print(f"\n  --- Normality Check: {name} ---")
    print(f"  Shapiro-Wilk: stat={stat:.4f}, p={p:.4f}")

    if n > LARGE_N_SHAPIRO:
        print(f"  ⚠ n={n} > {LARGE_N_SHAPIRO}: Shapiro-Wilk is overly sensitive.")
        print(f"    Rely on visual (ECDF/Q-Q) and effect size (|skew| < {SKEW_SYMMETRIC}) instead.")

    if p > 0.05:
        print(f"  → Cannot reject normality (p > 0.05)")
    else:
        print(f"  → Reject normality (p <= 0.05)")


def recommend_center(series: pd.Series) -> str:
    """Recommend mean or median based on skewness."""
    skew = stats.skew(series.dropna())
    if abs(skew) < SKEW_SYMMETRIC:
        return "mean"
    elif abs(skew) < SKEW_MODERATE:
        return "median (moderate skew)"
    else:
        return "median (strong skew)"


def recommend_spread(series: pd.Series) -> str:
    """Recommend std or IQR/MAD based on skewness."""
    skew = stats.skew(series.dropna())
    if abs(skew) < SKEW_SYMMETRIC:
        return "standard deviation"
    elif abs(skew) < SKEW_MODERATE:
        return "IQR"
    else:
        return "IQR or MAD"


def validate_positive(series: pd.Series, name: str = "variable") -> None:
    """Raise if series contains non-positive values (for log transform)."""
    if (series <= 0).any():
        raise ValueError(f"Log transform requires all positive values; {name} has values <= 0")


def kurtosis_description(kurt: float) -> str:
    """Return text description of kurtosis value."""
    if kurt < 0:
        return "lighter tails + flatter peak than normal"
    elif kurt > 0:
        return "heavier tails + sharper peak than normal"
    return "similar to normal (mesokurtic)"


def savefig(name: str) -> None:
    """Save current figure as PDF and PNG."""
    plt.savefig(FIGS_DIR / f"{name}.pdf", bbox_inches="tight", dpi=300)
    plt.savefig(FIGS_DIR / f"{name}.png", bbox_inches="tight", dpi=150)
    print(f"  Saved: {FIGS_DIR / name}.pdf + .png")
