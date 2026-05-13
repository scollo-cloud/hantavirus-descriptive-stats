"""
D4_avg_temp_c.py — Distribution analysis of avg_temp_c (continuous, near-normal)
"""
import numpy as np; np.random.seed(42)
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns; sns.set_theme(style="whitegrid")
from scipy import stats
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from helper import load_csv, savefig, print_summary, normality_check

df = load_csv("hantavirus_environmental.csv")
temp = df["avg_temp_c"].dropna()
n = len(temp)


# ── 1. Box Plot ──
fig, ax = plt.subplots(figsize=(10, 2.5))
ax.boxplot(temp, vert=False, patch_artist=True, widths=0.3,
           boxprops=dict(facecolor="forestgreen", alpha=0.6),
           medianprops=dict(color="red", linewidth=2))
ax.set_title("Average Temperature — Box Plot")
ax.set_xlabel("Temperature (°C)")
ax.text(0.02, 0.85, f"n = {n}", transform=ax.transAxes, fontsize=9, alpha=0.7)
savefig("temp_boxplot")
plt.close()

# ── 2. Violin Plot with Box Overlay ──
fig, ax = plt.subplots(figsize=(10, 3))
parts = ax.violinplot(temp, vert=False, showmeans=False, showmedians=False, widths=0.4)
for pc in parts["bodies"]:
    pc.set_facecolor("forestgreen")
    pc.set_alpha(0.5)
ax.boxplot(temp, vert=False, widths=0.15, patch_artist=True,
           boxprops=dict(facecolor="lightgreen", alpha=0.7),
           medianprops=dict(color="red", linewidth=2))
ax.set_title("Average Temperature — Violin Plot with Box Overlay")
ax.set_xlabel("Temperature (°C)")
ax.text(0.02, 0.85, f"n = {n}", transform=ax.transAxes, fontsize=9, alpha=0.7)
ax.scatter(temp.mean(), 1, color="darkblue", s=50, marker="D", zorder=5,
           label=f"Mean ({temp.mean():.1f}°C)")
ax.legend(loc="upper right")
savefig("temp_violin")
plt.close()

# ── 3. Histogram (FD rule) ──
min_val, max_val = temp.min(), temp.max()
bins_fd = int(np.ceil((max_val - min_val) / (2 * stats.iqr(temp) / n**(1/3))))

fig, ax = plt.subplots(figsize=(8, 4))
ax.hist(temp, bins=bins_fd, color="forestgreen", edgecolor="white", alpha=0.7)
ax.set_title(f"Average Temperature — Histogram (FD rule, {bins_fd} bins)")
ax.set_xlabel("Temperature (°C)")
ax.set_ylabel("Frequency")
savefig("temp_histogram")
plt.close()

# ── 4. ECDF ──
fig, ax = plt.subplots(figsize=(8, 4))
ax.hist(temp, bins=bins_fd, density=True, cumulative=True,
        color="forestgreen", edgecolor="white", alpha=0.7, label="ECDF")
mu, sigma = temp.mean(), temp.std()
x = np.linspace(temp.min(), temp.max(), 200)
ax.plot(x, stats.norm.cdf(x, mu, sigma), "r--", label="Normal (theoretical)")
ax.set_title("Average Temperature — Cumulative Normalized Histogram (ECDF)")
ax.set_xlabel("Temperature (°C)")
ax.set_ylabel("Cumulative Proportion")
ax.legend()
savefig("temp_ecdf")
plt.close()

# ── 5. Q-Q Plot (useful here — temp has room on both sides) ──
fig, ax = plt.subplots(figsize=(6, 6))
stats.probplot(temp, dist="norm", plot=ax)
ax.set_title("Average Temperature — Q-Q Plot")
savefig("temp_qq")
plt.close()

# ── 6. Summary + Normality ──
print_summary("avg_temp_c", temp)
normality_check(temp, "avg_temp_c")

# ── 7. Conclusions ──
skew_val = stats.skew(temp)
kurt_val = stats.kurtosis(temp)
print(f"\n  ─── CONCLUSIONS ───")
print(f"  Shape: {'right-skewed' if skew_val > 0.5 else 'left-skewed' if skew_val < -0.5 else 'approximately symmetric'} (skew={skew_val:.3f})")
print(f"  Tails: {'heavy' if kurt_val > 0 else 'thin/light'} (kurtosis={kurt_val:.3f})")
print(f"  Recommended center: {'mean' if abs(skew_val) < 0.5 else 'median'} (mean={temp.mean():.2f}, median={temp.median():.2f})")
print(f"  Recommended spread: {'std' if abs(skew_val) < 0.5 else 'IQR or MAD'}")
