"""
01_load_explore.py — Load each CSV, inspect structure, missing values, duplicates, and red flags
"""
import numpy as np; np.random.seed(42)
DATA_DIR = "../data"
import pandas as pd
import os

files = [
    "hantavirus_clinical.csv",
    "hantavirus_environmental.csv",
    "hantavirus_country_yearly.csv",
    "hantavirus_master.csv",
    "hantavirus_monthly_trends.csv",
    "hantavirus_outbreaks.csv",
    "hantavirus_virus_strains.csv",
    "sources_metadata.csv",
    "data_dictionary.csv",
]

for f in files:
    path = os.path.join(DATA_DIR, f)
    df = pd.read_csv(path)
    print(f"\n{'='*60}")
    print(f"  File: {f}")
    print(f"  Shape: {df.shape[0]} rows × {df.shape[1]} cols")
    print(f"{'='*60}")

    print(f"\n  --- Columns & Dtypes ---")
    for col, dtype in df.dtypes.items():
        print(f"    {col:35s} {str(dtype):10s}")

    print(f"\n  --- Missing Values ---")
    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(1)
    missing_df = pd.DataFrame({"missing": missing, "%": missing_pct})
    missing_df = missing_df[missing_df["missing"] > 0]
    if missing_df.empty:
        print("    (none)")
    else:
        print(missing_df.to_string())

    print(f"\n  --- Duplicates ---")
    dups = df.duplicated().sum()
    print(f"    {dups} duplicate rows ({dups/len(df)*100:.1f}%)")

    print(f"\n  --- Categorical Columns (value counts) ---")
    cat_cols = df.select_dtypes(include=["object"]).columns
    for col in cat_cols:
        n_unique = df[col].nunique()
        print(f"\n    {col} ({n_unique} unique):")
        print(f"      {df[col].value_counts().to_string()}")

    print(f"\n  --- Numeric Columns (min / max) ---")
    num_cols = df.select_dtypes(include=["int64", "float64"]).columns
    for col in num_cols:
        c = df[col].dropna()
        if len(c) > 0:
            print(f"    {col:35s}  min={c.min():12.4f}  max={c.max():12.4f}")
        else:
            print(f"    {col:35s}  (all missing)")

    print(f"\n  --- First 3 Rows ---")
    print(df.head(3).to_string())
