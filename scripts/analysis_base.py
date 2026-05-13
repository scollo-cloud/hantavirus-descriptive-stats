"""
analysis_base.py — Standardized analysis pipeline for individual variables.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from helper import (
    load_csv, savefig, print_summary, normality_check, 
    validate_positive, iqr_outliers
)
from config import STYLE

def analyze_variable(filename: str, col_name: str, display_name: str):
    """Standardized analysis pipeline for a numeric variable."""
    df = load_csv(filename)
    series = df[col_name].dropna()
    n = len(series)

    # 1. Box Plot
    fig, ax = plt.subplots(figsize=STYLE["figsize_std"])
    ax.boxplot(series, vert=False, patch_artist=True, widths=STYLE["box_width"],
               boxprops=dict(facecolor=STYLE["box_color"], alpha=STYLE["box_alpha"]),
               medianprops=dict(color=STYLE["median_color"], linewidth=2))
    ax.set_title(f"{display_name} — Box Plot")
    ax.set_xlabel("Value")
    ax.text(0.02, 0.85, f"n = {n}", transform=ax.transAxes, fontsize=9, alpha=0.7)
    savefig(f"{col_name}_boxplot", subdir="boxplots")
    plt.close()

    # 2. Violin Plot
    fig, ax = plt.subplots(figsize=STYLE["figsize_std"])
    parts = ax.violinplot(series, vert=False, showmeans=False, showmedians=False)
    for pc in parts["bodies"]:
        pc.set_facecolor(STYLE["box_color"])
        pc.set_alpha(STYLE["violin_alpha"])
    ax.boxplot(series, vert=False, widths=0.15, patch_artist=True,
               boxprops=dict(facecolor="lightblue", alpha=0.7),
               medianprops=dict(color=STYLE["median_color"], linewidth=2))
    ax.set_title(f"{display_name} — Violin Plot")
    ax.set_xlabel("Value")
    ax.scatter(series.mean(), 1, color=STYLE["mean_color"], s=50, marker=STYLE["mean_marker"], zorder=5)
    savefig(f"{col_name}_violin", subdir="violins")
    plt.close()

    # 3. Histogram
    fig, ax = plt.subplots(figsize=STYLE["figsize_std"])
    ax.hist(series, bins="fd", color=STYLE["box_color"], edgecolor="white", alpha=STYLE["hist_alpha"])
    ax.set_title(f"{display_name} — Histogram (FD rule)")
    ax.set_xlabel("Value")
    savefig(f"{col_name}_histogram", subdir="distributions")
    plt.close()

    # 4. ECDF
    fig, ax = plt.subplots(figsize=STYLE["figsize_std"])
    ax.hist(series, bins="fd", density=True, cumulative=True, histtype="step", color="black")
    ax.set_title(f"{display_name} — ECDF")
    ax.set_xlabel("Value")
    savefig(f"{col_name}_ecdf", subdir="distributions")
    plt.close()

    # 5. Q-Q Plot
    fig, ax = plt.subplots(figsize=STYLE["figsize_square"])
    stats.probplot(series, dist="norm", plot=ax)
    ax.set_title(f"{display_name} — Q-Q Plot")
    savefig(f"{col_name}_qq", subdir="distributions")
    plt.close()

    # 6. Combined Dist Analysis (for backward compatibility/overview)
    fig, axes = plt.subplots(1, 2, figsize=STYLE["figsize_wide"])
    axes[0].hist(series, bins="fd", color=STYLE["box_color"], edgecolor="white", alpha=STYLE["hist_alpha"])
    axes[0].set_title("Histogram")
    axes[1].hist(series, bins="fd", density=True, cumulative=True, histtype="step", color="black")
    axes[1].set_title("ECDF")
    savefig(f"{col_name}_dist_analysis", subdir="distributions")
    plt.close()

    # 7. Summary & Normality
    stats_dict = print_summary(display_name, series)
    normality_check(series, display_name)
    
    return stats_dict
