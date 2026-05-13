"""
02_summary_stats.py — Summary statistics for every numeric column across all datasets
"""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

import pandas as pd
from helper import DATA_DIR, load_csv, print_summary

files = [
    "hantavirus_clinical.csv",
    "hantavirus_environmental.csv",
    "hantavirus_country_yearly.csv",
    "hantavirus_master.csv",
    "hantavirus_monthly_trends.csv",
    "hantavirus_outbreaks.csv",
]

for f in files:
    try:
        df = load_csv(f)
    except (FileNotFoundError, ValueError) as e:
        print(f"  ⚠ {e}")
        continue

    num_cols = df.select_dtypes(include=["int64", "float64"]).columns
    print(f"\n{'#'*65}")
    print(f"  FILE: {f}")
    print(f"{'#'*65}")

    for col in num_cols:
        print_summary(col, df[col])
