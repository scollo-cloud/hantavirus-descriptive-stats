"""
D2_hospital_days.py — Full distribution analysis of hospital_days
"""
import numpy as np; np.random.seed(42)
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns; sns.set_theme(style="whitegrid")
from scipy import stats
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from helper import load_csv, savefig, print_summary, normality_check

df = load_csv("hantavirus_clinical.csv")
hosp = df["hospital_days"].dropna()
n = len(hosp)

FIGS_DIR = "../figures"

# ── 1. Box Plot ──
fig, ax = plt.subplots(figsize=(10, 2.5))
ax.boxplot(hosp, vert=False, patch_artist=True, widths=0.3,
           boxprops=dict(facecolor="steelblue", alpha=0.6),
           medianprops=dict(color="red", linewidth=2))
ax.set_title("Hospital Days — Box Plot")
ax.set_xlabel("Days")
ax.text(0.02, 0.85, f"n = {n}", transform=ax.transAxes, fontsize=9, alpha=0.7)
savefig("hospital_boxplot")
plt.close()

# ── 2. Violin Plot with Box Overlay ──
fig, ax = plt.subplots(figsize=(10, 3))
parts = ax.violinplot(hosp, vert=False, showmeans=False, showmedians=False, widths=0.4)
for pc in parts["bodies"]:
    pc.set_facecolor("steelblue")
    pc.set_alpha(0.5)
ax.boxplot(hosp, vert=False, widths=0.15, patch_artist=True,
           boxprops=dict(facecolor="lightblue", alpha=0.7),
           medianprops=dict(color="red", linewidth=2))
ax.set_title("Hospital Days — Violin Plot with Box Overlay")
ax.set_xlabel("Days")
ax.text(0.02, 0.85, f"n = {n}", transform=ax.transAxes, fontsize=9, alpha=0.7)
ax.scatter(hosp.mean(), 1, color="darkblue", s=50, marker="D", zorder=5, label=f"Mean ({hosp.mean():.1f})")
ax.legend(loc="upper right")
savefig("hospital_violin")
plt.close()

# ── 3. Histogram (integer bins + FD rule) ──
min_val, max_val = hosp.min(), hosp.max()
bins_int = np.arange(min_val, max_val + 2) - 0.5
bins_fd = int(np.ceil((max_val - min_val) / (2 * stats.iqr(hosp) / n**(1/3))))

fig, axes = plt.subplots(1, 2, figsize=(14, 4))
axes[0].hist(hosp, bins=bins_int, color="steelblue", edgecolor="white", alpha=0.7)
axes[0].set_title(f"Hospital Days — Integer Bins")
axes[0].set_xlabel("Days")
axes[0].set_ylabel("Frequency")

axes[1].hist(hosp, bins=bins_fd, color="steelblue", edgecolor="white", alpha=0.7)
axes[1].set_title(f"Hospital Days — FD Rule ({bins_fd} bins)")
axes[1].set_xlabel("Days")
axes[1].set_ylabel("Frequency")
plt.tight_layout()
savefig("hospital_histogram")
plt.close()

# ── 4. Log-transformed histogram ──
log_hosp = np.log(hosp)
log_bins = int(np.sqrt(n))

fig, axes = plt.subplots(1, 2, figsize=(14, 4))
axes[0].hist(hosp, bins=bins_fd, color="steelblue", edgecolor="white", alpha=0.7)
axes[0].set_title("Hospital Days — Original Scale")
axes[0].set_xlabel("Days")
axes[0].set_ylabel("Frequency")

axes[1].hist(log_hosp, bins=log_bins, color="darkorange", edgecolor="white", alpha=0.7)
axes[1].set_title("Hospital Days — Log-Transformed")
axes[1].set_xlabel("log(Days)")
axes[1].set_ylabel("Frequency")
log_stat, log_p = stats.shapiro(log_hosp)
axes[1].text(0.05, 0.95, f"Shapiro p={log_p:.4f}", transform=axes[1].transAxes,
             fontsize=9, verticalalignment="top",
             color="green" if log_p > 0.05 else "red")
plt.tight_layout()
savefig("hospital_log_histogram")
plt.close()

# ── 5. ECDF ──
fig, ax = plt.subplots(figsize=(8, 4))
ax.hist(hosp, bins=bins_fd, density=True, cumulative=True,
        color="steelblue", edgecolor="white", alpha=0.7, label="ECDF")
mu, sigma = hosp.mean(), hosp.std()
x = np.linspace(hosp.min(), hosp.max(), 200)
ax.plot(x, stats.norm.cdf(x, mu, sigma), "r--", label="Normal (theoretical)")
ax.set_title("Hospital Days — Cumulative Normalized Histogram (ECDF)")
ax.set_xlabel("Days")
ax.set_ylabel("Cumulative Proportion")
ax.legend()
savefig("hospital_ecdf")
plt.close()

# ── 6. Q-Q Plot ──
fig, ax = plt.subplots(figsize=(6, 6))
stats.probplot(hosp, dist="norm", plot=ax)
ax.set_title("Hospital Days — Q-Q Plot")
savefig("hospital_qq")
plt.close()

# ── 7. Summary + Normality ──
print_summary("hospital_days", hosp)
normality_check(hosp, "hospital_days")

# ── 8. Conclusions ──
skew_val = stats.skew(hosp)
kurt_val = stats.kurtosis(hosp)
print(f"\n  ─── CONCLUSIONS ───")
print(f"  Shape: {'right-skewed' if skew_val > 0.5 else 'left-skewed' if skew_val < -0.5 else 'approx symmetric'} (skew={skew_val:.3f})")
print(f"  Tails: {'heavy' if kurt_val > 0 else 'thin/light'} (kurtosis={kurt_val:.3f})")
print(f"  Recommended center: {'mean' if abs(skew_val) < 0.5 else 'median'} (mean={hosp.mean():.2f}, median={hosp.median():.2f})")
print(f"  Recommended spread: {'std' if abs(skew_val) < 0.5 else 'IQR or MAD'}")
print(f"  Log-normal? {'Yes' if log_p > 0.05 else 'No'}")
