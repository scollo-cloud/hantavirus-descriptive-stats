# Phase E1 — Comparative Violin Plots

## What we did
Created side-by-side violin plots comparing key variables across subgroups.

## Comparisons made

### 1. Incubation by severity
- All four severity levels have nearly identical incubation (~19d median)
- **Lesson:** Severity does NOT affect incubation period — it's determined by the virus, not the patient's condition
- Script: `E1_comparative_violins.py`

### 2. Incubation by outcome
- Recovered: median=20d, Deceased: median=17d
- Deceased patients had slightly shorter incubation — possibly more aggressive disease
- But the difference is small (3 days)

### 3. Incubation by syndrome
- HPS: median=16d, HFRS: median=22d
- Real biological difference between the two syndrome types
- HPS incubates faster

### 4. Hospital days by severity
- Already analyzed in D2 — clean separation between all 4 levels

### 5. Temperature by biome
- 14 biomes sorted coldest to warmest
- Ranges from Boreal taiga (cold) to Valdivian forest/Atlantic forest (warm)
- Labels improved to be readable (wider figure, larger margins)

### 6. Rainfall by biome
- 14 biomes sorted driest to wettest
- Desert scrub (63mm) to Valdivian forest (630mm) — 10x difference
- Labels improved similarly for readability

### 7. Confirmed cases by syndrome
- HPS vs HFRS shown both with all data and with outliers removed
- HPS: mean=30/yr, HFRS: mean=2515/yr — massive difference

### 8. CFR by syndrome (already in D8)
- HPS: 28.1% vs HFRS: 1.4% — 20x difference

## Key takeaways
- Group comparisons reveal patterns invisible in aggregate
- Some variables differ by syndrome (incubation, cases, CFR)
- Some differ by severity (hospital, ICU days)
- Some differ by biome (rainfall, temperature)
- Some are constant across groups (rodent abundance)
