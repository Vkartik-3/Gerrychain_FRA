# Gerrymandering Detection Methodology

## Table of Contents
1. [What is Gerrymandering?](#what-is-gerrymandering)
2. [Core Concepts](#core-concepts)
3. [Detection Method: Ensemble Analysis](#detection-method-ensemble-analysis)
4. [How We Detect Gerrymandering](#how-we-detect-gerrymandering)
5. [Step-by-Step Process](#step-by-step-process)
6. [Interpreting Results](#interpreting-results)
7. [Real-World Examples](#real-world-examples)
8. [Limitations and Caveats](#limitations-and-caveats)

---

## What is Gerrymandering?

**Gerrymandering** is the practice of manipulating district boundaries to favor one political party over another. There are two main techniques:

### 1. Packing
Concentrate opposition voters into a few districts that they win overwhelmingly (70-90%), wasting their votes.

**Example:**
- District 1: 90% DEM, 10% REP (DEM wins - but wastes 40% extra votes)
- District 2: 45% DEM, 55% REP (REP wins by small margin)
- District 3: 45% DEM, 55% REP (REP wins by small margin)

Result: 60% DEM votes statewide → only 33% of seats

### 2. Cracking
Spread opposition voters thinly across many districts so they never achieve a majority.

**Example:**
- District 1: 48% DEM, 52% REP (REP wins narrowly)
- District 2: 48% DEM, 52% REP (REP wins narrowly)
- District 3: 48% DEM, 52% REP (REP wins narrowly)

Result: 48% DEM votes → 0% of seats

---

## Core Concepts

### Geographic Units (Precincts)
- **Precinct**: Smallest voting unit, typically a neighborhood or small area
- Each precinct has:
  - Population count
  - Vote totals for each party
  - Geographic boundaries (polygon shapefile)
  - Adjacency information (which precincts border it)

### Districts
- **District**: A grouping of contiguous precincts
- Must satisfy legal constraints:
  - **Contiguity**: All precincts must be connected (can't have islands)
  - **Population balance**: Districts should have roughly equal population (±30% tolerance in our analysis)
  - **Compactness**: Districts shouldn't have bizarre shapes (though we don't enforce this strictly)

### Partition
- **Partition**: A complete assignment of all precincts to districts
- Example: Precinct A → District 1, Precinct B → District 2, etc.
- A valid partition covers all precincts exactly once

---

## Detection Method: Ensemble Analysis

Instead of trying to define what a "fair" map looks like mathematically, we use a **comparison-based approach**:

### The Core Idea
1. Generate thousands of random redistricting maps that satisfy all legal requirements
2. Measure the partisan outcomes of these random maps
3. See where the actual map falls in this distribution
4. If the actual map is an extreme outlier, it's suspicious

### Why This Works
- If a state naturally favors one party due to geography (e.g., Democrats clustered in cities), the random ensemble will show this
- If the actual map performs MUCH better for one party than 95%+ of random fair maps, that suggests intentional manipulation
- This method is **agnostic** - it doesn't assume proportional representation is the goal

---

## How We Detect Gerrymandering

### Step 1: Create Initial Partition
We use **Recursive Tree Partitioning** to create districts:

```
1. Build a graph where precincts are nodes, edges connect adjacent precincts
2. Randomly select a "root" precinct
3. Grow a tree from that root until it reaches target population
4. Cut that tree off as District 1
5. Repeat for remaining precincts until all districts are created
```

**Why recursive tree?**
- Guarantees contiguity (tree structure ensures connectivity)
- Balances population automatically
- Fast and simple

### Step 2: Generate Ensemble Using MCMC

We use **Markov Chain Monte Carlo (MCMC)** to explore the space of possible redistricting maps:

```
Starting from initial partition:
For each of 100-500 steps:
    1. Randomly select a precinct on a district boundary
    2. Propose flipping it to the neighboring district
    3. Check if this maintains contiguity
    4. If yes, accept the flip
    5. Record the partisan outcome
```

**Key properties:**
- **Random walk**: Each step makes a small change, gradually exploring different maps
- **Contiguity constraint**: Never accept a flip that breaks connectivity
- **Acceptance**: We accept all valid flips (no bias toward any outcome)
- **Ergodic**: Over time, explores the full space of possible fair maps

### Step 3: Calculate Partisan Outcomes

For each partition in the ensemble:

```python
for district in partition:
    dem_votes = sum of all DEM votes in precincts in this district
    rep_votes = sum of all REP votes in precincts in this district

    if dem_votes > rep_votes:
        DEM wins this district
    else:
        REP wins this district

# Count total DEM districts won
dem_wins = count of districts won by DEM
```

After 100 steps, we have a list like: `[3, 2, 3, 3, 2, 3, 3, 4, 3, 2, ...]`

### Step 4: Percentile Calculation

Compare the initial map to the ensemble distribution:

```python
# Count how many ensemble maps have fewer DEM wins than initial
below_initial = count(ensemble_value < initial_value)

# Count how many are equal
equal_initial = count(ensemble_value == initial_value)

# Calculate percentile using midpoint method (handles ties)
percentile = (below_initial + 0.5 * equal_initial) / total_ensemble * 100
```

**Example:**
- Initial map: 6 DEM districts
- Ensemble: [4, 5, 5, 6, 5, 6, 5, 4, 6, 5] (10 maps)
- Below: 4 maps have < 6 DEM districts
- Equal: 3 maps have = 6 DEM districts
- Percentile: (4 + 0.5×3) / 10 = 55%

**Interpretation:**
- **0-5%**: Extreme outlier favoring Republicans
- **5-25%**: Moderate Republican advantage
- **25-75%**: Normal range, not suspicious
- **75-95%**: Moderate Democratic advantage
- **95-100%**: Extreme outlier favoring Democrats

### Step 5: Flag Outliers

```python
if percentile < 5 or percentile > 95:
    FLAG AS SUSPICIOUS - Potential Gerrymandering
else:
    APPEARS FAIR
```

---

## Step-by-Step Process

### What Happens When You Run `quick_demo.py`

```
1. LOAD STATE DATA
   ├─ Read shapefile containing precinct boundaries
   ├─ Build adjacency graph (which precincts touch)
   └─ Extract election data (DEM votes, REP votes, population)

2. DETECT DATA COLUMNS
   ├─ Find population column (TOTPOP, POP, etc.)
   ├─ Find DEM column (PRES12D, SEN18D, etc.)
   └─ Find REP column (PRES12R, SEN18R, etc.)

3. CREATE INITIAL PARTITION
   ├─ Convert all data to numeric (fix string/int issues)
   ├─ Use recursive tree to create N districts
   └─ Ensure population balance (±30%)

4. CALCULATE INITIAL OUTCOME
   ├─ For each district, sum DEM and REP votes
   ├─ Determine winner of each district
   └─ Count total DEM districts won

5. RUN MCMC ENSEMBLE
   ├─ Start from initial partition
   ├─ For 100 iterations:
   │  ├─ Propose random boundary flip
   │  ├─ Check contiguity constraint
   │  ├─ Accept if valid
   │  └─ Record DEM districts won
   └─ Build distribution of outcomes

6. CALCULATE PERCENTILE
   ├─ Compare initial outcome to ensemble
   ├─ Use midpoint method for ties
   └─ Determine percentile rank

7. FLAG IF OUTLIER
   └─ If < 5% or > 95%, flag as suspicious
```

---

## Interpreting Results

### Example 1: Clear Gerrymandering

**State X:**
```
Initial map: 8/10 REP districts
Statewide vote share: 48% REP, 52% DEM
Ensemble: 4.2 avg REP districts (range: 3-6)
Initial map at 98.5 percentile
```

**Analysis:**
- Republicans got 48% of votes but 80% of seats
- Random fair maps give Republicans only ~42% of seats on average
- Initial map is at 98.5th percentile (better for REP than 98.5% of fair maps)
- **Verdict: ⚠️ SUSPICIOUS - Likely gerrymandered to favor Republicans**

### Example 2: Fair Map Despite Disproportionality

**State Y:**
```
Initial map: 5/5 DEM districts
Statewide vote share: 58% DEM, 42% REP
Ensemble: 5.0 avg DEM districts (range: 5-5)
Initial map at 50.0 percentile
```

**Analysis:**
- Democrats got 58% of votes and 100% of seats (seems unfair!)
- BUT all random fair maps ALSO give 5/5 to Democrats
- This is because DEM voters are evenly spread while REP voters are concentrated
- Geography naturally prevents Republicans from winning districts
- **Verdict: ✅ FAIR - Disproportional outcome is due to geography, not manipulation**

### Example 3: Borderline Case

**State Z:**
```
Initial map: 6/10 DEM districts
Statewide vote share: 54% DEM, 46% REP
Ensemble: 5.8 avg DEM districts (range: 4-7)
Initial map at 93.2 percentile
```

**Analysis:**
- Democrats got 54% of votes and 60% of seats (slightly disproportional)
- Ensemble average is 5.8, initial is 6
- At 93.2nd percentile - higher than most fair maps but not quite extreme
- **Verdict: ✅ FAIR (but close to threshold) - Possibly mild pro-DEM advantage, but within normal variation**

### Example 4: High Variation = Competitive State

**State W:**
```
Initial map: 5/9 DEM districts
Statewide vote share: 51% DEM, 49% REP
Ensemble: 4.8 avg DEM districts (range: 2-7)
Initial map at 58.3 percentile
```

**Analysis:**
- Wide ensemble range (2-7) indicates highly competitive geography
- Small changes in district lines can swing multiple seats
- Initial map is near the middle (58.3%)
- **Verdict: ✅ FAIR - Competitive state with high sensitivity to redistricting**

### Example 5: No Variation = Geography Locked

**Delaware (from our demo):**
```
Initial map: 2/3 DEM districts
Statewide vote share: 59.5% DEM
Ensemble: 2.0 avg DEM districts (range: 2-2)
Initial map at 50.0 percentile
```

**Analysis:**
- Zero variation in ensemble (all maps give 2/3)
- Geography/demographics make it impossible to draw districts any other way
- Literally cannot gerrymander even if you tried
- **Verdict: ✅ FAIR - Geography determines outcome completely**

---

## Real-World Examples

### North Carolina (Historical Example)

In 2016, North Carolina's congressional map was challenged in court:

**Actual Results:**
- Initial map: 10/13 REP districts (77%)
- Statewide vote: ~50% REP, 50% DEM
- If analyzed with our method, ensemble might show: 6.5 avg REP districts (range: 5-8)
- Percentile: ~99.5% (extreme outlier)

**What happened:**
- Court found intentional partisan gerrymandering
- Map was struck down and redrawn

**How our method would detect it:**
- 99.5th percentile → Flag as suspicious
- 10 REP districts vs 6.5 ensemble average = huge gap
- Clear signal of manipulation

### Wisconsin (Another Example)

Wisconsin's 2011 map:

**Results:**
- 2012 election: 60/99 REP state assembly seats (61%)
- Statewide vote: 48.6% REP, 51.4% DEM
- Republicans won majority despite losing popular vote

**Analysis approach:**
- Ensemble of fair maps would likely show: ~47% REP seats on average
- Actual map probably at >95th percentile
- Red flag for gerrymandering

---

## Limitations and Caveats

### 1. MCMC Exploration Limitations

**Issue:** MCMC might not explore the FULL space of possible maps

**Why:**
- Starting from one initial partition
- Only makes small local changes
- Might miss distant regions of the map space

**Mitigation:**
- Run longer chains (500+ steps instead of 100)
- Run multiple chains from different starting points
- Use more sophisticated proposals (not just single flips)

### 2. Number of Districts Matters

**Issue:** Fewer districts = less variation possible

**Example:**
- 3 districts: Limited possible outcomes
- 13 districts: Much more flexibility

**Impact:**
- Small states (Delaware, Vermont) show less variation
- Harder to detect gerrymandering in states with few districts

### 3. Data Quality

**Common issues we encountered:**
- String vs numeric data types (Vermont)
- Invalid geometries (North Carolina)
- Contiguity problems (Rhode Island)
- Missing election data

**Solution:** Robust error handling and data cleaning

### 4. Geography vs Gerrymandering

**Challenge:** How do you distinguish between:
- Natural geographic advantage (legal)
- Intentional manipulation (illegal)

**Our approach:**
- If geography causes the bias, random fair maps will show it
- Only flag maps that are outliers COMPARED to random fair maps
- This separates geographic effects from intentional design

### 5. Single Election Snapshot

**Issue:** We only look at one election year

**Problem:**
- Elections vary year to year
- 2012 might be a DEM wave, 2016 a REP wave
- A map might seem fair in 2012 but biased in 2020

**Better approach:**
- Test against multiple election years
- Look for consistent bias across cycles

### 6. Population Balance Tolerance

**Our setting:** ±30% population deviation

**Reality:**
- Federal law requires ≤1% for congressional districts
- State districts have more flexibility (~10%)
- Our 30% is very loose for demonstration purposes

**Impact:**
- More flexibility = more possible maps = harder to detect manipulation
- Tighter constraints = better reflects real requirements

### 7. Compactness Not Enforced

**We don't measure:**
- District shape "weirdness"
- Compactness scores
- Community of interest preservation

**Why:**
- Simplifies the algorithm
- Focuses purely on partisan outcomes
- Real-world maps must consider these factors

---

## How to Know When Gerrymandering Exists

### The Smoking Guns

**1. Extreme Percentile (<5% or >95%)**
- Most reliable indicator
- Means map is more extreme than 95% of fair alternatives
- Hard to explain by chance alone

**2. Disproportionality + Extreme Percentile**
- One party gets X% votes but Y% seats (where Y >> X or Y << X)
- AND this outcome is extreme in the ensemble
- Example: 48% votes → 75% seats + 98th percentile = clear manipulation

**3. Bizarre District Shapes (Visual Test)**
- Not in our analysis, but important
- Example: Maryland's 3rd district (looks like a dragon)
- Indicates intentional line-drawing to achieve partisan goals

**4. Persistence Across Elections**
- Same party keeps winning disproportionate seats
- Across multiple election cycles
- Despite changes in vote share

**5. Legislative Intent Evidence**
- Maps drawn by partisan legislature
- Explicit statements of intent (rare but it happens!)
- Racial or partisan data used in drawing process

### When NOT to Cry Gerrymandering

**1. Disproportional Results BUT Normal Percentile**
- Example: Iowa in our demo (50% votes → 75% seats but 50th percentile)
- Geography naturally causes this outcome
- Not manipulation

**2. High Percentile BUT Small Absolute Difference**
- Example: 5.2 DEM districts vs 5.0 ensemble average, 92nd percentile
- Technically high percentile but tiny real difference
- Probably just noise

**3. Urban/Rural Divide States**
- One party's voters clustered in cities, other spread in rural areas
- Naturally creates "packing" of urban party
- Not necessarily intentional

---

## Summary Decision Tree

```
Is the actual map at <5% or >95% percentile?
│
├─ NO (5-95%) → Probably FAIR
│   └─ Even if disproportional, it's within normal range
│
└─ YES (<5% or >95%) → SUSPICIOUS
    │
    ├─ Is the absolute difference large?
    │   ├─ YES (e.g., 8 districts vs 5 avg) → Likely GERRYMANDERED
    │   └─ NO (e.g., 5.2 vs 5.0 avg) → Possibly just noise
    │
    ├─ Is the ensemble range narrow or wide?
    │   ├─ NARROW (e.g., 5-5) → Geography determines outcome, FAIR
    │   └─ WIDE (e.g., 2-8) → Many alternatives possible, manipulation likely
    │
    └─ Does visual inspection show bizarre shapes?
        ├─ YES → Strong evidence of gerrymandering
        └─ NO → Might be subtle manipulation or just geography
```

---

## Conclusion

Our gerrymandering detection method:

**Strengths:**
✅ Objective and quantitative
✅ Accounts for geographic realities
✅ Doesn't assume proportional representation is always fair
✅ Detects both pro-DEM and pro-REP bias
✅ Provides statistical confidence (percentile)

**Weaknesses:**
❌ Computationally intensive
❌ Requires good data quality
❌ May miss some forms of manipulation
❌ Doesn't consider compactness, communities of interest
❌ Single-election snapshot

**Best Use:**
- Screening tool to identify suspicious maps
- Provide statistical evidence for court cases
- Compare multiple redistricting proposals
- Educate public about gerrymandering

**Bottom Line:**
If a map scores <5% or >95% percentile with a large absolute difference from the ensemble mean and wide ensemble variation, that's strong evidence of gerrymandering worthy of further investigation and possible legal challenge.
