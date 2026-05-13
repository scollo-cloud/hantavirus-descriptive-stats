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
# SECTION: Introduction & Summary Stats
# ════════════════════════════════════════════
def get_metric_card(label, value, sub):
    return f"""
    <div class="metric-card">
      <div class="metric-label">{label}</div>
      <div class="metric-value">{value}</div>
      <div class="metric-sub">{sub}</div>
    </div>
    """

summary_cards = f"""
<div class="metric-row">
  {get_metric_card("Total Patients", f"{len(df_clin):,}", "Clinical Records")}
  {get_metric_card("Avg Incubation", f"{df_clin['incubation_days'].mean():.1f}d", "across syndromes")}
  {get_metric_card("Global CFR", f"{df_yr['case_fatality_rate'].mean()*100:.1f}%", "Syndrome-dependent")}
  {get_metric_card("Max Rainfall", f"{df_env['rainfall_mm'].max():,.0f}mm", "biome extreme")}
</div>
"""

intro = f"""
<div class="hero">
  <h1>Hantavirus Descriptive Statistics</h1>
  <p class="subtitle">A deep dive into global epidemiological data with automated outlier detection and subgroup analysis.</p>
</div>
{summary_cards}
<div class="card">
  <h2>Dashboard Overview</h2>
  <p><strong>Goal:</strong> Transform raw global Hantavirus data into actionable insights through descriptive statistics.</p>
  <p><strong>Data:</strong> <a href="https://www.kaggle.com/datasets/zkskhurram/hantavirus-andes-virus-global-epidemiology" target="_blank">Kaggle Global Epidemiology</a></p>
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
  <img src="../figures/distributions/incubation_days_ecdf.png" style="max-width:100%; border:1px solid #ddd; border-radius:4px;">
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
  <div><img src="../figures/clinical/hospital_by_severity.png" style="max-width:100%; border:1px solid #ddd; border-radius:4px;"></div>
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
  <div><img src="../figures/clinical/icu_split.png" style="max-width:100%; border:1px solid #ddd; border-radius:4px;"></div>
  <div><img src="../figures/clinical/icu_by_severity.png" style="max-width:100%; border:1px solid #ddd; border-radius:4px;"></div>
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
  <div><img src="../figures/distributions/avg_temp_c_histogram.png" style="max-width:100%; border:1px solid #ddd; border-radius:4px;"></div>
  <div><img src="../figures/distributions/avg_temp_c_qq.png" style="max-width:100%; border:1px solid #ddd; border-radius:4px;"></div>
</div>

<div class="card">
  <h2>Rainfall</h2>
  <p><strong>Finding:</strong> Right-skewed (skew={stats.skew(rain):.2f}), heavy-tailed (kurtosis={stats.kurtosis(rain):.2f}). Biome explains 10x variation.</p>
</div>
<div class="plot-row">
  <div><img src="../figures/distributions/rainfall_mm_histogram.png" style="max-width:100%; border:1px solid #ddd; border-radius:4px;"></div>
  <div><img src="../figures/comparative/compare_rain_biome.png" style="max-width:100%; border:1px solid #ddd; border-radius:4px;"></div>
</div>

<div class="card">
  <h2>Rodent Abundance</h2>
  <p><strong>Finding:</strong> Most symmetric variable (skew={stats.skew(rodent):.2f}). Nearly constant across biomes (0.64–0.72 range).</p>
  <p><strong>Caveat:</strong> This assumes comparable sampling protocols across biomes.</p>
</div>
<div class="plot-row">
  <div><img src="../figures/distributions/rodent_abundance_index_histogram.png" style="max-width:100%; border:1px solid #ddd; border-radius:4px;"></div>
  <div><img src="../figures/distributions/rodent_abundance_index_qq.png" style="max-width:100%; border:1px solid #ddd; border-radius:4px;"></div>
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
  <div><img src="../figures/comparative/compare_cases_syndrome.png" style="max-width:100%; border:1px solid #ddd; border-radius:4px;"></div>
  <div><img src="../figures/boxplots/confirmed_cases_boxplot.png" style="max-width:100%; border:1px solid #ddd; border-radius:4px;"></div>
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
  <div><img src="../figures/distributions/case_fatality_rate_histogram.png" style="max-width:100%; border:1px solid #ddd; border-radius:4px;"></div>
  <div><img src="../figures/comparative/compare_cases_syndrome.png" style="max-width:100%; border:1px solid #ddd; border-radius:4px;"></div>
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
  <div><img src="../figures/comparative/compare_incubation_severity.png" style="max-width:100%; border:1px solid #ddd; border-radius:4px;"></div>
  <div><img src="../figures/comparative/compare_incubation_syndrome.png" style="max-width:100%; border:1px solid #ddd; border-radius:4px;"></div>
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
<img src="../figures/critique/critique_bar_vs_violin.png" style="max-width:100%; border:1px solid #ddd; border-radius:4px; margin-top:10px;">
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
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
:root {{
  --primary: #2563eb;
  --primary-dark: #1d4ed8;
  --secondary: #64748b;
  --bg: #f8fafc;
  --card-bg: #ffffff;
  --text: #1e293b;
  --text-light: #64748b;
  --border: #e2e8f0;
  --sidebar-width: 260px;
  --shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
}}

* {{ margin: 0; padding: 0; box-sizing: border-box; }}

body {{
  font-family: 'Inter', -apple-system, sans-serif;
  background-color: var(--bg);
  color: var(--text);
  line-height: 1.6;
  display: flex;
  min-height: 100vh;
}}

/* Sidebar */
.sidebar {{
  width: var(--sidebar-width);
  background: #1e293b;
  color: white;
  height: 100vh;
  position: sticky;
  top: 0;
  padding: 24px 0;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  box-shadow: 4px 0 10px rgba(0,0,0,0.1);
}}

.sidebar-header {{
  padding: 0 24px 24px;
  border-bottom: 1px solid rgba(255,255,255,0.1);
  margin-bottom: 24px;
}}

.sidebar-header h2 {{
  font-size: 18px;
  font-weight: 700;
  letter-spacing: -0.025em;
  color: #f8fafc;
}}

.nav-links {{
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  flex: 1;
}}

.nav-links a {{
  padding: 12px 24px;
  color: #94a3b8;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 12px;
}}

.nav-links a:hover {{
  background: rgba(255,255,255,0.05);
  color: white;
}}

.nav-links a.active {{
  background: var(--primary);
  color: white;
}}

/* Main Content */
.main-content {{
  flex: 1;
  padding: 40px;
  max-width: 1200px;
  margin: 0 auto;
}}

.section {{ display: none; animation: fadeIn 0.4s ease-out; }}
.section.active {{ display: block; }}

@keyframes fadeIn {{
  from {{ opacity: 0; transform: translateY(10px); }}
  to {{ opacity: 1; transform: translateY(0); }}
}}

/* Components */
.hero {{
  background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
  color: white;
  padding: 60px 40px;
  border-radius: 16px;
  margin-bottom: 32px;
  box-shadow: var(--shadow-lg);
}}

.hero h1 {{
  font-size: 36px;
  font-weight: 800;
  margin-bottom: 12px;
  letter-spacing: -0.025em;
}}

.hero p {{
  font-size: 18px;
  opacity: 0.9;
  max-width: 700px;
}}

.card {{
  background: var(--card-bg);
  border-radius: 16px;
  padding: 32px;
  margin-bottom: 24px;
  border: 1px solid var(--border);
  box-shadow: var(--shadow);
  transition: transform 0.2s, box-shadow 0.2s;
}}

.card:hover {{
  box-shadow: var(--shadow-lg);
}}

.card h2 {{
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 16px;
  color: #0f172a;
  display: flex;
  align-items: center;
  gap: 12px;
}}

.card h2::before {{
  content: '';
  display: inline-block;
  width: 4px;
  height: 24px;
  background: var(--primary);
  border-radius: 2px;
}}

.plot-row {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
  gap: 24px;
  margin-bottom: 24px;
}}

.metric-row {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
}}

.metric-card {{
  background: white;
  padding: 24px;
  border-radius: 16px;
  border: 1px solid var(--border);
  box-shadow: var(--shadow);
  text-align: center;
}}

.metric-label {{
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-light);
  margin-bottom: 8px;
}}

.metric-value {{
  font-size: 28px;
  font-weight: 800;
  color: var(--primary);
  margin-bottom: 4px;
}}

.metric-sub {{
  font-size: 12px;
  color: var(--text-light);
}}

.plot-container p.caption {{
  font-size: 14px;
  color: var(--text-light);
  margin-top: 12px;
  font-style: italic;
  text-align: center;
}}


/* Tables */
.table-wrap {{
  overflow-x: auto;
  border-radius: 12px;
  border: 1px solid var(--border);
  margin-top: 16px;
}}

.tbl {{
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}}

.tbl th {{
  background: #f8fafc;
  color: #475569;
  font-weight: 600;
  text-align: left;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border);
}}

.tbl td {{
  padding: 12px 16px;
  border-bottom: 1px solid var(--border);
  color: #1e293b;
}}

.tbl tr:last-child td {{ border-bottom: none; }}
.tbl tr:hover {{ background: #f1f5f9; }}

.badge {{
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
  background: #e2e8f0;
}}

.badge-primary {{ background: #dbeafe; color: #1e40af; }}

.badge-primary {{ background: #dbeafe; color: #1e40af; }}

@media (max-width: 1024px) {{
  body {{ flex-direction: column; }}
  .sidebar {{ width: 100%; height: auto; position: static; }}
  .sidebar-header {{ padding-bottom: 12px; margin-bottom: 12px; }}
  .nav-links {{ flex-direction: row; flex-wrap: wrap; padding: 0 12px; }}
  .nav-links a {{ padding: 8px 16px; }}
  .main-content {{ padding: 20px; }}
  .plot-row {{ grid-template-columns: 1fr; }}
}}
</style>
</head>
<body>

<div class="sidebar">
  <div class="sidebar-header">
    <h2>Hantavirus Stats</h2>
  </div>
  <div class="nav-links">
    {nav_links}
  </div>
</div>

<div class="main-content">
  {all_sections}
</div>

<script>
function showSection(id) {{
  document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('.nav-links a').forEach(a => a.classList.remove('active'));
  
  document.getElementById(id).classList.add('active');
  const activeLink = Array.from(document.querySelectorAll('.nav-links a')).find(a => a.getAttribute('onclick').includes(id));
  if (activeLink) activeLink.classList.add('active');
  
  window.scrollTo({{top: 0, behavior: 'smooth'}});
}}
showSection('intro');
</script>
</body>
</html>"""

with open(f"{DASHBOARD_DIR}/index.html", "w") as f:
    f.write(html)

size = os.path.getsize(f"{DASHBOARD_DIR}/index.html") / 1024
print(f"  Dashboard saved: {DASHBOARD_DIR}/index.html ({size:.0f} KB)")
