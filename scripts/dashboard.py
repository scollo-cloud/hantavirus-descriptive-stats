"""
dashboard.py — Generate interactive HTML dashboard of all findings
"""
import numpy as np; np.random.seed(42)
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats
import os, sys, json, base64
sys.path.insert(0, os.path.dirname(__file__))
from helper import load_csv, kurtosis_description

DASHBOARD_DIR = "../dashboard"
os.makedirs(DASHBOARD_DIR, exist_ok=True)

def fig_to_div(fig):
    return fig.to_html(full_html=False, include_plotlyjs=False)

sections_html = []
navbar_items = []

def add_nav(id, label):
    navbar_items.append((id, label))

def add_section(id, label, content):
    add_nav(id, label)
    sections_html.append(f'<div id="{id}" class="section">{content}</div>')

# ── Load data ──
df_clin = load_csv("hantavirus_clinical.csv")
df_env = load_csv("hantavirus_environmental.csv")
df_yr = load_csv("hantavirus_country_yearly.csv")

# ════════════════════════════════════════════
# SECTION: Introduction
# ════════════════════════════════════════════
intro = """
<div class="hero">
  <h1>Hantavirus Descriptive Statistics</h1>
  <p class="subtitle">A step-by-step analysis of distribution, central tendency, variability, and visualization</p>
</div>
<div class="card">
  <p><strong>Data:</strong> <a href="https://www.kaggle.com/datasets/zkskhurram/hantavirus-andes-virus-global-epidemiology" target="_blank">Kaggle — Hantavirus Global Epidemiology</a> <em>(historical dataset, not 2025 outbreak data)</em></p>
  <p><strong>Goal:</strong> Apply descriptive statistics concepts from textbook to real data — learn, make mistakes, fix them.</p>
  <p><strong>Tools:</strong> Python (pandas, numpy, scipy, matplotlib, seaborn, plotly), LaTeX</p>
</div>
<div class="card">
  <h3>Datasets</h3>
  <table class="tbl">
    <tr><th>File</th><th>Rows</th><th>Key Variables</th></tr>
    <tr><td>hantavirus_clinical.csv</td><td>7,538</td><td>incubation_days, hospital_days, icu_days, severity, outcome</td></tr>
    <tr><td>hantavirus_environmental.csv</td><td>896</td><td>avg_temp_c, rainfall_mm, rodent_abundance_index, biome</td></tr>
    <tr><td>hantavirus_country_yearly.csv</td><td>939</td><td>confirmed_cases, case_fatality_rate, syndrome, country</td></tr>
  </table>
</div>
"""
add_section("intro", "Introduction", intro)

# ════════════════════════════════════════════
# SECTION: Master Summary Table
# ════════════════════════════════════════════
rows = []
for name, series in [
    ("Incubation Days", df_clin["incubation_days"]),
    ("Hospital Days", df_clin["hospital_days"]),
    ("ICU Days", df_clin["icu_days"]),
    ("Temperature", df_env["avg_temp_c"]),
    ("Rainfall", df_env["rainfall_mm"]),
    ("Rodent Abundance", df_env["rodent_abundance_index"]),
    ("Confirmed Cases", df_yr["confirmed_cases"]),
    ("Case Fatality Rate", df_yr["case_fatality_rate"]),
]:
    c = series.dropna()
    q1, q3 = c.quantile(0.25), c.quantile(0.75)
    sk = stats.skew(c)
    ku = stats.kurtosis(c)
    center = "Mean" if abs(sk) < 0.5 else "Median"
    spread = "Std" if abs(sk) < 0.5 else "IQR"
    rows.append(f"<tr><td>{name}</td><td>{len(c)}</td><td>{c.mean():.2f}</td><td>{c.median():.2f}</td>"
                f"<td>{c.std():.2f}</td><td>{q3-q1:.2f}</td><td>{sk:.2f}</td><td>{ku:.2f}</td>"
                f"<td>{center}</td><td>{spread}</td></tr>")

master_table = f"""
<div class="card">
  <h2>Master Summary</h2>
  <p>Key statistics for all 8 numeric variables. Skewness > |0.5| → use median + IQR instead of mean + std.</p>
  <div class="table-wrap">
  <table class="tbl">
    <tr><th>Variable</th><th>n</th><th>Mean</th><th>Median</th><th>Std</th><th>IQR</th><th>Skew</th><th>Kurtosis</th><th>Center</th><th>Spread</th></tr>
    {''.join(rows)}
  </table>
  </div>
</div>
"""
add_section("summary", "Summary Table", master_table)

# ════════════════════════════════════════════
# SECTION: D1 — Incubation Days
# ════════════════════════════════════════════
inc = df_clin["incubation_days"].dropna()

fig_box = go.Figure()
fig_box.add_trace(go.Box(x=inc, name="", boxmean="sd", marker_color="steelblue"))
fig_box.update_layout(title="Incubation Days — Box Plot", xaxis_title="Days", height=250, margin=dict(l=20, r=20, t=40, b=20))

bins = int(np.sqrt(len(inc)))
fig_hist = go.Figure()
fig_hist.add_trace(go.Histogram(x=inc, nbinsx=bins, marker_color="steelblue", opacity=0.7))
fig_hist.update_layout(title=f"Incubation Days — Histogram ({bins} bins)", xaxis_title="Days", yaxis_title="Frequency", height=300, margin=dict(l=20, r=20, t=40, b=20))

sk = stats.skew(inc)
ku = stats.kurtosis(inc)
d1_html = f"""
<div class="card">
  <h2>Incubation Days</h2>
  <p><strong>Finding:</strong> Right-skewed (skew={sk:.2f}), unimodal, {kurtosis_description(ku)}. Mean={inc.mean():.1f}d, Median={inc.median():.0f}d. Not normal.</p>
  <p><strong>Mistake fixed:</strong> Originally used beeswarm + KDE + sqrt-rule bins. Replaced with box+violin + integer-aligned bins + ECDF.</p>
  <p><strong>Subgroups:</strong> Incubation is similar across severity levels (~19d) but differs by syndrome — HPS (16d) vs HFRS (22d).</p>
</div>
<div class="plot-row">
  <div>{fig_box.to_html(full_html=False, include_plotlyjs=False)}</div>
  <div>{fig_hist.to_html(full_html=False, include_plotlyjs=False)}</div>
</div>
<div class="card">
  <h3>ECDF — Normal vs Log-Normal Overlay</h3>
  <p>The incubation data deviates from the normal CDF (red) but follows the log-normal CDF (green) more closely.</p>
  <img src="../figures/incubation_ecdf.png" style="max-width:100%; border:1px solid #ddd; border-radius:4px;">
</div>
"""
add_section("d1", "Incubation Days", d1_html)

# ════════════════════════════════════════════
# SECTION: D2 — Hospital Days
# ════════════════════════════════════════════
hosp = df_clin["hospital_days"].dropna()
fig_hosp = go.Figure()
fig_hosp.add_trace(go.Box(x=hosp, name="", boxmean="sd", marker_color="steelblue"))
fig_hosp.update_layout(title="Hospital Days — Box Plot", xaxis_title="Days", height=250, margin=dict(l=20, r=20, t=40, b=20))

d2_html = f"""
<div class="card">
  <h2>Hospital Days</h2>
  <p><strong>Finding:</strong> Appears bimodal in aggregate — actually 4 unimodal severity groups cleanly separated.</p>
  <p><strong>Key discovery:</strong> Each severity level has a distinct, non-overlapping center.</p>
</div>
<div class="plot-row">
  <div>{fig_hosp.to_html(full_html=False, include_plotlyjs=False)}</div>
  <div><img src="../figures/hospital_by_severity.png" style="max-width:100%; border:1px solid #ddd; border-radius:4px;"></div>
</div>
<div class="card">
  <table class="tbl">
    <tr><th>Severity</th><th>n</th><th>Mean</th><th>Median</th><th>IQR</th></tr>
    <tr><td>Mild</td><td>1121</td><td>2.5</td><td>2</td><td>1</td></tr>
    <tr><td>Moderate</td><td>2669</td><td>6.5</td><td>6</td><td>3</td></tr>
    <tr><td>Severe</td><td>2606</td><td>13.5</td><td>13</td><td>5</td></tr>
    <tr><td>Critical</td><td>1142</td><td>20.6</td><td>21</td><td>7</td></tr>
  </table>
  <p><strong>Lesson:</strong> Always check subgroups before describing a distribution. The "bimodal" shape was an aggregation artifact.</p>
</div>
"""
add_section("d2", "Hospital Days", d2_html)

# ════════════════════════════════════════════
# SECTION: D3 — ICU Days
# ════════════════════════════════════════════
icu = df_clin["icu_days"].dropna()
icu_gt0 = icu[icu > 0]

d3_html = f"""
<div class="card">
  <h2>ICU Days — Spike-and-Slab Distribution</h2>
  <p><strong>Finding:</strong> 50.3% of patients have icu_days = 0 (never admitted). Minimum ICU stay = 3 days.</p>
  <p><strong>Key discovery:</strong> ICU admission is perfectly predicted by severity:</p>
  <table class="tbl">
    <tr><th>Severity</th><th>ICU Rate</th><th>ICU Days (median)</th></tr>
    <tr><td>Mild</td><td>0%</td><td>—</td></tr>
    <tr><td>Moderate</td><td>0%</td><td>—</td></tr>
    <tr><td>Severe</td><td>100%</td><td>4</td></tr>
    <tr><td>Critical</td><td>100%</td><td>12</td></tr>
  </table>
  <p><strong>Approach:</strong> Split into two questions: (1) Who goes to ICU? (binary), (2) How long do they stay? (non-zero only).</p>
</div>
<div class="plot-row">
  <div><img src="../figures/icu_split.png" style="max-width:100%; border:1px solid #ddd; border-radius:4px;"></div>
  <div><img src="../figures/icu_by_severity.png" style="max-width:100%; border:1px solid #ddd; border-radius:4px;"></div>
</div>
"""
add_section("d3", "ICU Days", d3_html)

# ════════════════════════════════════════════
# SECTION: D4-D6 — Environmental
# ════════════════════════════════════════════
temp = df_env["avg_temp_c"].dropna()
rain = df_env["rainfall_mm"].dropna()
rodent = df_env["rodent_abundance_index"].dropna()

env_html = f"""
<div class="card">
  <h2>Temperature</h2>
  <p><strong>Finding:</strong> Approximately normal (skew={stats.skew(temp):.2f}). Mean={temp.mean():.1f}°C, Median={temp.median():.1f}°C.</p>
  <p>Only outlier: -8.8°C in Ostrobothnia, Finland (real, kept).</p>
</div>
<div class="plot-row">
  <div><img src="../figures/temp_histogram.png" style="max-width:100%; border:1px solid #ddd; border-radius:4px;"></div>
  <div><img src="../figures/temp_qq.png" style="max-width:100%; border:1px solid #ddd; border-radius:4px;"></div>
</div>

<div class="card">
  <h2>Rainfall</h2>
  <p><strong>Finding:</strong> Right-skewed (skew={stats.skew(rain):.2f}), heavy-tailed (kurtosis={stats.kurtosis(rain):.2f}). Biome explains 10x variation.</p>
</div>
<div class="plot-row">
  <div><img src="../figures/rain_histogram.png" style="max-width:100%; border:1px solid #ddd; border-radius:4px;"></div>
  <div><img src="../figures/rain_by_biome.png" style="max-width:100%; border:1px solid #ddd; border-radius:4px;"></div>
</div>

<div class="card">
  <h2>Rodent Abundance</h2>
  <p><strong>Finding:</strong> Most symmetric variable (skew={stats.skew(rodent):.2f}). Nearly constant across biomes (0.64–0.72 range).</p>
  <p><strong>Caveat:</strong> This assumes comparable sampling protocols across biomes.</p>
</div>
<div class="plot-row">
  <div><img src="../figures/rodent_histogram.png" style="max-width:100%; border:1px solid #ddd; border-radius:4px;"></div>
  <div><img src="../figures/rodent_by_biome.png" style="max-width:100%; border:1px solid #ddd; border-radius:4px;"></div>
</div>
"""
add_section("env", "Environmental", env_html)

# ════════════════════════════════════════════
# SECTION: D7 — Confirmed Cases
# ════════════════════════════════════════════
cases = df_yr["confirmed_cases"].dropna()
hps_c = df_yr[df_yr["syndrome"]=="HPS"]["confirmed_cases"]
hfrs_c = df_yr[df_yr["syndrome"]=="HFRS"]["confirmed_cases"]

d7_html = f"""
<div class="card">
  <h2>Confirmed Cases</h2>
  <p><strong>Finding:</strong> Most extreme skew (skew={stats.skew(cases):.2f}). Mean={cases.mean():.0f}, Median={cases.median():.0f} — mean is 31x the median.</p>
  <p><strong>Tail driven by:</strong> China HFRS (17k–24k cases/year, consistently since 1970s).</p>
</div>
<div class="plot-row">
  <div><img src="../figures/cases_by_syndrome.png" style="max-width:100%; border:1px solid #ddd; border-radius:4px;"></div>
  <div><img src="../figures/cases_nooutliers_boxplot.png" style="max-width:100%; border:1px solid #ddd; border-radius:4px;"></div>
</div>
<div class="card">
  <table class="tbl">
    <tr><th>Region</th><th>n</th><th>Mean</th><th>Median</th><th>Max</th></tr>
    <tr><td>AMRO (Americas)</td><td>273</td><td>30</td><td>13</td><td>146</td></tr>
    <tr><td>EURO (Europe)</td><td>439</td><td>1,046</td><td>89</td><td>9,496</td></tr>
    <tr><td>WPRO (Asia)</td><td>227</td><td>5,358</td><td>482</td><td>23,885</td></tr>
  </table>
  <p><strong>Question:</strong> Is the 100x gap real or underreporting? Consistent data across decades supports real biological differences in rodent host ecology.</p>
</div>
"""
add_section("d7", "Confirmed Cases", d7_html)

# ════════════════════════════════════════════
# SECTION: D8 — Case Fatality Rate
# ════════════════════════════════════════════
cfr = df_yr["case_fatality_rate"].dropna()
add_section("d8", "CFR", f"""
<div class="card">
  <h2>Case Fatality Rate</h2>
  <p><strong>Finding:</strong> Bimodal by syndrome. HPS (mean=28.1%) is <strong>20x more lethal</strong> than HFRS (mean=1.4%).</p>
  <p>Overall CFR of 9.2% represents neither group. Never report CFR as a single number.</p>
  <p><strong>Note:</strong> Differences may partly reflect healthcare access, not just virology.</p>
</div>
<div class="plot-row">
  <div><img src="../figures/cfr_combined.png" style="max-width:100%; border:1px solid #ddd; border-radius:4px;"></div>
  <div><img src="../figures/cfr_by_syndrome.png" style="max-width:100%; border:1px solid #ddd; border-radius:4px;"></div>
</div>
""")

# ════════════════════════════════════════════
# SECTION: Comparative Analysis
# ════════════════════════════════════════════
add_section("compare", "Comparisons", """
<div class="card">
  <h2>Comparative Analysis</h2>
  <p>Key comparisons across subgroups:</p>
  <ul>
    <li><strong>Incubation by severity:</strong> No difference (~19d all levels) — surprisingly similar</li>
    <li><strong>Incubation by syndrome:</strong> HPS (16d) shorter than HFRS (22d)</li>
    <li><strong>Incubation by outcome:</strong> Deceased (17d) slightly shorter than Recovered (20d)</li>
    <li><strong>Hospital by severity:</strong> Clean separation between all 4 levels</li>
    <li><strong>Temperature by biome:</strong> Coldest to warmest — expected pattern</li>
    <li><strong>Rainfall by biome:</strong> Desert (63mm) to Valdivian forest (630mm) — 10x range</li>
  </ul>
</div>
<div class="plot-row">
  <div><img src="../figures/compare_incubation_severity.png" style="max-width:100%; border:1px solid #ddd; border-radius:4px;"></div>
  <div><img src="../figures/compare_incubation_syndrome.png" style="max-width:100%; border:1px solid #ddd; border-radius:4px;"></div>
</div>
""")

# ════════════════════════════════════════════
# SECTION: Bar Chart Critique
# ════════════════════════════════════════════
add_section("critique", "Bar Critique", """
<div class="card">
  <h2>Bar Chart + Error Bar — Why It's Misleading</h2>
  <p>The bar chart (left) hides: sample size, distribution shape, multimodality, outliers, and the fact that mean ± SE assumes normal symmetry.</p>
  <p>The violin + box (right) shows: n, min, Q1, median, Q3, max, shape, skew, tails.</p>
</div>
<img src="../figures/critique_bar_vs_violin.png" style="max-width:100%; border:1px solid #ddd; border-radius:4px; margin-top:10px;">
""")

# ════════════════════════════════════════════
# SECTION: Mistakes
# ════════════════════════════════════════════
add_section("mistakes", "Mistakes", """
<div class="card">
  <h2>Mistakes Made and Fixed</h2>
  <table class="tbl">
    <tr><th>Mistake</th><th>Why It Failed</th><th>Fixed With</th></tr>
    <tr><td>Beeswarm plot</td><td>No vertical spread — couldn't see density</td><td>Box + Violin plot</td></tr>
    <tr><td>86 histogram bins (sqrt rule on integers)</td><td>Empty bins between integers — "comb" effect</td><td>Integer-aligned bins; FD rule for continuous</td></tr>
    <tr><td>KDE on discrete data</td><td>Density below 0; bandwidth subjective</td><td>Log histogram for continuous; skip for integer</td></tr>
    <tr><td>Q-Q on bounded data</td><td>Always deviates at lower tail</td><td>ECDF + subgroup split</td></tr>
    <tr><td>Describing shape without subgroups</td><td>Hospital days appeared bimodal</td><td>Check subgroups first</td></tr>
    <tr><td>ECDF x-axis at -2000</td><td>Cases can't be negative</td><td>Set xlim starting at 0</td></tr>
  </table>
</div>
""")

# ════════════════════════════════════════════
# BUILD: Full HTML
# ════════════════════════════════════════════
nav_links = "\n".join(f'<a href="#" onclick="showSection(\'{id}\')">{label}</a>'
                       for id, label in navbar_items)

all_sections = "\n".join(sections_html)

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Hantavirus Descriptive Statistics Dashboard</title>
<script src="https://cdn.plot.ly/plotly-3.0.1.min.js"></script>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; color: #333; }}
.navbar {{ background: #2c3e50; padding: 12px 20px; position: sticky; top: 0; z-index: 100; display: flex; flex-wrap: wrap; gap: 4px; }}
.navbar a {{ color: #ecf0f1; text-decoration: none; padding: 6px 14px; border-radius: 4px; font-size: 13px; }}
.navbar a:hover {{ background: #34495e; }}
.container {{ max-width: 1100px; margin: 0 auto; padding: 20px; }}
.section {{ display: none; }}
.section.active {{ display: block; }}
.hero {{ background: linear-gradient(135deg, #2c3e50, #3498db); color: white; padding: 40px; border-radius: 8px; margin-bottom: 20px; }}
.hero h1 {{ font-size: 28px; margin-bottom: 8px; }}
.hero .subtitle {{ font-size: 16px; opacity: 0.9; }}
.card {{ background: white; border-radius: 8px; padding: 20px; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
.card h2 {{ font-size: 20px; margin-bottom: 10px; color: #2c3e50; }}
.card h3 {{ font-size: 16px; margin-bottom: 8px; color: #34495e; }}
.card p {{ margin-bottom: 8px; line-height: 1.5; }}
.card ul {{ margin-left: 20px; margin-bottom: 10px; }}
.card li {{ margin-bottom: 4px; line-height: 1.4; }}
.plot-row {{ display: flex; flex-wrap: wrap; gap: 12px; margin-bottom: 16px; }}
.plot-row > div {{ flex: 1; min-width: 300px; background: white; border-radius: 8px; padding: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
.tbl {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
.tbl th {{ background: #2c3e50; color: white; padding: 8px 10px; text-align: left; }}
.tbl td {{ padding: 6px 10px; border-bottom: 1px solid #ddd; }}
.tbl tr:nth-child(even) {{ background: #f9f9f9; }}
.table-wrap {{ overflow-x: auto; }}
a {{ color: #3498db; }}
@media (max-width: 768px) {{ .navbar a {{ font-size: 11px; padding: 4px 8px; }} .hero h1 {{ font-size: 22px; }} }}
</style>
</head>
<body>

<div class="navbar">{nav_links}</div>
<div class="container">{all_sections}</div>

<script>
function showSection(id) {{
  document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  window.scrollTo({{top: 0}});
}}
showSection('intro');
</script>
</body>
</html>"""

with open(f"{DASHBOARD_DIR}/index.html", "w") as f:
    f.write(html)

size = os.path.getsize(f"{DASHBOARD_DIR}/index.html") / 1024
print(f"  Dashboard saved: {DASHBOARD_DIR}/index.html ({size:.0f} KB)")
