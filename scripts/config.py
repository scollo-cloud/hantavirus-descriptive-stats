"""
config.py — Centralized configuration for paths, styles, and statistical thresholds.
"""
from pathlib import Path

# --- Path Handling (Absolute Paths) ---
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
DATA_DIR = PROJECT_ROOT / "data"
FIGS_DIR = PROJECT_ROOT / "figures"
TABLES_DIR = PROJECT_ROOT / "tables"
REPORT_DIR = PROJECT_ROOT / "report"
DASHBOARD_DIR = PROJECT_ROOT / "dashboard"

# Ensure directories exist
for d in [FIGS_DIR, TABLES_DIR, DASHBOARD_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# --- Statistical Thresholds (Bulmer 1979) ---
SKEW_SYMMETRIC = 0.5   # |skew| < 0.5 ≈ symmetric
SKEW_MODERATE = 1.0    # 0.5 ≤ |skew| < 1.0 = moderate skew
LARGE_N_THRESHOLD = 50 # Beyond this, Shapiro-Wilk is often too sensitive

# --- Plotting Styles ---
STYLE = {
    "box_width": 0.3,
    "box_color": "steelblue",
    "box_alpha": 0.6,
    "violin_alpha": 0.5,
    "median_color": "red",
    "mean_marker": "D",
    "mean_color": "darkblue",
    "hist_alpha": 0.7,
    "grid_style": "whitegrid",
    "figsize_std": (10, 4),
    "figsize_wide": (14, 4),
    "figsize_square": (6, 6),
}

# --- Data Mapping ---
FILE_MAP = {
    "clinical": "hantavirus_clinical.csv",
    "environmental": "hantavirus_environmental.csv",
    "yearly": "hantavirus_country_yearly.csv",
}

RANDOM_SEED = 42
