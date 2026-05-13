"""
D1_incubation_days.py — Full distribution analysis of incubation_days
CORRECTED: handles discrete integer data properly
"""
import numpy as np; np.random.seed(42)
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns; sns.set_theme(style="whitegrid")
from scipy import stats
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from helper import load_csv, savefig, print_summary, normality_check, validate_positive

df = load_csv("hantavirus_clinical.csv")
inc = df["incubation_days"].dropna()
n = len(inc)

# ── 1. Box Plot ──
fig, ax = plt.subplots(figsize=(10, 2.5))
bp = ax.boxplot(inc, vert=False, patch_artist=True,
                widths=0.3,
                boxprops=dict(facecolor="steelblue", alpha=0.6),
                medianprops=dict(color="red", linewidth=2),
                whiskerprops=dict(color="black"),
                capprops=dict(color="black"),
                flierprops=dict(marker="o", markerfacecolor="red", markersize=4, alpha=0.6))
ax.set_title("Incubation Days — Box Plot")
ax.set_xlabel("Days")
# Note the sample size
ax.text(0.02, 0.85, f"n = {n}", transform=ax.transAxes, fontsize=9, alpha=0.7)
savefig("incubation_boxplot")
plt.close()

# ── 2. Violin Plot (with box inside) ──
fig, ax = plt.subplots(figsize=(10, 3))
parts = ax.violinplot(inc, vert=False, showmeans=False, showmedians=False,
                      widths=0.4)
for pc in parts["bodies"]:
    pc.set_facecolor("steelblue")
    pc.set_alpha(0.5)
# Overlay box plot inside violin
ax.boxplot(inc, vert=False, widths=0.15, patch_artist=True,
           boxprops=dict(facecolor="lightblue", alpha=0.7),
           medianprops=dict(color="red", linewidth=2),
           flierprops=dict(marker="o", markerfacecolor="red", markersize=4))
ax.set_title("Incubation Days — Violin Plot with Box Overlay")
ax.set_xlabel("Days")
ax.text(0.02, 0.85, f"n = {n}", transform=ax.transAxes, fontsize=9, alpha=0.7)
# Add mean marker
ax.scatter(inc.mean(), 1, color="darkblue", s=50, marker="D", zorder=5, label=f"Mean ({inc.mean():.1f})")
ax.legend(loc="upper right")
savefig("incubation_violin")
plt.close()

# ── 3. Histogram with appropriate bins (integer-aligned) ──
min_day, max_day = inc.min(), inc.max()
bins_int = np.arange(min_day, max_day + 2) - 0.5  # align bin edges on half-integers

fig, axes = plt.subplots(1, 2, figsize=(14, 4))

# 3a. Integer-aligned bins (shows the real discrete nature)
axes[0].hist(inc, bins=bins_int, color="steelblue", edgecolor="white", alpha=0.7)
axes[0].set_title(f"Incubation Days — Histogram (integer bins, n={n})")
axes[0].set_xlabel("Days")
axes[0].set_ylabel("Frequency")

# 3b. Smooth histogram using FD rule (shows overall shape)
bins_fd = int(np.ceil((max_day - min_day) / (2 * stats.iqr(inc) / n**(1/3))))
axes[1].hist(inc, bins=bins_fd, color="steelblue", edgecolor="white", alpha=0.7)
axes[1].set_title(f"Incubation Days — Histogram (FD rule, {bins_fd} bins)")
axes[1].set_xlabel("Days")
axes[1].set_ylabel("Frequency")

plt.tight_layout()
savefig("incubation_histogram")
plt.close()

# ── 4. Log-transformed histogram ──
fig, axes = plt.subplots(1, 2, figsize=(14, 4))

# 4a. Original scale
axes[0].hist(inc, bins=bins_fd, color="steelblue", edgecolor="white", alpha=0.7)
axes[0].set_title("Incubation Days — Original Scale")
axes[0].set_xlabel("Days")
axes[0].set_ylabel("Frequency")

# 4b. Log-transformed
validate_positive(inc, "incubation_days")
log_inc = np.log(inc)
log_bins = int(np.sqrt(n))
axes[1].hist(log_inc, bins=log_bins, color="darkorange", edgecolor="white", alpha=0.7)
axes[1].set_title("Incubation Days — Log-Transformed")
axes[1].set_xlabel("log(Days)")
axes[1].set_ylabel("Frequency")

# Shapiro on log-transformed
log_stat, log_p = stats.shapiro(log_inc)
axes[1].text(0.05, 0.95, f"Shapiro p={log_p:.4f}", transform=axes[1].transAxes,
             fontsize=9, verticalalignment="top",
             color="green" if log_p > 0.05 else "red")

plt.tight_layout()
savefig("incubation_log_histogram")
plt.close()

if log_p > 0.05:
    print(f"  Log-transform: Shapiro p={log_p:.4f} → data IS log-normal (cannot reject normality)")
else:
    print(f"  Log-transform: Shapiro p={log_p:.4f} → data is NOT perfectly log-normal either")

# ── 5. ECDF with theoretical normal + log-normal overlay ──
fig, ax = plt.subplots(figsize=(8, 4))
ax.hist(inc, bins=bins_fd, density=True, cumulative=True,
        color="steelblue", edgecolor="white", alpha=0.7, label="ECDF")
mu, sigma = inc.mean(), inc.std()
x = np.linspace(inc.min(), inc.max(), 200)
ax.plot(x, stats.norm.cdf(x, mu, sigma), "r--", label="Normal (theoretical)")

# Log-normal overlay: parameters from log-transformed data
log_mu = np.log(inc).mean()
log_sigma = np.log(inc).std()
ax.plot(x, stats.lognorm.cdf(x, s=log_sigma, scale=np.exp(log_mu)),
        "g-.", label="Log-Normal (theoretical)", alpha=0.8)

ax.set_title("Incubation Days — ECDF with Normal vs Log-Normal Overlay")
ax.set_xlabel("Days")
ax.set_ylabel("Cumulative Proportion")
ax.legend()
savefig("incubation_ecdf")
plt.close()

# ── 6. Q-Q Plot (with discrete-data caveat) ──
fig, ax = plt.subplots(figsize=(6, 6))
stats.probplot(inc, dist="norm", plot=ax)
ax.set_title("Incubation Days — Q-Q Plot\n(note: plateaus = discrete integer data)")
savefig("incubation_qq")
plt.close()

# ── 7. Summary statistics ──
print_summary("incubation_days", inc)
normality_check(inc, "incubation_days (raw)")

# ── 8. Conclusions ──
skew_val = stats.skew(inc)
kurt_val = stats.kurtosis(inc)
print(f"\n  ─── CONCLUSIONS ───")
print(f"  Shape: {'right-skewed' if skew_val > 0.5 else 'left-skewed' if skew_val < -0.5 else 'approximately symmetric'} (skew={skew_val:.3f})")
print(f"  Tails: {'heavy' if kurt_val > 0 else 'thin/light'} (kurtosis={kurt_val:.3f})")
print(f"  Modes: inspect histogram for number of peaks")
print(f"  Log-normal? {'Yes' if log_p > 0.05 else 'No, but closer than raw'}")
print(f"  Recommended center: {'mean' if abs(skew_val) < 0.5 else 'median'} (mean={inc.mean():.2f}, median={inc.median():.2f})")
print(f"  Recommended spread: {'std' if abs(skew_val) < 0.5 else 'IQR or MAD'}")
print(f"  (std={inc.std():.2f}, IQR={inc.quantile(0.75)-inc.quantile(0.25):.2f}, MAD={(inc-inc.median()).abs().median():.2f})")
