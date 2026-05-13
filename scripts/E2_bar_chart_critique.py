"""
E2_bar_chart_critique.py — Side-by-side comparison: bar+errorbar vs violin+box
Demonstrates why bar charts with error bars hide the distribution
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

# Use hospital_days by severity — the clearest example
severity_order = ["Mild", "Moderate", "Severe", "Critical"]
colors = ["green", "goldenrod", "darkorange", "red"]

groups = [df[df["severity"] == s]["hospital_days"].dropna() for s in severity_order]
means = [g.mean() for g in groups]
sems = [stats.sem(g) for g in groups]
ns = [len(g) for g in groups]

# ── Side-by-side: Bar + errorbar vs Violin + box ──
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# LEFT: Bar chart with error bars (the "bad" version)
axes[0].bar(severity_order, means, yerr=sems, color=colors, alpha=0.6,
            capsize=5, edgecolor="black")
axes[0].set_title("Hospital Days by Severity\nBar Chart + Error Bar (mean ± 1 SE)")
axes[0].set_ylabel("Hospital Days")
axes[0].set_xlabel("Severity")
# Add n annotations
for i, (m, n) in enumerate(zip(means, ns)):
    axes[0].text(i, m + sems[i] + 1, f"n={n}", ha="center", fontsize=8, alpha=0.7)

# RIGHT: Violin + box (the "good" version)
parts = axes[1].violinplot(groups, vert=True, showmeans=False, showmedians=False,
                           positions=range(1, len(groups)+1), widths=0.6)
for i, pc in enumerate(parts["bodies"]):
    pc.set_facecolor(colors[i])
    pc.set_alpha(0.5)

for i, g in enumerate(groups):
    axes[1].boxplot(g, vert=True, positions=[i+1], widths=0.15, patch_artist=True,
                    boxprops=dict(facecolor="white", alpha=0.7),
                    medianprops=dict(color="red", linewidth=2),
                    showfliers=False)
    axes[1].scatter(i+1, g.mean(), color="darkblue", s=40, marker="D", zorder=5)

axes[1].set_xticks(range(1, len(severity_order)+1))
axes[1].set_xticklabels(severity_order)
axes[1].set_title("Hospital Days by Severity\nViolin + Box Plot (full distribution)")
axes[1].set_ylabel("Hospital Days")
axes[1].set_xlabel("Severity")

plt.tight_layout()
savefig("critique_bar_vs_violin", subdir="critique")
plt.close()


