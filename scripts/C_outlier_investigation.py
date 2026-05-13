"""
C_outlier_investigation.py — Systematic outlier investigation
For every numeric column: flag by IQR, print context, decide keep/remove
"""
import numpy as np; np.random.seed(42)
import pandas as pd
from scipy import stats
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from helper import load_csv, iqr_outliers

DECISIONS = []  # track keep/remove for each

def investigate(series, df, name, context_cols, is_count=False):
    q1, q3 = series.quantile(0.25), series.quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    
    outliers_series = iqr_outliers(series)
    outliers = df.loc[outliers_series.index]
    
    if len(outliers) == 0:
        print(f"\n  {name}: no outliers flagged")
        return
    
    print(f"\n{'='*70}")
    print(f"  {name} — {len(outliers)} outliers flagged (IQR bounds: [{lower:.2f}, {upper:.2f}])")
    print(f"{'='*70}")
    
    # Show each outlier with context
    cols = [col for col in context_cols if col in outliers.columns] + [series.name]
    print(outliers[cols].sort_values(series.name, ascending=False).head(20).to_string(index=False))
    
    # Numbers
    kept = outliers[series.name].count()
    DECISIONS.append({
        "variable": name,
        "n_outliers": len(outliers),
        "pct": len(outliers) / len(series) * 100,
        "bounds": f"[{lower:.2f}, {upper:.2f}]",
        "verdict": "keep (real)"  # default — change after discussion
    })
    return outliers

# ── Clinical: incubation_days, hospital_days, icu_days ──
df_clin = load_csv("hantavirus_clinical.csv")
ctx = ["syndrome", "virus_strain", "severity", "outcome", "age_group", "gender", "country_iso3"]

investigate(df_clin["incubation_days"], df_clin, "incubation_days", ctx)
investigate(df_clin["hospital_days"], df_clin, "hospital_days", ctx + ["icu_admission"])
investigate(df_clin["icu_days"], df_clin, "icu_days", ctx)

# ── Environmental: temp, rainfall, rodent ──
df_env = load_csv("hantavirus_environmental.csv")
env_ctx = ["region", "biome", "year", "quarter", "exposure_setting", "rodent_host_species"]
investigate(df_env["avg_temp_c"], df_env, "avg_temp_c", env_ctx)
investigate(df_env["rainfall_mm"], df_env, "rainfall_mm", env_ctx)
investigate(df_env["rodent_abundance_index"], df_env, "rodent_abundance_index", env_ctx)
investigate(df_env["deforestation_km2"], df_env, "deforestation_km2", env_ctx)

# ── Country yearly: confirmed_cases, cfr ──
df_yr = load_csv("hantavirus_country_yearly.csv")
yr_ctx = ["country", "who_region", "syndrome", "year"]
investigate(df_yr["confirmed_cases"], df_yr, "confirmed_cases", yr_ctx, is_count=True)
investigate(df_yr["case_fatality_rate"], df_yr, "case_fatality_rate", yr_ctx)

# ── Summary ──
print(f"\n\n{'='*70}")
print(f"  OUTLIER INVESTIGATION SUMMARY")
print(f"{'='*70}")
dec_df = pd.DataFrame(DECISIONS)
dec_df["verdict"] = "keep (real)"  # all default to keep pending discussion
print(dec_df.to_string(index=False))
print(f"\n  All outliers default to KEEP unless we find evidence of data errors.")
print(f"  Next step: review each and decide if any should be removed.")
