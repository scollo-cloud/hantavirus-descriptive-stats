"""
D2b_hospital_investigation.py — Investigate why hospital_days is bimodal
Tests: severity, outcome, syndrome, age_group
"""
import numpy as np; np.random.seed(42)
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns; sns.set_theme(style="whitegrid")
from scipy import stats
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from helper import load_csv, savefig

df = load_csv("hantavirus_clinical.csv")

# ── Hypothesis A: Split by Severity ──
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
severity_order = ["Mild", "Moderate", "Severe", "Critical"]
colors = {"Mild": "green", "Moderate": "goldenrod", "Severe": "darkorange", "Critical": "red"}

# A1: Overlaid histograms
for sev in severity_order:
    subset = df[df["severity"] == sev]["hospital_days"].dropna()
    axes[0].hist(subset, bins=np.arange(1, 29) - 0.5, alpha=0.5,
                 label=f"{sev} (n={len(subset)})", color=colors[sev])
axes[0].set_title("Hospital Days by Severity")
axes[0].set_xlabel("Days")
axes[0].set_ylabel("Frequency")
axes[0].legend()

# A2: Violin plots per severity
order_sev = [s for s in severity_order if s in df["severity"].unique()]
data_sev = [df[df["severity"] == s]["hospital_days"].dropna() for s in order_sev]
parts = axes[1].violinplot(data_sev, vert=False, showmedians=True)
for i, pc in enumerate(parts["bodies"]):
    pc.set_facecolor(list(colors.values())[i])
    pc.set_alpha(0.6)
axes[1].set_yticks(range(1, len(order_sev) + 1))
axes[1].set_yticklabels(order_sev)
axes[1].set_title("Hospital Days by Severity (Violin)")
axes[1].set_xlabel("Days")

plt.tight_layout()
savefig("hospital_by_severity", subdir="clinical")
plt.close()

# ── Hypothesis B: Split by Outcome ──
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
outcome_colors = {"Recovered": "steelblue", "Deceased": "red"}

for out in ["Recovered", "Deceased"]:
    subset = df[df["outcome"] == out]["hospital_days"].dropna()
    axes[0].hist(subset, bins=np.arange(1, 29) - 0.5, alpha=0.6,
                 label=f"{out} (n={len(subset)})", color=outcome_colors[out])
axes[0].set_title("Hospital Days by Outcome")
axes[0].set_xlabel("Days")
axes[0].set_ylabel("Frequency")
axes[0].legend()

order_out = [o for o in ["Recovered", "Deceased"] if o in df["outcome"].unique()]
data_out = [df[df["outcome"] == o]["hospital_days"].dropna() for o in order_out]
parts = axes[1].violinplot(data_out, vert=False, showmedians=True)
for i, pc in enumerate(parts["bodies"]):
    pc.set_facecolor(list(outcome_colors.values())[i])
    pc.set_alpha(0.6)
axes[1].set_yticks(range(1, len(order_out) + 1))
axes[1].set_yticklabels(order_out)
axes[1].set_title("Hospital Days by Outcome (Violin)")
axes[1].set_xlabel("Days")

plt.tight_layout()
savefig("hospital_by_outcome", subdir="clinical")
plt.close()

# ── Hypothesis C: Split by Syndrome ──
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
syn_colors = {"HPS": "steelblue", "HFRS": "darkorange"}

for syn in ["HPS", "HFRS"]:
    subset = df[df["syndrome"] == syn]["hospital_days"].dropna()
    axes[0].hist(subset, bins=np.arange(1, 29) - 0.5, alpha=0.6,
                 label=f"{syn} (n={len(subset)})", color=syn_colors[syn])
axes[0].set_title("Hospital Days by Syndrome")
axes[0].set_xlabel("Days")
axes[0].set_ylabel("Frequency")
axes[0].legend()

order_syn = [s for s in ["HPS", "HFRS"] if s in df["syndrome"].unique()]
data_syn = [df[df["syndrome"] == s]["hospital_days"].dropna() for s in order_syn]
parts = axes[1].violinplot(data_syn, vert=False, showmedians=True)
for i, pc in enumerate(parts["bodies"]):
    pc.set_facecolor(list(syn_colors.values())[i])
    pc.set_alpha(0.6)
axes[1].set_yticks(range(1, len(order_syn) + 1))
axes[1].set_yticklabels(order_syn)
axes[1].set_title("Hospital Days by Syndrome (Violin)")
axes[1].set_xlabel("Days")

plt.tight_layout()
savefig("hospital_by_syndrome", subdir="clinical")
plt.close()

# ── Hypothesis D: Split by Age Group ──
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
age_order = ["0-14", "15-29", "30-44", "45-59", "60+"]
age_colors = {"0-14": "purple", "15-29": "blue", "30-44": "green",
              "45-59": "orange", "60+": "red"}

for age in age_order:
    subset = df[df["age_group"] == age]["hospital_days"].dropna()
    axes[0].hist(subset, bins=np.arange(1, 29) - 0.5, alpha=0.4,
                 label=f"{age} (n={len(subset)})", color=age_colors[age])
axes[0].set_title("Hospital Days by Age Group")
axes[0].set_xlabel("Days")
axes[0].set_ylabel("Frequency")
axes[0].legend()

order_age = [a for a in age_order if a in df["age_group"].unique()]
data_age = [df[df["age_group"] == a]["hospital_days"].dropna() for a in order_age]
parts = axes[1].violinplot(data_age, vert=False, showmedians=True)
for i, pc in enumerate(parts["bodies"]):
    pc.set_facecolor(list(age_colors.values())[i])
    pc.set_alpha(0.6)
axes[1].set_yticks(range(1, len(order_age) + 1))
axes[1].set_yticklabels(order_age)
axes[1].set_title("Hospital Days by Age Group (Violin)")
axes[1].set_xlabel("Days")

plt.tight_layout()
savefig("hospital_by_age", subdir="clinical")
plt.close()

# ── Print summary stats for each split ──
print(f"{'='*70}")
print(f"  HOSPITAL DAYS — Subgroup Investigation")
print(f"{'='*70}")

for factor_name, factor_col in [("Severity", "severity"), ("Outcome", "outcome"),
                                 ("Syndrome", "syndrome"), ("Age Group", "age_group")]:
    print(f"\n  ─── {factor_name} ───")
    for group in df[factor_col].unique():
        subset = df[df[factor_col] == group]["hospital_days"].dropna()
        print(f"  {group:15s}  n={len(subset):5d}  mean={subset.mean():.1f}  median={subset.median():.0f}  IQR={subset.quantile(0.75)-subset.quantile(0.25):.0f}")
