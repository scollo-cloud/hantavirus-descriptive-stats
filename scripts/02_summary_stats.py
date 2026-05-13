"""
02_summary_stats.py — Summary statistics for every numeric column across all datasets
"""
import numpy as np; np.random.seed(42)
DATA_DIR = "../data"
import pandas as pd
from scipy import stats
import os


files = [
    "hantavirus_clinical.csv",
    "hantavirus_environmental.csv",
    "hantavirus_country_yearly.csv",
    "hantavirus_master.csv",
    "hantavirus_monthly_trends.csv",
    "hantavirus_outbreaks.csv",
]

for f in files:
    df = pd.read_csv(os.path.join(DATA_DIR, f))
    num_cols = df.select_dtypes(include=["int64", "float64"]).columns
    print(f"\n{'='*65}")
    print(f"  {f}")
    print(f"{'='*65}")

    for col in num_cols:
        c = df[col].dropna()
        q1, q3 = c.quantile(0.25), c.quantile(0.75)
        mad = (c - c.median()).abs().median()
        skew_val = stats.skew(c)
        kurt_val = stats.kurtosis(c)

        print(f"\n  {col}")
        print(f"  {'─'*40}")
        print(f"    Count:        {len(c):>8d}")
        print(f"    Mean:         {c.mean():>10.4f}")
        print(f"    Median:       {c.median():>10.4f}")
        print(f"    Std Dev:      {c.std():>10.4f}")
        print(f"    Variance:     {c.var():>10.4f}")
        print(f"    MAD:          {mad:>10.4f}")
        print(f"    IQR:          {q3 - q1:>10.4f}")
        print(f"    Range:        [{c.min():>8.4f}, {c.max():>8.4f}]")
        print(f"    Skewness:     {skew_val:>10.4f}")
        print(f"    Kurtosis:     {kurt_val:>10.4f}")
