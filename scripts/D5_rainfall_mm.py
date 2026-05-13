"""
D5_rainfall_mm.py — Distribution analysis of rainfall_mm (right-skewed, continuous)
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
rain = df["rainfall_mm"].dropna()
n = len(rain)

FIGS_DIR = "../figures"

# ── 1. Box Plot ──
fig, ax = plt.subplots(figsize=(10, 2.5))
ax.boxplot(rain, vert=False, patch_artist=True, widths=0.3,
           boxprops=dict(facecolor="royalblue", alpha=0.6),
           medianprops=dict(color="red", linewidth=2))
ax.set_title("Rainfall — Box Plot")
ax.set_xlabel("Rainfall (mm)")
ax.text(0.02, 0.85, f"n = {n}", transform=ax.transAxes, fontsize=9, alpha=0.7)
savefig("rain_boxplot")
plt.close()

# ── 2. Violin Plot with Box Overlay ──
fig, ax = plt.subplots(figsize=(10, 3))
parts = ax.violinplot(rain, vert=False, showmeans=False, showmedians=False, widths=0.4)
for pc in parts["bodies"]:
    pc.set_facecolor("royalblue")
    pc.set_alpha(0.5)
ax.boxplot(rain, vert=False, widths=0.15, patch_artist=True,
           boxprops=dict(facecolor="lightblue", alpha=0.7),
           medianprops=dict(color="red", linewidth=2))
ax.set_title("Rainfall — Violin Plot with Box Overlay")
ax.set_xlabel("Rainfall (mm)")
ax.text(0.02, 0.85, f"n = {n}", transform=ax.transAxes, fontsize=9, alpha=0.7)
ax.scatter(rain.mean(), 1, color="darkblue", s=50, marker="D", zorder=5,
           label=f"Mean ({rain.mean():.0f} mm)")
ax.legend(loc="upper right")
savefig("rain_violin")
plt.close()

# ── 3. Histogram (FD rule — continuous data) ──
min_val, max_val = rain.min(), rain.max()
bins_fd = int(np.ceil((max_val - min_val) / (2 * stats.iqr(rain) / n**(1/3))))

fig, axes = plt.subplots(1, 2, figsize=(14, 4))
axes[0].hist(rain, bins=bins_fd, color="royalblue", edgecolor="white", alpha=0.7)
axes[0].set_title(f"Rainfall — Full Range (FD rule, {bins_fd} bins)")
axes[0].set_xlabel("Rainfall (mm)")
axes[0].set_ylabel("Frequency")

# Zoomed: rainfall < 600mm to see the bulk of the distribution
rain_zoom = rain[rain < 600]
axes[1].hist(rain_zoom, bins=30, color="royalblue", edgecolor="white", alpha=0.7)
axes[1].set_title(f"Rainfall — Zoomed (<600mm, {len(rain_zoom)} of {n} pts)")
axes[1].set_xlabel("Rainfall (mm)")
axes[1].set_ylabel("Frequency")

plt.tight_layout()
savefig("rain_histogram")
plt.close()

# ── 4. Log-transformed histogram (continuous — works well) ──
log_rain = np.log(rain + 1)  # +1 to handle zeros
log_bins = int(np.sqrt(n))

fig, axes = plt.subplots(1, 2, figsize=(14, 4))
axes[0].hist(rain, bins=bins_fd, color="royalblue", edgecolor="white", alpha=0.7)
axes[0].set_title("Rainfall — Original Scale")
axes[0].set_xlabel("Rainfall (mm)")
axes[0].set_ylabel("Frequency")

axes[1].hist(log_rain, bins=log_bins, color="darkorange", edgecolor="white", alpha=0.7)
axes[1].set_title("Rainfall — Log-Transformed (continuous data)")
axes[1].set_xlabel("log(Rainfall + 1)")
axes[1].set_ylabel("Frequency")
log_stat, log_p = stats.shapiro(log_rain)
axes[1].text(0.05, 0.95, f"Shapiro p={log_p:.4f}", transform=axes[1].transAxes,
             fontsize=9, verticalalignment="top",
             color="green" if log_p > 0.05 else "red")
plt.tight_layout()
savefig("rain_log_histogram")
plt.close()

# ── 5. ECDF ──
fig, ax = plt.subplots(figsize=(8, 4))
ax.hist(rain, bins=bins_fd, density=True, cumulative=True,
        color="royalblue", edgecolor="white", alpha=0.7, label="ECDF")
mu, sigma = rain.mean(), rain.std()
x = np.linspace(rain.min(), rain.max(), 200)
ax.plot(x, stats.norm.cdf(x, mu, sigma), "r--", label="Normal (theoretical)")
ax.set_title("Rainfall — Cumulative Normalized Histogram")
ax.set_xlabel("Rainfall (mm)")
ax.set_ylabel("Cumulative Proportion")
ax.legend()
savefig("rain_ecdf")
plt.close()

# ── 6. Q-Q Plot (rainfall is not bounded at 0, but has positive domain only) ──
fig, ax = plt.subplots(figsize=(6, 6))
stats.probplot(rain, dist="norm", plot=ax)
ax.set_title("Rainfall — Q-Q Plot")
savefig("rain_qq")
plt.close()

# ── 7. Subgroup: by biome ──
fig, ax = plt.subplots(figsize=(10, 5))
biomes = df.groupby("biome")["rainfall_mm"].apply(list)
labels = [f"{b}\n(n={len(v)})" for b, v in biomes.items()]
ax.violinplot([df[df["biome"] == b]["rainfall_mm"].dropna() for b in biomes.index],
              vert=False, showmedians=True)
ax.set_yticks(range(1, len(biomes) + 1))
ax.set_yticklabels(labels, fontsize=8)
ax.set_title("Rainfall by Biome")
ax.set_xlabel("Rainfall (mm)")
plt.tight_layout()
savefig("rain_by_biome")
plt.close()

# ── 8. Summary + Normality ──
print_summary("rainfall_mm", rain)
normality_check(rain, "rainfall_mm")

# Print biome means
print(f"\n  ─── RAINFALL BY BIOME ───")
for biome in biomes.index:
    sub = df[df["biome"] == biome]["rainfall_mm"]
    print(f"  {biome:25s}: mean={sub.mean():6.1f}  median={sub.median():6.1f}  n={len(sub)}")

# ── 9. Conclusions ──
skew_val = stats.skew(rain)
kurt_val = stats.kurtosis(rain)
print(f"\n  ─── CONCLUSIONS ───")
print(f"  Shape: {'right-skewed' if skew_val > 0.5 else 'left-skewed' if skew_val < -0.5 else 'approx symmetric'} (skew={skew_val:.3f})")
print(f"  Tails: {'heavy' if kurt_val > 0 else 'thin/light'} (kurtosis={kurt_val:.3f})")
print(f"  Recommended center: {'mean' if abs(skew_val) < 0.5 else 'median'} (mean={rain.mean():.2f}, median={rain.median():.2f})")
print(f"  Recommended spread: {'std' if abs(skew_val) < 0.5 else 'IQR or MAD'}")
print(f"  Log-normal? {'Yes' if log_p > 0.05 else 'Closer than raw but still rejected'}")
