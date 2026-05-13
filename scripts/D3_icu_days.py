"""
D3_icu_days.py — Full distribution analysis of icu_days
Note: icu_days has a structural zero spike (most patients never go to ICU)
"""
import numpy as np; np.random.seed(42)
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns; sns.set_theme(style="whitegrid")
from scipy import stats
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from helper import validate_positive, load_csv, savefig, print_summary, normality_check

df = load_csv("hantavirus_clinical.csv")
icu = df["icu_days"].dropna()
n = len(icu)


# ── 1. Box Plot ──
fig, ax = plt.subplots(figsize=(10, 2.5))
ax.boxplot(icu, vert=False, patch_artist=True, widths=0.3,
           boxprops=dict(facecolor="steelblue", alpha=0.6),
           medianprops=dict(color="red", linewidth=2))
ax.set_title("ICU Days — Box Plot")
ax.set_xlabel("Days")
ax.text(0.02, 0.85, f"n = {n}", transform=ax.transAxes, fontsize=9, alpha=0.7)
savefig("icu_boxplot")
plt.close()

# ── 2. Violin Plot with Box Overlay ──
fig, ax = plt.subplots(figsize=(10, 3))
parts = ax.violinplot(icu, vert=False, showmeans=False, showmedians=False, widths=0.4)
for pc in parts["bodies"]:
    pc.set_facecolor("steelblue")
    pc.set_alpha(0.5)
ax.boxplot(icu, vert=False, widths=0.15, patch_artist=True,
           boxprops=dict(facecolor="lightblue", alpha=0.7),
           medianprops=dict(color="red", linewidth=2))
ax.set_title("ICU Days — Violin Plot with Box Overlay")
ax.set_xlabel("Days")
ax.text(0.02, 0.85, f"n = {n}", transform=ax.transAxes, fontsize=9, alpha=0.7)
ax.scatter(icu.mean(), 1, color="darkblue", s=50, marker="D", zorder=5,
           label=f"Mean ({icu.mean():.2f})")
ax.legend(loc="upper right")
savefig("icu_violin")
plt.close()

# ── 3. Histogram ──
min_val, max_val = icu.min(), icu.max()
bins_fd = int(np.ceil((max_val - min_val) / (2 * stats.iqr(icu) / n**(1/3))))

fig, axes = plt.subplots(1, 2, figsize=(14, 4))

# Left: full range (shows the zero spike)
axes[0].hist(icu, bins=np.arange(-0.5, max_val + 2), color="steelblue",
             edgecolor="white", alpha=0.7)
axes[0].set_title("ICU Days — Full Range (zero spike)")
axes[0].set_xlabel("Days")
axes[0].set_ylabel("Frequency")

# Right: zoomed to non-zero only (shows the ICU-stay distribution)
icu_nonzero = icu[icu > 0]
axes[1].hist(icu_nonzero, bins=np.arange(0.5, max_val + 2), color="darkorange",
             edgecolor="white", alpha=0.7)
axes[1].set_title(f"ICU Days — Non-Zero Only (n={len(icu_nonzero)})")
axes[1].set_xlabel("Days")
axes[1].set_ylabel("Frequency")

plt.tight_layout()
savefig("icu_histogram")
plt.close()

# ── 4. Log-transformed ──
log_icu = np.log(icu[icu > 0])  # log only non-zero
log_bins = int(np.sqrt(len(log_icu)))

fig, axes = plt.subplots(1, 2, figsize=(14, 4))
axes[0].hist(icu, bins=np.arange(-0.5, max_val + 2), color="steelblue",
             edgecolor="white", alpha=0.7)
axes[0].set_title("ICU Days — Original")
axes[0].set_xlabel("Days")
axes[0].set_ylabel("Frequency")

axes[1].hist(log_icu, bins=log_bins, color="darkorange", edgecolor="white", alpha=0.7)
axes[1].set_title("ICU Days (>0) — Log-Transformed")
axes[1].set_xlabel("log(Days)")
axes[1].set_ylabel("Frequency")
if len(log_icu) > 3:
    log_stat, log_p = stats.shapiro(log_icu)
    axes[1].text(0.05, 0.95, f"Shapiro p={log_p:.4f}", transform=axes[1].transAxes,
                 fontsize=9, verticalalignment="top",
                 color="green" if log_p > 0.05 else "red")
plt.tight_layout()
savefig("icu_log_histogram")
plt.close()

# ── 5. ECDF ──
fig, ax = plt.subplots(figsize=(8, 4))
ax.hist(icu, bins=bins_fd, density=True, cumulative=True,
        color="steelblue", edgecolor="white", alpha=0.7, label="ECDF")
mu, sigma = icu.mean(), icu.std()
x = np.linspace(icu.min(), icu.max(), 200)
ax.plot(x, stats.norm.cdf(x, mu, sigma), "r--", label="Normal (theoretical)")
ax.set_title("ICU Days — Cumulative Normalized Histogram")
ax.set_xlabel("Days")
ax.set_ylabel("Cumulative Proportion")
ax.legend()
savefig("icu_ecdf")
plt.close()

# ── 6. Q-Q Plot ──
fig, ax = plt.subplots(figsize=(6, 6))
stats.probplot(icu, dist="norm", plot=ax)
ax.set_title("ICU Days — Q-Q Plot")
savefig("icu_qq")
plt.close()

# ── 7. Summary + Normality ──
print_summary("icu_days (all)", icu)
print_summary("icu_days (>0 only)", icu_nonzero)
normality_check(icu, "icu_days (all)")

# ── 8. Conclusions ──
skew_val = stats.skew(icu)
kurt_val = stats.kurtosis(icu)
zero_pct = (icu == 0).mean() * 100
print(f"\n  ─── CONCLUSIONS ───")
print(f"  Zero spike: {zero_pct:.1f}% of patients have icu_days = 0")
print(f"  This is a 'spike-and-slab' distribution: structural zero + continuous tail")
print(f"  Overall shape: right-skewed (skew={skew_val:.3f})")
print(f"  Recommended center: median ({icu.median():.0f}) — mean ({icu.mean():.2f}) is misleading")
print(f"  For the non-zero subgroup only:")
print(f"    n={len(icu_nonzero)}, mean={icu_nonzero.mean():.2f}, median={icu_nonzero.median():.0f}")
