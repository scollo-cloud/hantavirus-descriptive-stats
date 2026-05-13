"""
D3b_icu_investigation.py — Investigate icu_days patterns by severity and admission status
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
icu = df["icu_days"].dropna()
icu_nonzero = icu[icu > 0]

# ── Part 1: icu_admission as a binary ──
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
adm_colors = {0: "lightgray", 1: "steelblue"}
for adm in [0, 1]:
    subset = df[df["icu_admission"] == adm]["hospital_days"].dropna()
    axes[0].hist(subset, bins=np.arange(0.5, 28), alpha=0.6,
                 label=f"ICU={adm} (n={len(subset)})", color=adm_colors[adm])
axes[0].set_title("Hospital Days by ICU Admission")
axes[0].set_xlabel("Hospital Days")
axes[0].set_ylabel("Frequency")
axes[0].legend()

# ICU admission rate by severity
sev_order = ["Mild", "Moderate", "Severe", "Critical"]
adm_rates = []
for sev in sev_order:
    sub = df[df["severity"] == sev]
    rate = sub["icu_admission"].mean()
    adm_rates.append(rate)
    print(f"  ICU admission rate — {sev:10s}: {rate*100:.1f}% (n={len(sub)})")

axes[1].bar(sev_order, adm_rates, color=["green", "goldenrod", "darkorange", "red"], alpha=0.7)
axes[1].set_title("ICU Admission Rate by Severity")
axes[1].set_ylabel("Proportion admitted to ICU")
axes[1].set_ylim(0, 1)
plt.tight_layout()
savefig("icu_by_admission")
plt.close()

# ── Part 2: ICU days (>0) split by severity ──
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
colors = {"Mild": "green", "Moderate": "goldenrod", "Severe": "darkorange", "Critical": "red"}

# Only patients who actually went to ICU
icu_df = df[df["icu_admission"] == 1]

for sev in sev_order:
    subset = icu_df[icu_df["severity"] == sev]["icu_days"].dropna()
    axes[0].hist(subset, bins=np.arange(2.5, 17), alpha=0.5,
                 label=f"{sev} (n={len(subset)})", color=colors[sev])
axes[0].set_title("ICU Days (>0) by Severity")
axes[0].set_xlabel("ICU Days")
axes[0].set_ylabel("Frequency")
axes[0].legend()

order_sev = [s for s in sev_order if s in icu_df["severity"].unique()]
data_sev = [icu_df[icu_df["severity"] == s]["icu_days"].dropna() for s in order_sev]
parts = axes[1].violinplot(data_sev, vert=False, showmedians=True)
for i, pc in enumerate(parts["bodies"]):
    pc.set_facecolor(list(colors.values())[i])
    pc.set_alpha(0.6)
axes[1].set_yticks(range(1, len(order_sev) + 1))
axes[1].set_yticklabels(order_sev)
axes[1].set_title("ICU Days (>0) by Severity (Violin)")
axes[1].set_xlabel("ICU Days")
plt.tight_layout()
savefig("icu_by_severity")
plt.close()

# ── Part 3: Overlaid histogram: all vs non-zero only ──
fig, axes = plt.subplots(1, 2, figsize=(14, 4))

# Left: ALL patients
n_all = len(icu)
nz = len(icu_nonzero)
axes[0].hist(icu, bins=np.arange(-0.5, 17), color="steelblue", edgecolor="white", alpha=0.7)
axes[0].set_title(f"ICU Days — All Patients (n={n_all}, {nz} admitted)")
axes[0].set_xlabel("Days")
axes[0].set_ylabel("Frequency")

# Right: ICU-only (non-zero) — with proper integer bins
axes[1].hist(icu_nonzero, bins=np.arange(2.5, 17), color="darkorange",
             edgecolor="white", alpha=0.7)
axes[1].set_title(f"ICU Days — Admitted Only (n={nz})")
axes[1].set_xlabel("Days")
axes[1].set_ylabel("Frequency")
# Add mean and median lines
axes[1].axvline(icu_nonzero.mean(), color="blue", linestyle="--", label=f"Mean={icu_nonzero.mean():.1f}")
axes[1].axvline(icu_nonzero.median(), color="red", linestyle="-", label=f"Median={icu_nonzero.median():.0f}")
axes[1].legend()
plt.tight_layout()
savefig("icu_split")

plt.close()

# ── Part 4: Q-Q for non-zero only ──
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
stats.probplot(icu, dist="norm", plot=axes[0])
axes[0].set_title("Q-Q Plot — All ICU Days (zero spike dominates)")
stats.probplot(icu_nonzero, dist="norm", plot=axes[1])
axes[1].set_title("Q-Q Plot — ICU Days > 0 Only")
plt.tight_layout()
savefig("icu_qq_split")
plt.close()

# ── Print summary ──
print(f"\n  ─── ICU ADMISSION RATES BY SEVERITY ───")
for sev in sev_order:
    sub = df[df["severity"] == sev]
    rate = sub["icu_admission"].mean()
    print(f"  {sev:10s}: admission rate = {rate*100:.1f}% (n={len(sub)})")

print(f"\n  ─── ICU DAYS (>0) BY SEVERITY ───")
for sev in sev_order:
    subset = icu_df[icu_df["severity"] == sev]["icu_days"]
    print(f"  {sev:10s}: n={len(subset):4d}, mean={subset.mean():.1f}, median={subset.median():.0f}")

print(f"\n  ─── Q-Q PLOT NOTE ───")
print(f"  All data Q-Q: dominated by zero spike → points on lower end are flat")
print(f"  Non-zero Q-Q: removes the spike, shows real ICU-stay distribution")
print(f"  Negative values in Q-Q: theoretical quantiles can be negative even if data isn't")
print(f"  That's fine — it just means 'bounded at zero, so not normal'")
