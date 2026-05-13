# Step B1 — Load & Inspect Each CSV

## What we did
Loaded every CSV file into pandas and printed: shape, column dtypes, missing values, duplicates, categorical value counts, numeric min/max, and the first 3 rows.

## Why each piece matters

### 1. Shape (rows × columns)
- Tells us the **size** of each dataset at a glance
- A very small dataset (like outbreaks.csv with 20 rows) means we can't trust statistics from it — small n leads to unreliable estimates
- A large dataset like clinical.csv (7538 rows) gives us stable estimates

### 2. Data types
- We check that numbers are recognized as numbers (`int64`, `float64`) and text as `object`
- **Red flag:** if a numeric column shows up as `object`, it means there's text hiding in it (like `"N/A"` or `"missing"`) — we need to clean that
- No such issues here, the data is well-typed

### 3. Missing values
- Tells us which columns have gaps and **how much** is missing
- We found two clean groups: symptoms missing at 35% and symptoms missing at 65%
- The exact, round percentages are a **structural clue** — this isn't random scatter
- **Key insight:** HPS patients don't have HFRS symptoms recorded, and vice versa. This is **Missing At Random (MAR)** — the missingness is caused by which syndrome the patient has
- **Implication:** we should NOT impute these. Imputing would create fake symptom data for a syndrome that doesn't even record that symptom

### 4. Duplicates
- 1 duplicate in 7538 rows is negligible (0.01%)
- If duplicates were high, it would mean double-counting — inflating sample size artificially
- This would make confidence intervals too narrow (false precision)

### 5. Categorical value counts
- We scan for **typos and inconsistent naming**
- Example of a problem: `"Mild"`, `"mild"`, `"MILD"` — should all be one category, but would show as 3 separate groups
- No issues here — the data is consistently labeled

### 6. Numeric min/max
- Quick sanity check for impossible values:
  - incubation_days: 7–42 (plausible for a virus)
  - hospital_days: 2–27 (plausible)
  - rainfall_mm: 0–1673 (physically possible, but the max is extreme — flag for outlier check)
  - rodent_abundance_index: 0.301–1.000 (within stated [0,1] range — good)

### 7. First 3 rows
- Final eyeball check
- Sometimes column headers shift into data rows, or formatting errors happen
- Nothing unusual here

## What we learned about our hantavirus data
| Dataset | Shape | Issues Found |
|---------|-------|-------------|
| clinical | 7538 × 29 | 14 symptom columns with structural missingness (MAR by syndrome) |
| environmental | 896 × 15 | None |
| country_yearly | 939 × 15 | None |
| master | 109 × 15 | None |
| monthly_trends | 924 × 5 | None |
| outbreaks | 20 × 10 | None (but very small n) |

## How this connects to descriptive statistics
Before you describe a dataset, you need to **trust** it. Step B1 is the "inspect before you trust" phase. If we had skipped this and gone straight to histograms, we might have:
- Plotted symptom data with missing values without knowing why
- Calculated averages on small datasets and treated them as reliable
- Missed the HPS/HFRS structural difference entirely
