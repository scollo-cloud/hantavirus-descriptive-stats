"""
D6_rodent_abundance.py — Distribution analysis of rodent_abundance_index (bounded [0,1], symmetric)
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
rodent = df["rodent_abundance_index"].dropna()
n = len(rodent)


# ── 1. Box Plot ──
fig, ax = plt.subplots(figsize=(10, 2.5))
ax.boxplot(rodent, vert=False, patch_artist=True, widths=0.3,
           boxprops=dict(facecolor="saddlebrown", alpha=0.6),
           medianprops=dict(color="red", linewidth=2))
ax.set_title("Rodent Abundance Index — Box Plot")
ax.set_xlabel("Index [0–1]")
ax.text(0.02, 0.85, f"n = {n}", transform=ax.transAxes, fontsize=9, alpha=0.7)
savefig("rodent_boxplot")
plt.close()

# ── 2. Violin Plot with Box Overlay ──
fig, ax = plt.subplots(figsize=(10, 3))
parts = ax.violinplot(rodent, vert=False, showmeans=False, showmedians=False, widths=0.4)
for pc in parts["bodies"]:
    pc.set_facecolor("saddlebrown")
    pc.set_alpha(0.5)
ax.boxplot(rodent, vert=False, widths=0.15, patch_artist=True,
           boxprops=dict(facecolor="tan", alpha=0.7),
           medianprops=dict(color="red", linewidth=2))
ax.set_title("Rodent Abundance Index — Violin Plot with Box Overlay")
ax.set_xlabel("Index [0–1]")
ax.text(0.02, 0.85, f"n = {n}", transform=ax.transAxes, fontsize=9, alpha=0.7)
ax.scatter(rodent.mean(), 1, color="darkblue", s=50, marker="D", zorder=5,
           label=f"Mean ({rodent.mean():.3f})")
ax.legend(loc="upper right")
savefig("rodent_violin")
plt.close()

# ── 3. Histogram (FD rule) ──
min_val, max_val = rodent.min(), rodent.max()
bins_fd = int(np.ceil((max_val - min_val) / (2 * stats.iqr(rodent) / n**(1/3))))

fig, ax = plt.subplots(figsize=(8, 4))
ax.hist(rodent, bins=bins_fd, color="saddlebrown", edgecolor="white", alpha=0.7)
ax.set_title(f"Rodent Abundance Index — Histogram (FD rule, {bins_fd} bins)")
ax.set_xlabel("Index [0–1]")
ax.set_ylabel("Frequency")
savefig("rodent_histogram")
plt.close()

# ── 4. ECDF ──
fig, ax = plt.subplots(figsize=(8, 4))
ax.hist(rodent, bins=bins_fd, density=True, cumulative=True,
        color="saddlebrown", edgecolor="white", alpha=0.7, label="ECDF")
mu, sigma = rodent.mean(), rodent.std()
x = np.linspace(rodent.min(), rodent.max(), 200)
ax.plot(x, stats.norm.cdf(x, mu, sigma), "r--", label="Normal (theoretical)")
ax.set_title("Rodent Abundance — Cumulative Normalized Histogram")
ax.set_xlabel("Index [0–1]")
ax.set_ylabel("Cumulative Proportion")
ax.legend()
savefig("rodent_ecdf")
plt.close()

# ── 5. Q-Q Plot (bounded [0,1], but has room from both sides) ──
fig, ax = plt.subplots(figsize=(6, 6))
stats.probplot(rodent, dist="norm", plot=ax)
ax.set_title("Rodent Abundance Index — Q-Q Plot")
savefig("rodent_qq")
plt.close()

# ── 6. By biome ──
fig, ax = plt.subplots(figsize=(10, 5))
ax.violinplot([df[df["biome"] == b]["rodent_abundance_index"].dropna()
               for b in df["biome"].unique()], vert=False, showmedians=True)
ax.set_yticks(range(1, len(df["biome"].unique()) + 1))
ax.set_yticklabels([f"{b}" for b in df["biome"].unique()], fontsize=8)
ax.set_title("Rodent Abundance by Biome")
ax.set_xlabel("Index [0–1]")
plt.tight_layout()
savefig("rodent_by_biome")
plt.close()

# ── 7. Summary + Normality ──
print_summary("rodent_abundance_index", rodent)
normality_check(rodent, "rodent_abundance_index")

# Print biome means
print(f"\n  ─── RODENT ABUNDANCE BY BIOME ───")
for biome in df["biome"].unique():
    sub = df[df["biome"] == biome]["rodent_abundance_index"]
    print(f"  {biome:25s}: mean={sub.mean():.3f}  median={sub.median():.3f}  n={len(sub)}")

# ── 8. Conclusions ──
skew_val = stats.skew(rodent)
kurt_val = stats.kurtosis(rodent)
print(f"\n  ─── CONCLUSIONS ───")
print(f"  Shape: {'right-skewed' if skew_val > 0.5 else 'left-skewed' if skew_val < -0.5 else 'approx symmetric'} (skew={skew_val:.3f})")
print(f"  Tails: {'heavy' if kurt_val > 0 else 'thin/light'} (kurtosis={kurt_val:.3f})")
print(f"  Recommended center: {'mean' if abs(skew_val) < 0.5 else 'median'} (mean={rodent.mean():.3f}, median={rodent.median():.3f})")
print(f"  Recommended spread: {'std' if abs(skew_val) < 0.5 else 'IQR or MAD'}")
print(f"  Note: Bounded [0,1] but near-symmetric — unusual for a bounded variable")
