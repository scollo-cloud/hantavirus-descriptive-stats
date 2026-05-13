"""
E1_comparative_violins.py — Comparative violin plots across all key variables
"""
import numpy as np; np.random.seed(42)
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns; sns.set_theme(style="whitegrid")
from scipy import stats
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from helper import load_csv, savefig


def make_violin(data_groups, group_names, title, xlabel, filename, colors=None, figsize=(10, 4)):
    fig, ax = plt.subplots(figsize=figsize)
    parts = ax.violinplot(data_groups, vert=False, showmeans=False, showmedians=False,
                          positions=range(1, len(data_groups)+1), widths=0.6)
    if colors:
        for i, pc in enumerate(parts["bodies"]):
            pc.set_facecolor(colors[i % len(colors)])
            pc.set_alpha(0.5)
    # Add box plots inside + sample size labels
    for i, data in enumerate(data_groups):
        n = len(data)
        if n < 30:
            print(f"  ⚠ {group_names[i]}: n={n} < 30 — violin KDE may be unstable")
        ax.boxplot(data, vert=False, positions=[i+1], widths=0.15, patch_artist=True,
                   boxprops=dict(facecolor="white", alpha=0.7),
                   medianprops=dict(color="red", linewidth=2),
                   showfliers=False)
        ax.text(data.max() + (data.max() - data.min()) * 0.05, i+1,
                f"n={n}", va="center", fontsize=8, alpha=0.7)
    ax.set_yticks(range(1, len(data_groups) + 1))
    ax.set_yticklabels(group_names)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    fig.subplots_adjust(left=0.3)
    plt.tight_layout()
    savefig(filename, subdir="comparative")
    plt.close()

# ── 1. incubation_days by severity ──
df = load_csv("hantavirus_clinical.csv")
order = ["Mild", "Moderate", "Severe", "Critical"]
groups = [df[df["severity"] == s]["incubation_days"].dropna() for s in order]
make_violin(groups, order, "Incubation Days by Severity", "Days",
            "compare_incubation_severity", colors=["green", "goldenrod", "darkorange", "red"])
for s, g in zip(order, groups):
    print(f"  Incubation by {s:10s}: n={len(g):4d}, mean={g.mean():.1f}, median={g.median():.0f}")

# ── 2. incubation_days by outcome ──
groups_out = [df[df["outcome"] == o]["incubation_days"].dropna() for o in ["Recovered", "Deceased"]]
make_violin(groups_out, ["Recovered", "Deceased"], "Incubation Days by Outcome", "Days",
            "compare_incubation_outcome", colors=["steelblue", "red"])
for o, g in zip(["Recovered", "Deceased"], groups_out):
    print(f"  Incubation by {o:10s}: n={len(g):4d}, mean={g.mean():.1f}, median={g.median():.0f}")

# ── 3. incubation_days by syndrome ──
groups_syn = [df[df["syndrome"] == s]["incubation_days"].dropna() for s in ["HPS", "HFRS"]]
make_violin(groups_syn, ["HPS", "HFRS"], "Incubation Days by Syndrome", "Days",
            "compare_incubation_syndrome", colors=["steelblue", "darkorange"])
for s, g in zip(["HPS", "HFRS"], groups_syn):
    print(f"  Incubation by {s:4s}: n={len(g):4d}, mean={g.mean():.1f}, median={g.median():.0f}")

# ── 4. hospital_days by severity ──
groups = [df[df["severity"] == s]["hospital_days"].dropna() for s in order]
make_violin(groups, order, "Hospital Days by Severity", "Days",
            "compare_hospital_severity", colors=["green", "goldenrod", "darkorange", "red"])

# ── 5. avg_temp_c by biome ──
df_env = load_csv("hantavirus_environmental.csv")
# Group biomes by mean temp for sorted display
biome_means = df_env.groupby("biome")["avg_temp_c"].mean().sort_values()
groups_temp = [df_env[df_env["biome"] == b]["avg_temp_c"].dropna() for b in biome_means.index]
make_violin(groups_temp, [f"{b}" for b in biome_means.index],
            "Temperature by Biome (sorted coldest → warmest)", "Temperature (°C)",
            "compare_temp_biome", colors=["blue"] * 14, figsize=(10, 7))

# ── 6. rainfall_mm by biome ──
biome_rain = df_env.groupby("biome")["rainfall_mm"].mean().sort_values()
groups_rain = [df_env[df_env["biome"] == b]["rainfall_mm"].dropna() for b in biome_rain.index]
make_violin(groups_rain, [f"{b}" for b in biome_rain.index],
            "Rainfall by Biome (sorted driest → wettest)", "Rainfall (mm)",
            "compare_rain_biome", colors=["blue"] * 14, figsize=(10, 7))

# ── 7. confirmed_cases by syndrome (no-outliers for readability) ──
df_yr = load_csv("hantavirus_country_yearly.csv")
hps_cases = df_yr[df_yr["syndrome"] == "HPS"]["confirmed_cases"]
hfrs_cases = df_yr[df_yr["syndrome"] == "HFRS"]["confirmed_cases"]
# Filter HFRS outliers for readability
q1_hf, q3_hf = hfrs_cases.quantile(0.25), hfrs_cases.quantile(0.75)
upper_hf = q3_hf + 1.5 * (q3_hf - q1_hf)
hfrs_clean = hfrs_cases[hfrs_cases <= upper_hf]

fig, axes = plt.subplots(1, 2, figsize=(14, 4))
# All data
axes[0].violinplot([hps_cases, hfrs_cases], vert=False, showmedians=True, positions=[1, 2])
axes[0].set_yticks([1, 2])
axes[0].set_yticklabels([f"HPS (n={len(hps_cases)})", f"HFRS (n={len(hfrs_cases)})"])
axes[0].set_title("Confirmed Cases by Syndrome — All Data")
axes[0].set_xlabel("Cases")

# Clean (no outliers)
axes[1].violinplot([hps_cases, hfrs_clean], vert=False, showmedians=True, positions=[1, 2])
axes[1].set_yticks([1, 2])
axes[1].set_yticklabels([f"HPS (n={len(hps_cases)})", f"HFRS (no outliers, n={len(hfrs_clean)})"])
axes[1].set_title("Confirmed Cases by Syndrome — HFRS Outliers Removed")
axes[1].set_xlabel("Cases")
plt.tight_layout()
savefig("compare_cases_syndrome", subdir="comparative")
plt.close()

print(f"\n  Cases by syndrome:")
print(f"  HPS:  n={len(hps_cases)}, mean={hps_cases.mean():.0f}, median={hps_cases.median():.0f}")
print(f"  HFRS: n={len(hfrs_cases)}, mean={hfrs_cases.mean():.0f}, median={hfrs_cases.median():.0f}")

# ── 8. case_fatality_rate by syndrome (already done in D8, just confirm) ──
print(f"\n  CFR by syndrome (already in D8):")
for syn in ["HPS", "HFRS"]:
    sub = df_yr[df_yr["syndrome"] == syn]["case_fatality_rate"]
    print(f"  {syn}: n={len(sub)}, mean={sub.mean():.3f}, median={sub.median():.3f}")
