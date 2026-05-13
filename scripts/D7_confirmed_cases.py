"""
D7_confirmed_cases.py — Distribution analysis of confirmed_cases (extreme right skew, count data)
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
cases = df["confirmed_cases"].dropna()
n = len(cases)

FIGS_DIR = "../figures"

# ── 1. Box Plot ──
fig, ax = plt.subplots(figsize=(10, 2.5))
ax.boxplot(cases, vert=False, patch_artist=True, widths=0.3,
           boxprops=dict(facecolor="darkred", alpha=0.6),
           medianprops=dict(color="red", linewidth=2))
ax.set_title("Confirmed Cases — Box Plot")
ax.set_xlabel("Cases")
ax.text(0.02, 0.85, f"n = {n}", transform=ax.transAxes, fontsize=9, alpha=0.7)
savefig("cases_boxplot")
plt.close()

# ── 2. Violin Plot with Box Overlay ──
fig, ax = plt.subplots(figsize=(10, 3))
parts = ax.violinplot(cases, vert=False, showmeans=False, showmedians=False, widths=0.4)
for pc in parts["bodies"]:
    pc.set_facecolor("darkred")
    pc.set_alpha(0.5)
ax.boxplot(cases, vert=False, widths=0.15, patch_artist=True,
           boxprops=dict(facecolor="salmon", alpha=0.7),
           medianprops=dict(color="red", linewidth=2))
ax.set_title("Confirmed Cases — Violin Plot with Box Overlay")
ax.set_xlabel("Cases")
ax.text(0.02, 0.85, f"n = {n}", transform=ax.transAxes, fontsize=9, alpha=0.7)
ax.scatter(cases.mean(), 1, color="darkblue", s=50, marker="D", zorder=5,
           label=f"Mean ({cases.mean():.0f})")
ax.legend(loc="upper right")
savefig("cases_violin")
plt.close()

# ── 3. Histogram — full range and zoomed ──
min_val, max_val = cases.min(), cases.max()
fig, axes = plt.subplots(1, 2, figsize=(14, 4))

# Left: full range (shows the massive right tail)
bins_fd_full = int(np.ceil((max_val - min_val) / (2 * stats.iqr(cases) / n**(1/3))))
axes[0].hist(cases, bins=bins_fd_full, color="darkred", edgecolor="white", alpha=0.7)
axes[0].set_title(f"Confirmed Cases — Full Range ({bins_fd_full} bins)")
axes[0].set_xlabel("Cases")
axes[0].set_ylabel("Frequency")

# Right: zoomed to < 1000 (shows the bulk of the data)
cases_zoom = cases[cases < 1000]
axes[1].hist(cases_zoom, bins=np.arange(-0.5, 1001, 50), color="darkred",
             edgecolor="white", alpha=0.7)
axes[1].set_title(f"Confirmed Cases — Zoomed (<1000, {len(cases_zoom)} of {n} pts)")
axes[1].set_xlabel("Cases")
axes[1].set_ylabel("Frequency")
plt.tight_layout()
savefig("cases_histogram")
plt.close()

# ── 4. Log-transformed histogram ──
log_cases = np.log(cases)
log_bins = int(np.sqrt(n))

fig, axes = plt.subplots(1, 2, figsize=(14, 4))
axes[0].hist(cases, bins=bins_fd_full, color="darkred", edgecolor="white", alpha=0.7)
axes[0].set_title("Confirmed Cases — Original Scale")
axes[0].set_xlabel("Cases")
axes[0].set_ylabel("Frequency")

axes[1].hist(log_cases, bins=log_bins, color="darkorange", edgecolor="white", alpha=0.7)
axes[1].set_title("Confirmed Cases — Log-Transformed")
axes[1].set_xlabel("log(Cases)")
axes[1].set_ylabel("Frequency")
log_stat, log_p = stats.shapiro(log_cases)
axes[1].text(0.05, 0.95, f"Shapiro p={log_p:.4f}", transform=axes[1].transAxes,
             fontsize=9, verticalalignment="top",
             color="green" if log_p > 0.05 else "red")
plt.tight_layout()
savefig("cases_log_histogram")
plt.close()

# ── 5. ECDF ──
fig, ax = plt.subplots(figsize=(8, 4))
ax.hist(cases, bins=bins_fd_full, density=True, cumulative=True,
        color="darkred", edgecolor="white", alpha=0.7, label="ECDF")
mu, sigma = cases.mean(), cases.std()
x = np.linspace(cases.min(), cases.max(), 200)
ax.plot(x, stats.norm.cdf(x, mu, sigma), "r--", label="Normal (theoretical)")
ax.set_xlim(0, 10000)  # zoom to show the relevant range (note: started at -2000 before — fixed! cases can't be negative)
ax.set_title("Confirmed Cases — Cumulative Normalized Histogram")
ax.set_xlabel("Cases")
ax.set_ylabel("Cumulative Proportion")
ax.legend()
savefig("cases_ecdf")
plt.close()

# ── 6. Q-Q Plot ──
fig, ax = plt.subplots(figsize=(6, 6))
stats.probplot(cases, dist="norm", plot=ax)
ax.set_title("Confirmed Cases — Q-Q Plot")
savefig("cases_qq")
plt.close()

# ── 7. No-outliers version (IQR rule, for readability) ──
q1, q3 = cases.quantile(0.25), cases.quantile(0.75)
iqr = q3 - q1
lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
cases_no = cases[(cases >= lower) & (cases <= upper)]
n_removed = len(cases) - len(cases_no)
print(f"\n  No-outliers version: removed {n_removed} outliers ({n_removed/len(cases)*100:.1f}%), {len(cases_no)} remain")

for suffix, data in [("", cases), ("_nooutliers", cases_no)]:
    lbl = "All Data" if suffix == "" else "No Outliers"
    hide_fliers = suffix == "_nooutliers"
    c = "darkred"

    # Box plot
    fig, ax = plt.subplots(figsize=(10, 2.5))
    ax.boxplot(data, vert=False, patch_artist=True, widths=0.3, showfliers=not hide_fliers,
               boxprops=dict(facecolor=c, alpha=0.6),
               medianprops=dict(color="red", linewidth=2))
    ax.set_title(f"Confirmed Cases — {lbl} (n={len(data)})")
    ax.set_xlabel("Cases")
    savefig(f"cases{suffix}_boxplot")
    plt.close()

    # Violin with box overlay
    fig, ax = plt.subplots(figsize=(10, 3))
    parts = ax.violinplot(data, vert=False, showmeans=False, showmedians=False, widths=0.4)
    for pc in parts["bodies"]:
        pc.set_facecolor(c)
        pc.set_alpha(0.5)
    ax.boxplot(data, vert=False, widths=0.15, patch_artist=True, showfliers=not hide_fliers,
               boxprops=dict(facecolor="salmon", alpha=0.7),
               medianprops=dict(color="red", linewidth=2))
    ax.scatter(data.mean(), 1, color="darkblue", s=50, marker="D", zorder=5,
               label=f"Mean ({data.mean():.0f})")
    ax.set_title(f"Confirmed Cases — {lbl} Violin")
    ax.set_xlabel("Cases")
    ax.legend(loc="upper right")
    savefig(f"cases{suffix}_violin")
    plt.close()

    # Histogram
    mn, mx = data.min(), data.max()
    bins_fd = int(np.ceil((mx - mn) / (2 * stats.iqr(data) / len(data)**(1/3))))
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.hist(data, bins=bins_fd, color=c, edgecolor="white", alpha=0.7)
    ax.set_title(f"Confirmed Cases — {lbl} Histogram ({bins_fd} bins)")
    ax.set_xlabel("Cases")
    ax.set_ylabel("Frequency")
    savefig(f"cases{suffix}_histogram")
    plt.close()

    # ECDF
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.hist(data, bins=bins_fd, density=True, cumulative=True,
            color=c, edgecolor="white", alpha=0.7, label="ECDF")
    mu_d, sigma_d = data.mean(), data.std()
    x = np.linspace(data.min(), data.max(), 200)
    ax.plot(x, stats.norm.cdf(x, mu_d, sigma_d), "r--", label="Normal (theoretical)")
    ax.set_title(f"Confirmed Cases — {lbl} ECDF")
    ax.set_xlabel("Cases")
    ax.set_ylabel("Cumulative Proportion")
    ax.legend()
    savefig(f"cases{suffix}_ecdf")
    plt.close()

    # Q-Q
    fig, ax = plt.subplots(figsize=(6, 6))
    stats.probplot(data, dist="norm", plot=ax)
    ax.set_title(f"Confirmed Cases — {lbl} Q-Q Plot")
    savefig(f"cases{suffix}_qq")
    plt.close()

# ── 8. By syndrome ──
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
syn_colors = {"HPS": "steelblue", "HFRS": "darkorange"}
for syn in ["HPS", "HFRS"]:
    subset = df[df["syndrome"] == syn]["confirmed_cases"].dropna()
    axes[0].hist(subset, bins=np.arange(-0.5, max_val + 500, 500), alpha=0.5,
                 label=f"{syn} (n={len(subset)})", color=syn_colors[syn])
axes[0].set_title("Confirmed Cases by Syndrome")
axes[0].set_xlabel("Cases")
axes[0].set_ylabel("Frequency")
axes[0].legend()

data_syn = [df[df["syndrome"] == s]["confirmed_cases"].dropna() for s in ["HPS", "HFRS"]]
parts = axes[1].violinplot(data_syn, vert=False, showmedians=True)
for i, pc in enumerate(parts["bodies"]):
    pc.set_facecolor(list(syn_colors.values())[i])
    pc.set_alpha(0.6)
axes[1].set_yticks([1, 2])
axes[1].set_yticklabels(["HPS", "HFRS"])
axes[1].set_title("Confirmed Cases by Syndrome (Violin)")
axes[1].set_xlabel("Cases")
plt.tight_layout()
savefig("cases_by_syndrome")
plt.close()

# ── 9. By WHO region ──
fig, ax = plt.subplots(figsize=(8, 4))
regions = df.groupby("who_region")["confirmed_cases"].apply(list)
labels = [f"{r}\n(n={len(v)})" for r, v in regions.items()]
ax.violinplot([df[df["who_region"] == r]["confirmed_cases"].dropna()
               for r in regions.index], vert=False, showmedians=True)
ax.set_yticks(range(1, len(regions) + 1))
ax.set_yticklabels(labels)
ax.set_title("Confirmed Cases by WHO Region")
ax.set_xlabel("Cases")
plt.tight_layout()
savefig("cases_by_region")
plt.close()

# ── 10. Summary + Normality ──
print_summary("confirmed_cases", cases)
normality_check(cases, "confirmed_cases")

# Print key subgroups
print(f"\n  ─── CASES BY SYNDROME ───")
for syn in ["HPS", "HFRS"]:
    sub = df[df["syndrome"] == syn]["confirmed_cases"]
    print(f"  {syn}: n={len(sub):4d}, mean={sub.mean():8.0f}, median={sub.median():6.0f}, max={sub.max():7.0f}")

print(f"\n  ─── CASES BY WHO REGION ───")
for region in df["who_region"].unique():
    sub = df[df["who_region"] == region]["confirmed_cases"]
    print(f"  {region}: n={len(sub):4d}, mean={sub.mean():8.0f}, median={sub.median():6.0f}, max={sub.max():7.0f}")

# ── 11. Conclusions ──
skew_val = stats.skew(cases)
kurt_val = stats.kurtosis(cases)
print(f"\n  ─── CONCLUSIONS ───")
print(f"  Shape: {'right-skewed' if skew_val > 0.5 else 'left-skewed' if skew_val < -0.5 else 'approx symmetric'} (skew={skew_val:.3f})")
print(f"  Tails: {'heavy' if kurt_val > 0 else 'thin/light'} (kurtosis={kurt_val:.3f})")
print(f"  Recommended center: {'mean' if abs(skew_val) < 0.5 else 'median'} (mean={cases.mean():.0f}, median={cases.median():.0f})")
print(f"  Recommended spread: {'std' if abs(skew_val) < 0.5 else 'IQR or MAD'}")
print(f"  Log-normal? {'Yes' if log_p > 0.05 else 'No, but much improved'}")
