# Step D1 — Questionnaire Results: User vs Numbers

## What the user observed (from plots)
- Median = 19, Q1 ≈ 14, Q3 ≈ 26
- Right-skewed (mean > median)
- Unimodal (one peak)
- Thin tail
- Not normal
- Log-histogram has comb/gaps

## What the numbers say
| Property | Numeric Value | Match? |
|----------|--------------|--------|
| Q1 | 13 | ✅ Close enough |
| Median | 19 | ✅ Exact |
| Q3 | 25 | ✅ Exact |
| Mean | 20.41 | ✅ |
| Skewness | +0.47 (moderate right) | ✅ Correct |
| Kurtosis | -0.49 (thin/light tails) | ✅ Correct |
| Shapiro-Wilk p | 0.000 (not normal) | ✅ Correct |

## Key insight from kurtosis
Kurtosis = -0.49 means **tails are thinner than normal**. Despite the right skew, values above ~35 days are actually *less common* than they would be in a perfectly normal distribution with the same mean and std.

## Best center for incubation_days
- Mean = 20.4, Median = 19
- Skew = 0.47 is moderate (|skew| < 0.5 means roughly symmetric)
- Either could be argued. In a report: *"Mean (20.4) slightly exceeds median (19), confirming mild right skew. Median is the more robust choice."*

## Best spread for incubation_days
- Std = 8.1, IQR = 12, MAD = 5
- With moderate skew → IQR is safest
- Std assumes symmetry, which we don't quite have
