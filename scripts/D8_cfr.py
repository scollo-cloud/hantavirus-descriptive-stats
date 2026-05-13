"""
D8_cfr.py — Distribution analysis of case_fatality_rate (proportion, likely bimodal by syndrome)
"""
import numpy as np; np.random.seed(42)
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns; sns.set_theme(style="whitegrid")
from scipy import stats
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from helper import load_csv, savefig, print_summary, normality_check

df = load_csv("hantavirus_country_yearly.csv")
cfr = df["case_fatality_rate"].dropna()
n = len(cfr)

FIGS_DIR = "../figures"

# ── 1. Box Plot ──
fig, ax = plt.subplots(figsize=(10, 2.5))
ax.boxplot(cfr, vert=False, patch_artist=True, widths=0.3,
           boxprops=dict(facecolor="purple", alpha=0.6),
           medianprops=dict(color="red", linewidth=2))
ax.set_title("Case Fatality Rate — Box Plot")
ax.set_xlabel("CFR")
ax.text(0.02, 0.85, f"n = {n}", transform=ax.transAxes, fontsize=9, alpha=0.7)
savefig("cfr_boxplot")
plt.close()

# ── 2. Violin Plot with Box Overlay ──
fig, ax = plt.subplots(figsize=(10, 3))
parts = ax.violinplot(cfr, vert=False, showmeans=False, showmedians=False, widths=0.4)
for pc in parts["bodies"]:
    pc.set_facecolor("purple")
    pc.set_alpha(0.5)
ax.boxplot(cfr, vert=False, widths=0.15, patch_artist=True,
           boxprops=dict(facecolor="lavender", alpha=0.7),
           medianprops=dict(color="red", linewidth=2))
ax.set_title("Case Fatality Rate — Violin Plot with Box Overlay")
ax.set_xlabel("CFR")
ax.text(0.02, 0.85, f"n = {n}", transform=ax.transAxes, fontsize=9, alpha=0.7)
ax.scatter(cfr.mean(), 1, color="darkblue", s=50, marker="D", zorder=5,
           label=f"Mean ({cfr.mean():.3f})")
ax.legend(loc="upper right")
savefig("cfr_violin")
plt.close()

# ── 3. Histogram (FD rule) ──
min_val, max_val = cfr.min(), cfr.max()
bins_fd = int(np.ceil((max_val - min_val) / (2 * stats.iqr(cfr) / n**(1/3))))
fig, ax = plt.subplots(figsize=(8, 4))
ax.hist(cfr, bins=bins_fd, color="purple", edgecolor="white", alpha=0.7)
ax.set_title(f"Case Fatality Rate — Histogram (FD rule, {bins_fd} bins)")
ax.set_xlabel("CFR")
ax.set_ylabel("Frequency")
savefig("cfr_histogram")
plt.close()

# ── 4. ECDF ──
fig, ax = plt.subplots(figsize=(8, 4))
ax.hist(cfr, bins=bins_fd, density=True, cumulative=True,
        color="purple", edgecolor="white", alpha=0.7, label="ECDF")
mu, sigma = cfr.mean(), cfr.std()
x = np.linspace(cfr.min(), cfr.max(), 200)
ax.plot(x, stats.norm.cdf(x, mu, sigma), "r--", label="Normal (theoretical)")
ax.set_title("Case Fatality Rate — Cumulative Normalized Histogram")
ax.set_xlabel("CFR")
ax.set_ylabel("Cumulative Proportion")
ax.legend()
savefig("cfr_ecdf")
plt.close()

# ── 5. Q-Q Plot ──
fig, ax = plt.subplots(figsize=(6, 6))
stats.probplot(cfr, dist="norm", plot=ax)
ax.set_title("Case Fatality Rate — Q-Q Plot")
savefig("cfr_qq")
plt.close()

# ── 6. By syndrome ──
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
syn_colors = {"HPS": "steelblue", "HFRS": "darkorange"}
for syn in ["HPS", "HFRS"]:
    subset = df[df["syndrome"] == syn]["case_fatality_rate"].dropna()
    axes[0].hist(subset, bins=20, alpha=0.5,
                 label=f"{syn} (n={len(subset)})", color=syn_colors[syn])
axes[0].set_title("Case Fatality Rate by Syndrome")
axes[0].set_xlabel("CFR")
axes[0].set_ylabel("Frequency")
axes[0].legend()

data_syn = [df[df["syndrome"] == s]["case_fatality_rate"].dropna() for s in ["HPS", "HFRS"]]
parts = axes[1].violinplot(data_syn, vert=False, showmedians=True)
for i, pc in enumerate(parts["bodies"]):
    pc.set_facecolor(list(syn_colors.values())[i])
    pc.set_alpha(0.6)
axes[1].set_yticks([1, 2])
axes[1].set_yticklabels(["HPS", "HFRS"])
axes[1].set_title("Case Fatality Rate by Syndrome (Violin)")
axes[1].set_xlabel("CFR")
plt.tight_layout()
savefig("cfr_by_syndrome")
plt.close()

# ── 6b. Split by syndrome: separate box+violin for each ──
for syn, color in [("HPS", "steelblue"), ("HFRS", "darkorange")]:
    sub = df[df["syndrome"] == syn]["case_fatality_rate"].dropna()
    fig, axes = plt.subplots(1, 2, figsize=(14, 3))

    axes[0].boxplot(sub, vert=False, patch_artist=True, widths=0.3,
                    boxprops=dict(facecolor=color, alpha=0.6),
                    medianprops=dict(color="red", linewidth=2))
    axes[0].set_title(f"{syn} — CFR (n={len(sub)})")
    axes[0].set_xlabel("CFR")

    parts = axes[1].violinplot(sub, vert=False, showmeans=False, showmedians=False, widths=0.4)
    for pc in parts["bodies"]:
        pc.set_facecolor(color)
        pc.set_alpha(0.5)
    axes[1].boxplot(sub, vert=False, widths=0.15, patch_artist=True,
                    boxprops=dict(facecolor="white", alpha=0.7),
                    medianprops=dict(color="red", linewidth=2))
    axes[1].scatter(sub.mean(), 1, color="darkblue", s=50, marker="D", zorder=5,
                    label=f"Mean ({sub.mean():.3f})")
    axes[1].set_title(f"{syn} — Violin")
    axes[1].set_xlabel("CFR")
    axes[1].legend(loc="upper right")
    plt.tight_layout()
    savefig(f"cfr_{syn.lower()}")
    plt.close()

    print(f"\n  ─── {syn} CFR ───")
    print(f"  n={len(sub)}, mean={sub.mean():.3f}, median={sub.median():.3f}")
    print(f"  IQR={sub.quantile(0.75)-sub.quantile(0.25):.3f}")

# ── 6c. Combined side-by-side violin+box for comparison ──
fig, ax = plt.subplots(figsize=(8, 4))
hps_sub = df[df["syndrome"] == "HPS"]["case_fatality_rate"].dropna()
hfrs_sub = df[df["syndrome"] == "HFRS"]["case_fatality_rate"].dropna()
parts = ax.violinplot([hps_sub, hfrs_sub], vert=False, showmeans=False, showmedians=False,
                      positions=[1, 2], widths=0.5)
for i, pc in enumerate(parts["bodies"]):
    pc.set_facecolor(["steelblue", "darkorange"][i])
    pc.set_alpha(0.5)
ax.boxplot(hps_sub, vert=False, positions=[1], widths=0.2, patch_artist=True,
           boxprops=dict(facecolor="steelblue", alpha=0.7), medianprops=dict(color="red", linewidth=2))
ax.boxplot(hfrs_sub, vert=False, positions=[2], widths=0.2, patch_artist=True,
           boxprops=dict(facecolor="darkorange", alpha=0.7), medianprops=dict(color="red", linewidth=2))
ax.set_yticks([1, 2])
ax.set_yticklabels(["HPS", "HFRS"])
ax.set_title("Case Fatality Rate — HPS vs HFRS")
ax.set_xlabel("CFR")
ax.scatter(hps_sub.mean(), 1, color="darkblue", s=50, marker="D", zorder=5, label=f"HPS mean={hps_sub.mean():.3f}")
ax.scatter(hfrs_sub.mean(), 2, color="darkblue", s=50, marker="D", zorder=5, label=f"HFRS mean={hfrs_sub.mean():.3f}")
ax.legend()
plt.tight_layout()
savefig("cfr_combined")
plt.close()

# ── 7. Summary + Normality ──
print_summary("case_fatality_rate", cfr)
normality_check(cfr, "case_fatality_rate")

print(f"\n  ─── CFR BY SYNDROME ───")
for syn in ["HPS", "HFRS"]:
    sub = df[df["syndrome"] == syn]["case_fatality_rate"]
    print(f"  {syn}: n={len(sub):4d}, mean={sub.mean():.3f}, median={sub.median():.3f}, max={sub.max():.3f}")

# ── 8. Conclusions ──
skew_val = stats.skew(cfr)
kurt_val = stats.kurtosis(cfr)
print(f"\n  ─── CONCLUSIONS ───")
print(f"  Shape: {'right-skewed' if skew_val > 0.5 else 'left-skewed' if skew_val < -0.5 else 'approx symmetric'} (skew={skew_val:.3f})")
print(f"  Tails: {'heavy' if kurt_val > 0 else 'thin/light'} (kurtosis={kurt_val:.3f})")
print(f"  Recommended center: {'mean' if abs(skew_val) < 0.5 else 'median'} (mean={cfr.mean():.3f}, median={cfr.median():.3f})")
print(f"  Recommended spread: {'std' if abs(skew_val) < 0.5 else 'IQR or MAD'}")
