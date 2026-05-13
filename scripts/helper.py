"""
helper.py — shared utility functions for all analysis scripts
"""
from typing import Optional, Tuple, Dict, Any
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import pandera as pa
from pandera.typing import Series
from config import DATA_DIR, FIGS_DIR, TABLES_DIR, SKEW_SYMMETRIC, SKEW_MODERATE, LARGE_N_THRESHOLD

# Set seaborn theme once
sns.set_theme(style="whitegrid")

# =============================================================================
# DATA VALIDATION
# =============================================================================

# Data Validation Schemas
clinical_schema = pa.DataFrameSchema({
    "incubation_days": pa.Column(float, pa.Check.ge(0), nullable=True),
    "hospital_days": pa.Column(float, pa.Check.ge(0), nullable=True),
    "icu_days": pa.Column(float, pa.Check.ge(0), nullable=True),
    "severity": pa.Column(str, pa.Check.isin(["Mild", "Moderate", "Severe", "Critical"]), nullable=True),
    "outcome": pa.Column(str, pa.Check.isin(["Recovered", "Deceased"]), nullable=True),
})

def validate_clinical_data(df: pd.DataFrame) -> pd.DataFrame:
    """Validate clinical dataset using pandera."""
    try:
        return clinical_schema.validate(df)
    except pa.errors.SchemaError as e:
        print(f"❌ Data Validation Error in clinical data: {e}")
        raise

def load_csv(filename: str, validate: bool = False) -> pd.DataFrame:
    """Load CSV from data directory with error handling."""
    path = DATA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Data file not found: {path}")
    if path.stat().st_size == 0:
        raise ValueError(f"File is empty: {path}")

    df = pd.read_csv(path)

    if validate and filename == "hantavirus_clinical.csv":
        df = validate_clinical_data(df)

    return df

# =============================================================================
# STATISTICAL FUNCTIONS
# =============================================================================

def iqr_outliers(series: pd.Series) -> pd.Series:
    """Flag outliers using IQR rule (1.5 * IQR)."""
    Q1 = series.quantile(0.25)
    Q3 = series.quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR
    return series[(series < lower) | (series > upper)]


def print_summary(name: str, series: pd.Series) -> Dict[str, float]:
    """
    Print key summary statistics for a numeric series and return as dict.
    
    Args:
        name: Name of the variable for display
        series: Pandas Series to summarize
        
    Returns:
        Dictionary containing all computed statistics for reuse
    """
    c = series.dropna()
    q1, q3 = c.quantile(0.25), c.quantile(0.75)
    iqr = q3 - q1
    skew_val = stats.skew(c)
    kurt_val = stats.kurtosis(c)
    kurt_desc = kurtosis_description(kurt_val)
    mad = (c - c.median()).abs().median()

    print(f"\n{'='*60}")
    print(f"  {name}")
    print(f"{'='*60}")
    print(f"  Count:      {len(c)}")
    print(f"  Missing:    {series.isna().sum()}")
    print(f"  Mean:       {c.mean():.4f}")
    print(f"  Median:     {c.median():.4f}")
    print(f"  Std Dev:    {c.std():.4f}")
    print(f"  Variance:   {c.var():.4f}")
    print(f"  MAD:        {mad:.4f}")
    print(f"  IQR:        {iqr:.4f}")
    print(f"  Range:      [{c.min():.4f}, {c.max():.4f}]")
    print(f"  Skewness:   {skew_val:.4f}")
    print(f"  Kurtosis:   {kurt_val:.4f} ({kurt_desc})")

    return {
        "n": len(c),
        "n_missing": series.isna().sum(),
        "mean": c.mean(),
        "median": c.median(),
        "std": c.std(),
        "var": c.var(),
        "mad": mad,
        "iqr": iqr,
        "min": c.min(),
        "max": c.max(),
        "skew": skew_val,
        "kurtosis": kurt_val,
        "kurtosis_desc": kurt_desc,
    }


def normality_check(series: pd.Series, name: str = "") -> Dict[str, Any]:
    """
    Check normality using visual inspection for large n, Shapiro-Wilk for small n.
    
    Args:
        series: Pandas Series to check for normality
        name: Name of the variable for display
        
    Returns:
        Dictionary with normality assessment results
    """
    clean = series.dropna()
    n = len(clean)
    
    result = {"n": n, "normal": None, "method": None, "note": None}

    print(f"\n  --- Normality Check: {name} ---")

    if n <= LARGE_N_THRESHOLD and n > 3:
        stat, p = stats.shapiro(clean)
        print(f"  Shapiro-Wilk: stat={stat:.4f}, p={p:.4f}")
        result["method"] = "Shapiro-Wilk"
        result["stat"] = stat
        result["p"] = p
        
        if p > 0.05:
            print(f"  → Cannot reject normality (p > 0.05)")
            result["normal"] = True
        else:
            print(f"  → Reject normality (p <= 0.05)")
            result["normal"] = False
    else:
        skew_val = stats.skew(clean)
        print(f"  ⚠ n={n} > {LARGE_N_THRESHOLD}: Shapiro-Wilk is overly sensitive.")
        print(f"    Skipping test. Rely on visual inspection (Q-Q, ECDF) instead.")
        print(f"    Skewness = {skew_val:.4f} (|skew| < {SKEW_SYMMETRIC} suggests symmetry)")
        result["method"] = "visual + skewness"
        result["skew"] = skew_val
        result["note"] = "Shapiro-Wilk skipped for large n"

    return result


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


def savefig(name: str, subdir: Optional[str] = None) -> None:
    """Save current figure as PDF and PNG in an optional subdirectory."""
    target_dir = FIGS_DIR
    if subdir:
        target_dir = FIGS_DIR / subdir
        target_dir.mkdir(parents=True, exist_ok=True)
    
    pdf_path = target_dir / f"{name}.pdf"
    png_path = target_dir / f"{name}.png"
    
    plt.savefig(pdf_path, bbox_inches="tight", dpi=300)
    plt.savefig(png_path, bbox_inches="tight", dpi=150)
    print(f"  Saved: {pdf_path} + .png")
