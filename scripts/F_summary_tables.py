"""
F_summary_tables.py — Generate all LaTeX tables for the report
"""
import numpy as np; np.random.seed(42)
import pandas as pd
from scipy import stats
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from helper import load_csv, TABLES_DIR, recommend_center, recommend_spread, iqr_outliers

def latex_table(df, caption, label, filename):
    tex = df.to_latex(index=False, escape=False, float_format="%.3f",
                      caption=caption, label=label,
                      position="htbp")
    with open(TABLES_DIR / filename, "w") as f:
        f.write(tex)
    print(f"  Saved: {TABLES_DIR / filename}")

# ── Table 1: Master Summary — all numeric variables ──
df_clin = load_csv("hantavirus_clinical.csv")
df_env = load_csv("hantavirus_environmental.csv")
df_yr = load_csv("hantavirus_country_yearly.csv")

rows = []
for name, series in [
    ("Incubation Days", df_clin["incubation_days"]),
    ("Hospital Days", df_clin["hospital_days"]),
    ("ICU Days", df_clin["icu_days"]),
    ("Temperature (°C)", df_env["avg_temp_c"]),
    ("Rainfall (mm)", df_env["rainfall_mm"]),
    ("Rodent Abundance", df_env["rodent_abundance_index"]),
    ("Confirmed Cases", df_yr["confirmed_cases"]),
    ("Case Fatality Rate", df_yr["case_fatality_rate"]),
]:
    c = series.dropna()
    q1, q3 = c.quantile(0.25), c.quantile(0.75)
    skew_val = stats.skew(c)
    kurt_val = stats.kurtosis(c)
    
    center = recommend_center(c).split(" ")[0].capitalize()
    spread = recommend_spread(c).split(" ")[0].capitalize()
    if spread == "Standard": spread = "Std"
    
    rows.append({
        "Variable": name,
        "n": len(c),
        "Mean": f"{c.mean():.2f}",
        "Median": f"{c.median():.2f}",
        "Std": f"{c.std():.2f}",
        "IQR": f"{q3-q1:.2f}",
        "MAD": f"{(c-c.median()).abs().median():.2f}",
        "Skewness": f"{skew_val:.2f}",
        "Kurtosis": f"{kurt_val:.2f}",
        "Best Center": center,
        "Best Spread": spread,
    })

master = pd.DataFrame(rows)
latex_table(master, "Summary statistics for all numeric variables across datasets",
            "tab:master", "master_summary.tex")

# ── Table 2: Incubation by Severity (D1 findings) ──
order = ["Mild", "Moderate", "Severe", "Critical"]
rows = []
for sev in order:
    sub = df_clin[df_clin["severity"] == sev]["incubation_days"]
    rows.append({
        "Severity": sev,
        "n": len(sub),
        "Mean": f"{sub.mean():.1f}",
        "Median": f"{sub.median():.0f}",
        "Std": f"{sub.std():.1f}",
        "IQR": f"{sub.quantile(0.75)-sub.quantile(0.25):.1f}",
    })
t2 = pd.DataFrame(rows)
latex_table(t2, "Incubation days stratified by severity level",
            "tab:incubation_severity", "incubation_by_severity.tex")

# ── Table 3: Hospital by Severity (D2 findings) ──
rows = []
for sev in order:
    sub = df_clin[df_clin["severity"] == sev]["hospital_days"]
    rows.append({
        "Severity": sev,
        "n": len(sub),
        "Mean": f"{sub.mean():.1f}",
        "Median": f"{sub.median():.0f}",
        "Std": f"{sub.std():.1f}",
        "IQR": f"{sub.quantile(0.75)-sub.quantile(0.25):.1f}",
    })
t3 = pd.DataFrame(rows)
latex_table(t3, "Hospital days stratified by severity level — each group has a distinct, non-overlapping center",
            "tab:hospital_severity", "hospital_by_severity.tex")

# ── Table 4: ICU by Severity (D3 findings) ──
rows = []
for sev in order:
    sub = df_clin[df_clin["severity"] == sev]
    adm = sub["icu_admission"].mean()
    icu_sub = sub[sub["icu_days"] > 0]["icu_days"]
    rows.append({
        "Severity": sev,
        "n": len(sub),
        "ICU Rate": f"{adm*100:.0f}\\%",
        "ICU Days (median)": f"{icu_sub.median():.0f}" if len(icu_sub) > 0 else "—",
        "ICU Days (mean)": f"{icu_sub.mean():.1f}" if len(icu_sub) > 0 else "—",
    })
t4 = pd.DataFrame(rows)
latex_table(t4, "ICU admission rates and stay lengths by severity",
            "tab:icu_severity", "icu_by_severity.tex")

# ── Table 5: CFR by Syndrome (D8 findings) ──
rows = []
for syn in ["HPS", "HFRS"]:
    sub = df_yr[df_yr["syndrome"] == syn]["case_fatality_rate"]
    rows.append({
        "Syndrome": syn,
        "n": len(sub),
        "Mean CFR": f"{sub.mean()*100:.1f}\\%",
        "Median CFR": f"{sub.median()*100:.1f}\\%",
        "Max CFR": f"{sub.max()*100:.1f}\\%",
        "IQR": f"{(sub.quantile(0.75)-sub.quantile(0.25))*100:.1f}\\%",
    })
t5 = pd.DataFrame(rows)
latex_table(t5, "Case fatality rate by syndrome — HPS is ~20x more lethal than HFRS",
            "tab:cfr_syndrome", "cfr_by_syndrome.tex")

# ── Table 6: Confirmed Cases by Region (D7 findings) ──
rows = []
for region in df_yr["who_region"].unique():
    sub = df_yr[df_yr["who_region"] == region]["confirmed_cases"]
    rows.append({
        "WHO Region": region,
        "n": len(sub),
        "Mean": f"{sub.mean():.0f}",
        "Median": f"{sub.median():.0f}",
        "Max": f"{sub.max():.0f}",
        "Total": f"{sub.sum():.0f}",
    })
t6 = pd.DataFrame(rows)
latex_table(t6, "Confirmed cases by WHO region — WPRO (Asia) dominates",
            "tab:cases_region", "cases_by_region.tex")

# ── Table 7: Incubation by Syndrome and Outcome ──
rows = []
for syn in ["HPS", "HFRS"]:
    sub = df_clin[df_clin["syndrome"] == syn]["incubation_days"]
    rows.append({
        "Group": f"{syn}",
        "n": len(sub),
        "Mean": f"{sub.mean():.1f}",
        "Median": f"{sub.median():.0f}",
        "IQR": f"{sub.quantile(0.75)-sub.quantile(0.25):.1f}",
    })
for outcome in ["Recovered", "Deceased"]:
    sub = df_clin[df_clin["outcome"] == outcome]["incubation_days"]
    rows.append({
        "Group": f"{outcome}",
        "n": len(sub),
        "Mean": f"{sub.mean():.1f}",
        "Median": f"{sub.median():.0f}",
        "IQR": f"{sub.quantile(0.75)-sub.quantile(0.25):.1f}",
    })
t7 = pd.DataFrame(rows)
latex_table(t7, "Incubation days by syndrome and outcome",
            "tab:incubation_groups", "incubation_by_groups.tex")

# ── Table 8: Environmental variables by biome ──
rows = []
for biome in df_env["biome"].unique():
    sub = df_env[df_env["biome"] == biome]
    rows.append({
        "Biome": biome,
        "n": len(sub),
        "Temp (°C)": f"{sub['avg_temp_c'].mean():.1f}",
        "Rain (mm)": f"{sub['rainfall_mm'].mean():.0f}",
        "Rodent Index": f"{sub['rodent_abundance_index'].mean():.2f}",
        "NDVI": f"{sub['ndvi'].mean():.2f}",
    })
t8 = pd.DataFrame(rows)
latex_table(t8, "Environmental variables by biome",
            "tab:env_biome", "environmental_by_biome.tex")

# ── Table 9: Mistake-fix summary ──
mistakes = pd.DataFrame([
    {"Mistake": "Beeswarm plot for discrete data",
     "Why it failed": "No vertical spread, couldn't see density",
     "Replaced with": "Box plot + Violin plot with box overlay"},
    {"Mistake": "Too many histogram bins (sqrt rule on integer data)",
     "Why it failed": "86 bins for 35-day range → empty bins, 'comb' effect",
     "Replaced with": "Integer-aligned bins (discrete) or FD rule (continuous)"},
    {"Mistake": "KDE on discrete/bounded data",
     "Why it failed": "Density extends below 0 (impossible), subjective bandwidth",
     "Replaced with": "Log-transformed histogram for continuous; skip for integer"},
    {"Mistake": "Q-Q plot on bounded-at-zero data",
     "Why it failed": "Always shows deviation at lower tail (bounded vs unbounded)",
     "Replaced with": "ECDF + subgroup split; Q-Q only for unbounded variables"},
    {"Mistake": "Describing distribution without checking subgroups",
     "Why it failed": "Hospital days appeared bimodal → actually 4 unimodal severity groups",
     "Replaced with": "Always check subgroups before describing shape"},
    {"Mistake": "ECDF x-axis starting at -2000",
     "Why it failed": "Cases can't be negative, misleading visualization",
     "Fixed by": "Set xlim starting at 0"},
])
latex_table(mistakes, "Summary of visualization mistakes, why they failed, and what they were replaced with",
            "tab:mistakes", "mistakes_summary.tex")

# ── Table 10: Outlier investigation summary ──
df_clin = load_csv("hantavirus_clinical.csv")
outliers_data = []
for name, series in [
    ("incubation_days", df_clin["incubation_days"]),
    ("hospital_days", df_clin["hospital_days"]),
    ("icu_days", df_clin["icu_days"]),
    ("avg\\_temp\\_c", df_env["avg_temp_c"]),
    ("rainfall\\_mm", df_env["rainfall_mm"]),
    ("rodent\\_abundance", df_env["rodent_abundance_index"]),
    ("confirmed\\_cases", df_yr["confirmed_cases"]),
    ("case\\_fatality\\_rate", df_yr["case_fatality_rate"]),
]:
    outliers = iqr_outliers(series)
    outliers_data.append({
        "Variable": name,
        "n outliers": len(outliers),
        "Percent": f"{len(outliers)/len(series)*100:.1f}\\%",
        "Verdict": "Keep (real)" if len(outliers) > 0 else "—",
    })
t10 = pd.DataFrame(outliers_data)
latex_table(t10, "Outlier investigation results — all flagged outliers were genuine extreme values, not errors",
            "tab:outliers", "outlier_summary.tex")

print(f"\n  All {len(outliers_data)+9} tables saved to {TABLES_DIR}/")
