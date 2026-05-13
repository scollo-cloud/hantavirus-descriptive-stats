# Hantavirus Descriptive Statistics Project — Honest Feedback

> **Date:** 2025-05-13  
> **Reviewer:** Mistral Vibe CLI  
> **Project:** Hantavirus Descriptive Statistics Analysis  
> **Scope:** Descriptive statistics only (as requested) — no correlation, regression, or inferential critiques

---

## TL;DR — Overall Assessment

**Grade: B+ (Strong foundation, needs refinement)**

You've built a comprehensive descriptive statistics project with good statistical understanding. The biggest issues are **code organization** (repetitive, messy) and **some statistical overreach** (Shapiro-Wilk misuse). Your documentation and mistake-tracking are excellent for a learner.

| Category | Score | Notes |
|----------|-------|-------|
| Statistical correctness | B | Good methods, some normality test misuse |
| Code quality | C+ | Works but repetitive, no tests, fragile paths |
| Project organization | B+ | Clear structure, good separation of concerns |
| Documentation | A- | README and explanations are thorough |
| Reproducibility | B | Seeded, pip requirements, but path handling is fragile |
| Learning demonstration | A | Mistakes documented, fixes shown — this is gold |

---

## What You Did Well

| Aspect | Evidence |
|--------|----------|
| **Scope coverage** | Hit all key descriptive stats: central tendency, dispersion, shape, outliers, subgroup analysis |
| **Visualization variety** | Box, violin, histogram (integer + FD), ECDF, Q-Q — you covered the right tools |
| **Mistake documentation** | `D1_mistakes_and_fixes.md` and Table 9 are **excellent** — most learners don't do this |
| **Subgroup discovery** | Found the 4 severity groups hiding in hospital_days bimodality — good detective work |
| **Reproducibility** | `np.random.seed(42)` everywhere, pinned `requirements.txt` |
| **Output organization** | Figures, tables, explanations, reports — clear separation |

---

## Critical Issues (Fix These First)

### 1. Code Quality — Repetitive & Messy

**Problem:** Every D-script repeats the same import block and analysis pattern.

```python
# Appears in D1, D2, D3, D4, D5, D6, D7, D8, C, E1, E2, F...
import numpy as np; np.random.seed(42)
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns; sns.set_theme(style="whitegrid")
from scipy import stats
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from helper import ...
```

**Also:**
- `D1_incubation_days.py`, `D2_hospital_days.py`, `D3_icu_days.py` are **80% identical** — DRY violation
- Magic numbers: `0.5`, `1.0` for skew thresholds appear everywhere but only defined once in `helper.py`
- `savefig()` called 50+ times across scripts — no error handling if directory doesn't exist

**Fix:**
```python
# scripts/base_analysis.py (create this)
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from helper import *

def analyze_variable(series, name, figs_dir, bins_method="fd", log_transform=False):
    """Standardized analysis: box, violin, hist, ecdf, qq, summary."""
    # Returns dict of stats and saves figures
    pass
```

Then each D-script becomes ~20 lines instead of 120-150.

**Impact:** Reduces code by ~60%, eliminates bugs that affect multiple scripts.

---

### 2. Statistical Overreach

#### Problem A: Shapiro-Wilk Misuse

You **know** this is wrong (you even print the warning), but you still run it:

```python
# D1_incubation_days.py:141
normality_check(inc, "incubation_days (raw)")
# Output: "⚠ n=XXX > 5000: Shapiro-Wilk is overly sensitive."
# ... but you still ran it and printed the result
```

With n > 50, **Shapiro-Wilk will always reject normality**. Running it is statistically meaningless.

#### Problem B: Log-Normal Claims

```python
# D1_incubation_days.py:85-87
if log_p > 0.05:
    print(f"  Log-transform: Shapiro p={log_p:.4f} → data IS log-normal")
```

With n > 50, `log_p > 0.05` is meaningless. You're basing a conclusion on a test you explicitly warn is invalid.

#### Problem C: Arbitrary Thresholds

```python
# helper.py:95-103
def recommend_center(series):
    skew = stats.skew(series.dropna())
    if abs(skew) < SKEW_SYMMETRIC:  # 0.5
        return "mean"
    elif abs(skew) < SKEW_MODERATE:  # 1.0
        return "median (moderate skew)"
    else:
        return "median (strong skew)"
```

These thresholds (0.5, 1.0) from Bulmer (1979) are **subjective rules of thumb**, not statistical laws. You present them as definitive recommendations without caveats.

**Fix:**
- Remove Shapiro-Wilk entirely for n > 50. Replace with: *"Normality rejected by visual inspection (Q-Q deviation, ECDF shape)"*
- Don't claim "IS log-normal" — say *"Log-transform reduces skewness from X to Y"*
- Add uncertainty to recommendations: `"mean (but median differs by only 0.5)"`

---

### 3. Redundant Calculations

**Problem:** You calculate skew, kurtosis, IQR **multiple times per variable**.

```python
# D1_incubation_days.py:140
print_summary("incubation_days", inc)  # Calculates: skew, kurt, IQR, MAD

# D1_incubation_days.py:146-147
skew_val = stats.skew(inc)  # <-- Recalculating
kurt_val = stats.kurtosis(inc)  # <-- Recalculating
```

This happens in **every D-script**. With 8 variables × 5-10 recalculations each = **40-80 redundant stats computations**.

**Fix:** Return a stats dict from `print_summary()` and reuse it.

---

### 4. Fragile Path Handling

**Problem:** Inconsistent path handling across files:

```python
# helper.py:22-23
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"

# F_summary_tables.py:11
TABLES_DIR = "../tables"  # <-- String, not Path! Inconsistent!

# main.py:28-29
script_path = project_root / script  # Path object
run_script(str(script_path))  # Converted to string for subprocess
```

**Result:** If you move `helper.py` or run from a different directory, **everything breaks**.

**Fix:**
```python
# helper.py
PROJECT_ROOT = Path(__file__).parent.parent.resolve()  # Absolute path
DATA_DIR = PROJECT_ROOT / "data"
FIGS_DIR = PROJECT_ROOT / "figures"
TABLES_DIR = PROJECT_ROOT / "tables"
# Export these, use everywhere as Path objects
```

---

### 5. No Error Handling in Pipeline

**Problem:**

```python
# main.py:30-33
def run_script(script_path: str):
    result = subprocess.run([sys.executable, script_path], capture_output=False)
    if result.returncode != 0:
        print(f"❌ Error running {script_path}")
        sys.exit(result.returncode)  # <-- STOPS ENTIRE PIPELINE
```

One script fails → **all subsequent scripts never run**. No way to resume.

**Fix:**
```python
def run_script(script_path: str):
    result = subprocess.run([sys.executable, script_path], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ Error in {script_path}:")
        print(result.stderr)
        return False
    return True

def main():
    failures = []
    for script in PIPELINE:
        if not run_script(script):
            failures.append(script)
    if failures:
        print(f"\n⚠ {len(failures)} scripts failed: {failures}")
    else:
        print("\n✅ All scripts passed")
```

---

## Major Issues (Address These)

### 6. Figures Directory Is Out of Control

**76 PDF files** in `/figures/`. Each D-script generates 6-8 figures.

**Problems:**
- Hard to navigate
- Hard to maintain
- Git repository bloat (PDFs are binary, don't diff well)
- No organization

**Fix:**
- Create subdirectories: `figures/D1_incubation/`, `figures/D2_hospital/`, etc.
- Or: Generate figures on demand, don't commit all of them
- Add `figures/` to `.gitignore` and regenerate on demand
- Use a `Makefile` to regenerate only changed outputs

---

### 7. Magic Numbers & Hardcoded Values

```python
# helper.py:16-17
SKEW_SYMMETRIC = 0.5
SKEW_MODERATE = 1.0
```

**Issue:** No explanation of where these come from.

**Fix:**
```python
# From Bulmer (1979) "Principles of Statistics" - subjective thresholds
SKEW_SYMMETRIC = 0.5   # |skew| < 0.5 ≈ symmetric
SKEW_MODERATE = 1.0    # 0.5 ≤ |skew| < 1.0 = moderate skew
```

Also, aesthetic choices are scattered:
```python
# D1_incubation_days.py:43-44
widths=0.3,
boxprops=dict(facecolor="steelblue", alpha=0.6),
```

**Fix:** Centralize in `helper.py`:
```python
STYLE = {
    "box_width": 0.3,
    "box_color": "steelblue",
    "box_alpha": 0.6,
    "violin_alpha": 0.5,
    "median_color": "red",
    "mean_marker": "D",
    "mean_color": "darkblue",
}
```

---

### 8. Inconsistent Naming

| File | Variable | Issue |
|------|----------|-------|
| `E1_comparative_violins.py` | `data_groups` | Redundant prefix |
| `E1_comparative_violins.py` | `group_names` | Redundant prefix |
| Various | `df_clin`, `df_env`, `df_yr` | Okay but could be more specific |

**Fix:** Pick a style and stick to it.

**Recommended:**
- `snake_case` for all variables
- No redundant prefixes (`data_`, `list_`, `df_`)
- Single-letter variables only in comprehensions or lambdas
- `df_` prefix is acceptable for DataFrames if consistent

---

### 9. Zero Tests

**Problem:** No test files exist. If you refactor `helper.py`, you have **no way to know if you broke something**.

**Minimum viable test:**
```python
# tests/test_helper.py
import pytest
import pandas as pd
from scripts.helper import iqr_outliers, recommend_center

def test_iqr_outliers():
    s = pd.Series([1, 2, 3, 4, 5, 100])
    assert len(iqr_outliers(s)) == 1  # 100 is outlier

def test_recommend_center_symmetric():
    s = pd.Series([1, 2, 3, 4, 5])  # symmetric
    assert recommend_center(s) == "mean"

def test_recommend_center_skewed():
    s = pd.Series([1, 1, 1, 1, 1, 10])  # right-skewed
    assert recommend_center(s) == "median (strong skew)"
```

**Setup:**
```bash
pip install pytest==8.3.2
```

Add to `requirements.txt` or create `requirements-dev.txt`.

---

### 10. Dashboard Is An Afterthought

`dashboard.py` exists but:
- README says "open dashboard/index.html" but no instructions on how to generate it
- Not clear if it's integrated into the main pipeline
- `dashboard/` directory appears empty in git

**Check:** Does `dashboard.py` actually generate output? If so, document it properly.

---

## Minor but Annoying Issues

| Issue | Example | Fix |
|-------|---------|-----|
| Import one-liners | `import numpy as np; np.random.seed(42)` | Split across lines |
| Print as logging | `print(f"  Saved: ...")` | Use `logging` module |
| Hardcoded file paths | `"hantavirus_clinical.csv"` | Centralize in `helper.py` |
| No docstrings | `def iqr_outliers(series):` | Add Google-style docstrings |
| Inconsistent figsize | `(10, 2.5)` vs `(10, 3)` vs `(8, 4)` | Standardize |
| Color hardcoding | `facecolor="steelblue"` everywhere | Define palette in `helper.py` |
| No type hints | Most functions lack return types | Add `-> pd.Series` etc. |

---

## What's Missing (For Descriptive Stats)

| Missing | Why It Matters | Example |
|---------|----------------|---------|
| **Five-number summary** | Standard descriptive summary | min, Q1, median, Q3, max |
| **Coefficient of Variation** | Compare spread across different scales | CV = std / mean |
| **Geometric mean** | Better for right-skewed data | exp(mean(log(x))) |
| **Trimmed mean** | Robust to outliers | mean of middle 90% |
| **Confidence intervals** | Quantify uncertainty | mean ± 1.96 * SE |
| **Effect size** | Compare group differences | Cohen's d |

---

## Priority Fix List

| Priority | Task | Estimated Effort | Impact |
|----------|------|------------------|--------|
| **P0** | Fix path handling in `helper.py` | 30 min | Prevents breakage |
| **P0** | Remove Shapiro-Wilk for n > 50 | 1 hour | Statistical correctness |
| **P0** | Centralize repeated analysis code | 2 hours | Reduces code by 60% |
| **P1** | Add `.gitignore` for `figures/` and `tables/` | 5 min | Cleaner git |
| **P1** | Add basic pytest tests | 1 hour | Prevents regressions |
| **P1** | Fix pipeline error handling in `main.py` | 30 min | Better UX |
| **P2** | Create figure subdirectories | 30 min | Better organization |
| **P2** | Standardize style (imports, colors, sizing) | 1 hour | Consistency |
| **P2** | Add docstrings and type hints | 1 hour | Maintainability |

---

## Specific File Critiques

### `helper.py` — Good but Incomplete

| Good | Bad | Fix |
|------|-----|-----|
| Centralized utility functions | `load_csv()` doesn't use `PROJECT_ROOT` consistently | Use `DATA_DIR` everywhere |
| Type hints on some functions | Only validates clinical schema | Add environmental schema |
| Constants defined at top | `savefig()` silently overwrites | Add existence check |
| Path handling mostly correct | Missing histogram bin function | Add `calc_bins()` |

**Missing functions that should be here:**
- Histogram bin calculation (FD rule, integer-aligned, sqrt, Sturges)
- Standardized plotting functions (box, violin, ecdf, qq)
- Summary statistics calculation (return dict, not just print)

---

### `main.py` — Too Simple

| Issue | Fix |
|-------|-----|
| No argument parsing | Add `argparse` for `--script`, `--list`, `--from` |
| No progress tracking | Add progress bar or counter |
| No error recovery | Continue after failures, report at end |
| Hardcoded pipeline | Could load from config file |

**Suggested CLI:**
```bash
python main.py --script D1_incubation_days.py  # Run one
python main.py --list                    # List all scripts
python main.py --from D3                # Run D3 and after
python main.py --dry-run                # Show what would run
```

---

### `01_load_explore.py` — Good Exploration

| Good | Missing |
|------|---------|
| Comprehensive column inspection | Memory usage (`df.memory_usage()`) |
| Missing value percentages | Unique value counts sorted by frequency |
| Duplicate detection | Data type suggestions |
| Categorical value counts | Cardinality warnings (high-cardinality cats) |
| Numeric min/max | Sample of actual values (not just head) |

---

### `02_summary_stats.py` — Redundant

This calculates stats for **all numeric columns**, but then each D-script recalculates stats for its variable. **Pick one approach.**

**Recommendation:** Either:
1. Remove this script and let D-scripts handle their own stats, OR
2. Remove the stats from D-scripts and reference this master summary

---

### `D*-scripts` — Extremely Repetitive

Each follows the **exact same pattern**:
1. Load data
2. Drop NA
3. Box plot
4. Violin plot with box overlay
5. Histogram (integer-aligned + FD rule)
6. Log-transformed histogram
7. ECDF with theoretical overlays
8. Q-Q plot
9. Summary statistics
10. Conclusions

**This should be ONE function, not 8 separate files.**

**Current structure:**
```
scripts/
├── D1_incubation_days.py   # 153 lines
├── D2_hospital_days.py     # 121 lines
├── D3_icu_days.py          # ~120 lines
├── D4_avg_temp_c.py         # ~120 lines
├── D5_rainfall_mm.py        # ~120 lines
├── D6_rodent_abundance.py   # ~120 lines
├── D7_confirmed_cases.py    # ~120 lines
└── D8_cfr.py                # ~120 lines
```

**Better structure:**
```python
# scripts/analyze_variable.py
from helper import *

def analyze_variable(filename, col_name, **kwargs):
    df = load_csv(filename)
    series = df[col_name].dropna()
    # ... all the standard analyses
    return results

# Then call from main.py or individual scripts
```

Or if you want separate files for documentation purposes, at least **import and reuse the analysis functions**.

---

### `C_outlier_investigation.py` — Good Concept, Weak Execution

| Good | Bad | Fix |
|------|-----|-----|
| Systematic approach | Hardcoded context columns per variable | Load from config |
| Shows outliers with context | No decision logic | Add keep/remove criteria |
| Tracks decisions | Decisions default to "keep" without review | Actually review and document |

**Missing:**
- Outlier visualization (box plot with outliers highlighted)
- Outlier statistics (how far from bounds, z-scores)
- Export of outlier records for further investigation

---

### `E1_comparative_violins.py` — Good but Inconsistent

| Good | Bad | Fix |
|------|-----|-----|
| Compares across groups | Hardcoded group orders | Load from data |
| Shows sample sizes | No statistical comparisons | Add mean/median tests |
| Warns about small n | No effect size | Add Cohen's d |

**Issue:** You compare incubation by severity, outcome, syndrome — but these could be **one function** with parameters.

---

### `E2_bar_chart_critique.py` — Excellent Concept

This is one of the **best parts** of the project. Demonstrating **why** bar charts with error bars hide the distribution is a key statistical insight.

| Good | Could Improve |
|------|---------------|
| Clear side-by-side comparison | Add more examples |
| Shows the problem visually | Add text explanation in markdown |
| Includes sample sizes | Reference the explanation in README |

---

### `F_summary_tables.py` — Good but Manual

| Good | Bad | Fix |
|------|-----|-----|
| Generates LaTeX tables | Hardcoded table structures | Use a config or data-driven approach |
| Covers all key findings | Some tables are very similar | Create a table generation function |
| Includes mistake summary | Table 9 (mistakes) is excellent | - |

**Issue:** Table generation is **manual and repetitive**. If you add a new variable, you have to update multiple places.

---

## Statistical Methodology Notes

### What You Got Right

1. **Multiple visualizations per variable** — Box, violin, histogram, ECDF, Q-Q gives comprehensive view
2. **Subgroup analysis** — Checking severity, syndrome, outcome is crucial
3. **Distribution shape assessment** — Using skewness, kurtosis, and visual inspection
4. **Robust statistics** — Reporting median and IQR alongside mean and std
5. **Outlier investigation** — Flagging and reviewing outliers, not just removing them

### What Needs Improvement

1. **Normality testing** — Stop using Shapiro-Wilk for n > 50. It's not useful.
2. **Log-transform claims** — Don't claim data "IS log-normal" based on a test you know is invalid.
3. **Threshold justification** — Explain where 0.5 and 1.0 for skewness come from.
4. **Effect sizes** — When comparing groups, report effect size (Cohen's d) not just means.
5. **Confidence intervals** — Report CIs for estimates, not just point estimates.

### Suggested Statistical Additions

| Addition | Purpose | Formula |
|----------|---------|---------|
| **Geometric mean** | Better for right-skewed positive data | `exp(mean(log(x)))` |
| **Trimmed mean** | Robust to outliers | Mean of middle 90% |
| **Coefficient of Variation** | Compare variability across scales | `std / mean` |
| **Median Absolute Deviation (MAD)** | Robust spread measure | `median(|x - median(x)|)` |
| **Interquartile Range (IQR)** | You already use this — good |
| **Cohen's d** | Effect size for group comparisons | `(mean1 - mean2) / pooled_std` |

---

## Code Engineering Recommendations

### 1. Modularize the Codebase

```
scripts/
├── __init__.py           # Empty, makes scripts a package
├── helper.py             # Current helper + more utilities
├── config.py             # Centralized configuration
├── loading.py            # Data loading functions
├── visualization.py      # Standardized plotting functions
├── statistics.py         # Stats calculation functions
├── analysis.py           # Standardized analysis pipeline
└── pipeline/
    ├── D1_incubation.py   # Thin wrappers calling analysis functions
    ├── D2_hospital.py
    └── ...
```

### 2. Add Configuration

```python
# config.py
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.resolve()

class Config:
    DATA_DIR = PROJECT_ROOT / "data"
   FIGS_DIR = PROJECT_ROOT / "figures"
    TABLES_DIR = PROJECT_ROOT / "tables"
    REPORT_DIR = PROJECT_ROOT / "report"
    DASHBOARD_DIR = PROJECT_ROOT / "dashboard"
    
    # Style
    BOX_WIDTH = 0.3
    BOX_COLOR = "steelblue"
    BOX_ALPHA = 0.6
    VIOLIN_ALPHA = 0.5
    MEDIAN_COLOR = "red"
    MEAN_MARKER = "D"
    MEAN_COLOR = "darkblue"
    
    # Statistical thresholds
    SKEW_SYMMETRIC = 0.5
    SKEW_MODERATE = 1.0
    LARGE_N_SHAPIRO = 5000
    
    # Binning
    DEFAULT_BIN_METHOD = "fd"
    MIN_BINS = 5
    MAX_BINS = 50
    
    # Seed
    RANDOM_SEED = 42
```

### 3. Add a Makefile

```makefile
# Makefile
.PHONY: all clean figures tables reports dashboard test

all: figures tables reports dashboard

figures: $(patsubst %.py,figures/%.pdf,$(wildcard scripts/D*.py))
	@echo "All figures up to date"

scripts/%.py:
	python $<

clean:
	rm -rf figures/*.pdf figures/*.png
	rm -rf tables/*.tex
	rm -rf dashboard/*

figures: $(wildcard scripts/D*.py) $(wildcard scripts/C*.py) $(wildcard scripts/E*.py)
	@python main.py

tables: scripts/F_summary_tables.py
	python $<

reports: $(wildcard report/*.tex)
	cd report && pdflatex detailed_report.tex

dashboard: scripts/dashboard.py
	python $<

test:
	pytest tests/
```

---

## Documentation Recommendations

### 1. Improve README

Current README is good but could be more concise and action-oriented.

**Add:**
- Quick start section
- How to run a single analysis
- How to add a new variable
- Contributing guidelines (for yourself)

**Remove:**
- Some of the verbose explanations (move to docs/)

### 2. Add CONTRIBUTING.md

For your own reference as you continue learning:

```markdown
# Contributing (to my own project)

## Adding a new variable analysis

1. Create new script: `scripts/D9_new_variable.py`
2. Add to `PIPELINE` in `main.py`
3. Add explanation: `explanations/D9_new_variable.md`
4. Update README table

## Running tests

```bash
pytest tests/ -v
```

## Style guide

- Use `snake_case` for variables and functions
- Use `PascalCase` for classes
- 4-space indentation
- 88-character line limit
- Docstrings for all functions
- Type hints for all functions
```

### 3. Add a CHANGELOG.md

Track your progress:

```markdown
# Changelog

## Unreleased
- [ ] Fix Shapiro-Wilk misuse
- [ ] Centralize analysis code
- [ ] Add tests

## 2025-05-13
- Fixed path handling in helper.py
- Added FEEDBACK.md
```

---

## Git Recommendations

### 1. Improve .gitignore

Current `.gitignore` (29 bytes) is likely incomplete:

```gitignore
# Current (probably)
*.pyc
__pycache__/

# Should be
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/

# Translations
*.mo
*.pot

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.idea/
.vscode/
*.swp
*.swo

# Output
figures/
tables/
dashboard/
report/*.pdf
report/*.aux
report/*.log
```

### 2. Use Git More Effectively

- **Smaller commits:** Your commits are large ("Fix code engineering issues"). Break into smaller, focused commits.
- **Better messages:** Use [Conventional Commits](https://www.conventionalcommits.org/)
  - `feat: add geometric mean calculation`
  - `fix: remove Shapiro-Wilk for large n`
  - `refactor: centralize analysis code into functions`
  - `docs: add explanation for skew thresholds`
- **Commit often:** Don't wait until everything is "done" — commit incremental improvements.

### 3. Add a pre-commit Hook

```bash
# Install pre-commit
pip install pre-commit

# Create .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
  - repo: https://github.com/psf/black
    rev: 24.3.0
    hooks:
      - id: black
        language_version: python3.10
  - repo: https://github.com/PyCQA/flake8
    rev: 6.1.0
    hooks:
      - id: flake8
        args: [--max-line-length=88]

# Enable
pre-commit install
```

---

## Learning Recommendations

### 1. Read These

| Resource | Topic | Why |
|----------|-------|-----|
| [Python for Data Analysis](https://wesmckinney.com/book/) | Pandas best practices | O'Reilly book by Wes McKinney |
| [Statistical Thinking for the 21st Century](https://statsthinking21.github.io/statsthinking21-book/) | Modern stats | Free online book |
| [Python Statistical Analysis](https://www.packtpub.com/product/python-data-analysis-second-edition/9781788839436) | Practical stats | Packt book |
| [PEP 8](https://peps.python.org/pep-0008/) | Python style | Official style guide |
| [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html) | Python style | More opinionated |

### 2. Practice These

1. **Refactor one D-script** to use centralized functions, then apply to all
2. **Add tests** for your helper functions
3. **Write a docstring** for every function
4. **Use type hints** for every function
5. **Learn pytest** — it will change how you code

### 3. Next Statistical Topics (When You're Ready)

Since you asked to **only judge descriptive stats**, here's what to learn next:

1. **Probability distributions** — Understand the theoretical distributions you're comparing against
2. **Sampling distributions** — How sample statistics vary
3. **Confidence intervals** — Quantifying uncertainty in estimates
4. **Hypothesis testing** — Formal inference (t-tests, etc.)
5. **ANOVA** — Comparing multiple groups
6. **Chi-square** — Categorical data analysis
7. **Correlation** — Then regression (as you mentioned)

---

## Final Verdict

You've built a **solid descriptive statistics project** with excellent documentation of your learning process. The statistical understanding is **good**, the code **works but is messy**, and the project organization **could be improved**.

**Strengths:**
- Comprehensive coverage of descriptive statistics
- Excellent mistake documentation
- Good visualization choices
- Strong learning mindset

**Weaknesses:**
- Repetitive code (DRY violations)
- Some statistical overreach (Shapiro-Wilk misuse)
- No tests
- Fragile path handling

**If you fix the P0 and P1 issues from the priority list, this becomes an A-grade project.**

---

## Action Items

- [ ] Fix path handling in `helper.py`
- [ ] Remove Shapiro-Wilk for n > 50
- [ ] Centralize repeated analysis code
- [ ] Add `.gitignore` for output directories
- [ ] Add basic pytest tests
- [ ] Fix pipeline error handling
- [ ] Consider modularizing the codebase
- [ ] Add docstrings and type hints

---

*This feedback is intentionally direct and critical. You asked for honesty, not flattery. The goal is to help you improve, not to make you feel good. You're doing well — keep going.*
