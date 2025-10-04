# Complete Guide: Understanding All GerryChain Example Files

**Purpose:** Explain what each file does, why we need it, and when to use it.

---

## Quick Reference Table

| File | Complexity | Runtime | Best For | Status |
|------|-----------|---------|----------|--------|
| `test_installation.py` | ⭐ Beginner | 5 sec | Verify setup | ✅ Works |
| `simple_simulation.py` | ⭐⭐ Beginner | 30 sec | Learn basics | ✅ Works |
| `detect_gerrymandering.py` | ⭐⭐ Intermediate | 2 min | Compare fair vs biased | ⚠️ Untested |
| `working_gerrymander_demo.py` | ⭐⭐⭐ Intermediate | 3 min | Realistic scenarios | ✅ Works |
| `gerrymandering_detection.py` | ⭐⭐⭐ Intermediate | 4 min | Polarized cities | ⚠️ Untested |
| `clear_gerrymander_example.py` | ⭐⭐⭐⭐ Advanced | 3 min | Seed-based search | ✅ Works |
| `extreme_gerrymandering.py` | ⭐⭐⭐⭐⭐ Advanced | 4 min | Detect suspicious maps | ✅ Fixed |

---

## The Learning Path: Which File to Run First?

### Level 1: Complete Beginner (Start Here!)

#### 1. `test_installation.py` - "Hello World" for GerryChain

**What it does:**
- Checks if GerryChain is installed correctly
- Creates a tiny 3×3 grid
- Makes sure basic imports work
- Prints success message

**Why you need it:**
- Verify your environment is set up correctly
- Quick smoke test (5 seconds)
- Fix dependency issues before running complex examples

**How to run:**
```bash
source .venv/bin/activate
python test_installation.py
```

**Expected output:**
```
Testing GerryChain installation...
✅ All imports successful
✅ Basic graph creation works
✅ GerryChain installation successful!
```

**When to use it:**
- First time using GerryChain
- After reinstalling dependencies
- Debugging environment issues

---

#### 2. `simple_simulation.py` - Your First Real Simulation

**What it does:**
1. Creates an **8×8 city grid** (64 blocks, ~638 people)
2. Randomly assigns voting preferences to each block
3. Divides city into **4 districts**
4. Runs **1000 MCMC steps** to generate alternative fair maps
5. Checks if original map is statistically normal

**Why you need it:**
- **Simplest working example** of gerrymandering detection
- Shows the complete MCMC workflow in ~30 seconds
- Uses neutral/random data (no intentional bias)
- Perfect for understanding the basic algorithm

**Key concepts demonstrated:**
- Grid graph creation
- Random population assignment
- MCMC simulation loop
- Statistical distribution analysis
- P-value interpretation

**How to run:**
```bash
source .venv/bin/activate
python simple_simulation.py
```

**Expected output:**
```
🚀 GerryChain Gerrymandering Detection Simulation
============================================================
🏙️  Creating 8x8 city grid...
✅ Created city with 64 blocks and 638 people
🗺️  Dividing city into 4 districts...
✅ Initial districts created:
   District 0: 149 people, 73 vs 76 votes → Party B wins
   District 1: 160 people, 87 vs 73 votes → Party A wins
   ...

🎲 Running MCMC simulation for 1000 steps...
   Step 200: Generated 200 alternative maps
   ...

📊 Analyzing Results...
Original map: Party A wins 3 out of 4 districts

In 1000 alternative fair maps:
   Average Party A districts: 3.51
   Party A wins 3 districts: 471 times (47.1%)

🔍 Gerrymandering Analysis:
✅ Original result occurs in 47.1% of fair maps
   This appears normal
```

**What the results mean:**
- **47.1%** = Original map appears in 47.1% of fair alternatives
- **Verdict:** ✅ FAIR (above 10% threshold)
- No evidence of gerrymandering detected

**When to use it:**
- Learning GerryChain for the first time
- Testing that MCMC algorithm works
- Quick demonstrations (30 seconds)
- Understanding ensemble comparison concept

---

### Level 2: Intermediate Understanding

#### 3. `detect_gerrymandering.py` - Comparing Fair vs Biased Maps

**What it does:**
1. Creates a **8×8 city** with geographic voting patterns (urban core vs suburbs)
2. Creates TWO different district maps using different random seeds:
   - **Seed 42:** "Fair" map
   - **Seed 999:** Potentially "Biased" map
3. Runs MCMC on BOTH maps to see which is more typical
4. Compares p-values to determine which is suspicious

**Why you need it:**
- Shows that **the same city can have different district outcomes**
- Demonstrates how random seed affects fairness
- Teaches the concept of "outlier detection"
- More realistic than `simple_simulation.py` (uses geographic clustering)

**Key innovation:**
Uses **distance-from-center** to create realistic voting patterns:
```python
if distance_from_center < 2:
    dem_pct = 0.70  # Urban core: 70% Democratic
elif distance_from_center < 3:
    dem_pct = 0.45  # Inner suburbs: 45% Democratic
else:
    dem_pct = 0.30  # Outer suburbs: 30% Democratic
```

**How to run:**
```bash
source .venv/bin/activate
python detect_gerrymandering.py
```

**What to expect:**
- Creates city with realistic geographic voting
- Tests fair map (seed 42)
- Tests biased map (seed 999)
- Compares p-values between the two

**When to use it:**
- After understanding `simple_simulation.py`
- Learning about geographic clustering
- Understanding how seed selection matters
- Comparing multiple maps from same city

---

#### 4. `working_gerrymander_demo.py` - Realistic Pack-and-Crack

**What it does:**
1. Creates a **6×6 city** where Democrats have ~52% citywide support
2. Creates a "fair" map using geographic division
3. Creates a "gerrymandered" map using manual assignment
4. Runs MCMC on both to detect which is an outlier

**Why you need it:**
- Demonstrates the **pack-and-crack strategy** explicitly
- Uses more realistic city size (6×6 = 36 blocks)
- Shows intentional gerrymandering technique
- Educational tool for understanding manipulation methods

**Pack-and-Crack Strategy Explained:**
```
Fair Map:
District 1: 52% Dem → Dem wins
District 2: 51% Dem → Dem wins
District 3: 53% Dem → Dem wins
Result: Democrats win 3/3 (matches 52% support)

Gerrymandered Map:
District 1: 85% Dem → Dem wins (PACKED - wasted votes)
District 2: 48% Dem → Rep wins (CRACKED - split Dems)
District 3: 47% Dem → Rep wins (CRACKED - split Dems)
Result: Democrats win 1/3 (despite 52% support!)
```

**How to run:**
```bash
source .venv/bin/activate
python working_gerrymander_demo.py
```

**When to use it:**
- Understanding gerrymandering tactics
- Educational presentations
- Seeing pack-and-crack in action
- More realistic than simple_simulation

---

#### 5. `gerrymandering_detection.py` - Polarized City Analysis

**What it does:**
1. Creates a **10×10 polarized city** (100 blocks)
2. Models Democrats clustering in urban core, Republicans in suburbs
3. Uses population density (denser in center)
4. Creates fair districts using `recursive_tree_part`
5. Runs extensive MCMC to find expected outcomes

**Why you need it:**
- **Larger scale** (100 blocks vs 36-64)
- **Realistic urban geography** (population density varies)
- Shows how real cities have clustered voters
- Longer runtime for more statistical confidence

**Unique features:**
- **Population density varies:** Urban core has 15-20 people/block, rural areas 5-10
- **Voter clustering:** 80% Dem in center, 20% Dem in outer areas
- Uses **5 districts** instead of 4
- Allows 15% population deviation (realistic constraint)

**How to run:**
```bash
source .venv/bin/activate
python gerrymandering_detection.py
```

**When to use it:**
- Analyzing larger cities
- Understanding urban vs suburban voting
- More computationally intensive analysis
- Research projects requiring larger samples

---

### Level 3: Advanced Techniques

#### 6. `clear_gerrymander_example.py` - Multi-Seed Search

**What it does:**
1. Creates a **6×6 balanced city** (Democrats ~45-50%)
2. **Searches through 10-15 different random seeds**
3. For each seed, creates districts using `recursive_tree_part`
4. Calculates "representation gap" for each map
5. Selects the MOST FAIR and MOST BIASED maps
6. Runs MCMC on both to prove statistical difference

**Why you need it:**
- **Automated gerrymander detection** (no manual district drawing)
- Shows that algorithms can produce different fairness levels
- **Representation gap** metric for measuring bias
- Systematic search methodology

**How it works:**
```python
for seed in range(15):
    random.seed(seed)
    assignment = recursive_tree_part(...)  # Create districts

    # Calculate representation gap
    citywide_dem_pct = 45.6%
    district_dem_pct = dem_wins / 4 * 100
    gap = abs(district_dem_pct - citywide_dem_pct)

# Sort by gap
fair_map = smallest_gap      # Example: 2/4 = 50%, gap = 4.4%
biased_map = largest_gap     # Example: 3/4 = 75%, gap = 29.4%
```

**Expected results:**
- Fair map: Occurs in ~50-60% of MCMC samples → ✅ FAIR
- Biased map: Occurs in ~5-10% of MCMC samples → ⚠️ SUSPICIOUS

**How to run:**
```bash
source .venv/bin/activate
python clear_gerrymander_example.py
```

**When to use it:**
- Research projects analyzing multiple maps
- Understanding algorithmic variation
- Comparing representation gaps
- Court evidence preparation (systematic methodology)

---

#### 7. `extreme_gerrymandering.py` - The Most Advanced Example (FIXED!)

**What it does:**
1. Creates a **6×6 city** with **strong geographic clustering** (80% Dem left, 25% Dem right)
2. Creates a **FAIR map** using simple quadrant division
3. **Searches through 50 random seeds** to find the most biased map
4. Tests BOTH maps with **2500 MCMC steps** (highest statistical power)
5. Detects suspicious gerrymandering below 10% threshold

**Why you need it:**
- **Highest detection sensitivity** (2500 MCMC steps)
- **Largest seed search** (50 trials)
- **4 districts** for better granularity
- **Strongest geographic clustering** for realistic scenarios
- **Successfully detects suspicious maps** (8.6% p-value)

**What makes it "extreme":**
1. **Enhanced Voting Pattern:**
   ```python
   if x <= 1:
       dem_votes = 80%  # LEFT: Strong Democratic
   elif x >= 4:
       dem_votes = 25%  # RIGHT: Strong Republican
   else:
       dem_votes = 55%  # CENTER: Swing
   ```

2. **Algorithmic Gerrymander Search:**
   ```python
   for seed in range(50):
       create_map(seed)
       calculate_democratic_wins()

   # Select map with FEWEST Democratic wins
   gerrymander_map = min(maps, key=lambda x: x.dem_wins)
   ```

3. **High-Power MCMC:**
   - 2500 steps per map
   - 5000 total samples generated
   - ~4 minute runtime

**Fixed Issues:**
- ❌ Original: Manual assignment broke contiguity
- ✅ Fixed: Uses `recursive_tree_part` with 50-seed search
- ❌ Original: 3 districts insufficient
- ✅ Fixed: 4 districts for better detection
- ❌ Original: Weak bias (28-32% p-value)
- ✅ Fixed: Strong bias (8.6% p-value = SUSPICIOUS!)

**How to run:**
```bash
source .venv/bin/activate
python extreme_gerrymandering.py
```

**Expected output:**
```
🏆 FINAL RESULTS
==================================================
Fair map verdict:        FAIR (57.3%)
Gerrymandered map verdict: SUSPICIOUS (8.6%)
```

**When to use it:**
- **Court-ready evidence** (high statistical power)
- **Detecting subtle gerrymandering** (below 10%)
- **Research requiring confidence** (2500 samples)
- **Demonstrating advanced techniques** (algorithmic search)

---

## Why Do We Need So Many Files?

### The Pedagogical Ladder

Think of these files like a **textbook with progressive chapters:**

1. **Chapter 1** (`test_installation.py`): "Can you even run the software?"
2. **Chapter 2** (`simple_simulation.py`): "Here's the basic concept"
3. **Chapter 3** (`detect_gerrymandering.py`): "Same city, different outcomes"
4. **Chapter 4** (`working_gerrymander_demo.py`): "Pack-and-crack explained"
5. **Chapter 5** (`gerrymandering_detection.py`): "Realistic urban geography"
6. **Chapter 6** (`clear_gerrymander_example.py`): "Systematic search"
7. **Chapter 7** (`extreme_gerrymandering.py`): "Court-ready analysis"

### Each File Teaches a Different Concept

| Concept | File That Teaches It |
|---------|---------------------|
| MCMC basics | `simple_simulation.py` |
| Geographic clustering | `detect_gerrymandering.py`, `gerrymandering_detection.py` |
| Pack-and-crack strategy | `working_gerrymander_demo.py` |
| Representation gap | `clear_gerrymander_example.py` |
| Algorithmic search | `clear_gerrymander_example.py`, `extreme_gerrymandering.py` |
| Contiguity constraints | `extreme_gerrymandering.py` (learned the hard way!) |
| Statistical thresholds | All files |
| High-power analysis | `extreme_gerrymandering.py` |

### Different Use Cases

**Teaching a Class:**
- Start with `simple_simulation.py` (30 seconds)
- Show `working_gerrymander_demo.py` (pack-and-crack visual)
- Demonstrate `clear_gerrymander_example.py` (systematic search)

**Research Project:**
- Use `extreme_gerrymandering.py` (2500 MCMC steps)
- Modify for your specific data
- Higher statistical confidence

**Quick Demo:**
- `simple_simulation.py` (fastest)
- `test_installation.py` (even faster, just verification)

**Court Evidence:**
- `extreme_gerrymandering.py` (highest power)
- `clear_gerrymander_example.py` (systematic methodology)
- 10,000+ MCMC steps for legal standards

---

## Comparison Matrix

### City Characteristics

| File | Grid Size | Blocks | Districts | Voting Pattern |
|------|-----------|--------|-----------|----------------|
| `simple_simulation.py` | 8×8 | 64 | 4 | Random |
| `detect_gerrymandering.py` | 8×8 | 64 | 4 | Distance-based |
| `working_gerrymander_demo.py` | 6×6 | 36 | 3-4 | Geographic (left/right) |
| `gerrymandering_detection.py` | 10×10 | 100 | 5 | Urban density + distance |
| `clear_gerrymander_example.py` | 6×6 | 36 | 4 | Geographic clustering |
| `extreme_gerrymandering.py` | 6×6 | 36 | 4 | Strong left/right clustering |

### Analysis Parameters

| File | MCMC Steps | Seed Search | Runtime | Detection Success |
|------|------------|-------------|---------|-------------------|
| `simple_simulation.py` | 1000 | No | 30 sec | N/A (neutral) |
| `detect_gerrymandering.py` | ~1500 | 2 seeds | 2 min | Moderate |
| `working_gerrymander_demo.py` | ~1200 | No | 3 min | Good |
| `gerrymandering_detection.py` | ~2000 | No | 4 min | Good |
| `clear_gerrymander_example.py` | 1200×2 | 10-15 seeds | 3 min | Excellent (7.8%) |
| `extreme_gerrymandering.py` | 2500×2 | 50 seeds | 4 min | **Best (8.6%)** |

---

## Recommended Learning Order

### For Complete Beginners (Week 1)

**Day 1:**
1. Read the technical documentation you provided
2. Run `test_installation.py` to verify setup
3. Run `simple_simulation.py` and understand every line

**Day 2-3:**
4. Read about geographic clustering in voting
5. Run `detect_gerrymandering.py`
6. Modify voting patterns and see how results change

**Day 4-5:**
7. Learn about pack-and-crack strategy
8. Run `working_gerrymander_demo.py`
9. Try creating your own manual gerrymander

### For Intermediate Users (Week 2)

**Day 1:**
1. Run `gerrymandering_detection.py` (larger scale)
2. Understand urban vs suburban voting patterns
3. Experiment with different city sizes

**Day 2-3:**
4. Study `clear_gerrymander_example.py` code
5. Understand systematic seed search
6. Learn representation gap metric

**Day 4-5:**
7. Read the SESSION_CHANGES_README.md
8. Understand why `extreme_gerrymandering.py` failed
9. Study the fix (recursive_tree_part with seed search)

### For Advanced Users (Week 3)

**Day 1-2:**
1. Run `extreme_gerrymandering.py` with different parameters
2. Increase MCMC steps to 5000
3. Try different grid sizes (8×8, 10×10)

**Day 3-4:**
4. Modify voting patterns to make detection harder/easier
5. Experiment with different constraints
6. Try different numbers of districts

**Day 5:**
7. Prepare for real-world data (shapefiles, actual elections)
8. Study the legal cases (Pennsylvania, North Carolina)
9. Design your own analysis for a real state

---

## Common Questions

### Q: Why so many similar files?

**A:** Each teaches a slightly different concept:
- **Different voting patterns** (random vs geographic vs polarized)
- **Different methodologies** (manual vs algorithmic)
- **Different complexity levels** (beginner to advanced)
- **Different use cases** (teaching vs research vs legal)

### Q: Which file should I actually use?

**A:** Depends on your goal:

| Goal | Use This File |
|------|--------------|
| Learning GerryChain | `simple_simulation.py` |
| Teaching a class | `working_gerrymander_demo.py` |
| Research project | `extreme_gerrymandering.py` |
| Quick demonstration | `simple_simulation.py` |
| Court evidence | `extreme_gerrymandering.py` (modified for 10k steps) |
| Understanding geography | `detect_gerrymandering.py` |

### Q: Can I delete the files I don't need?

**A:** Yes, but keep:
- `test_installation.py` (for debugging)
- `simple_simulation.py` (fastest demo)
- `extreme_gerrymandering.py` (most powerful)

### Q: Which file is the "best"?

**A:** `extreme_gerrymandering.py` is most sophisticated because:
- ✅ Highest statistical power (2500 MCMC steps)
- ✅ Largest search space (50 seeds)
- ✅ Successfully detects suspicious maps (8.6%)
- ✅ Uses best practices (algorithmic + contiguity-preserving)
- ✅ Court-ready methodology

But "best" depends on context:
- **Fastest:** `simple_simulation.py`
- **Most educational:** `working_gerrymander_demo.py`
- **Most realistic geography:** `gerrymandering_detection.py`
- **Best methodology:** `clear_gerrymander_example.py`
- **Highest power:** `extreme_gerrymandering.py`

---

## Evolution of the Files (Historical Perspective)

### Generation 1: Simple Examples
- `test_installation.py` - Basic verification
- `simple_simulation.py` - First working example

### Generation 2: Realistic Scenarios
- `detect_gerrymandering.py` - Geographic clustering
- `working_gerrymander_demo.py` - Pack-and-crack demonstration
- `gerrymandering_detection.py` - Polarized cities

### Generation 3: Advanced Techniques
- `clear_gerrymander_example.py` - Systematic search introduced
- `extreme_gerrymandering.py` - Highest-power analysis

### Our Session: The Fix
- Found `extreme_gerrymandering.py` broken (contiguity error)
- Applied lessons from `clear_gerrymander_example.py` (algorithmic search)
- Created most powerful example (8.6% detection)

---

## Summary: The Essential Files

If you only run **THREE files**, make them:

### 1. `simple_simulation.py` (30 seconds)
**Why:** Fastest way to see MCMC in action
**Learn:** Basic algorithm, ensemble comparison, p-values

### 2. `clear_gerrymander_example.py` (3 minutes)
**Why:** Shows systematic methodology
**Learn:** Seed search, representation gap, fair vs biased

### 3. `extreme_gerrymandering.py` (4 minutes)
**Why:** Most sophisticated, successfully detects gerrymandering
**Learn:** High-power analysis, algorithmic search, contiguity preservation

---

## Final Recommendation

**Start here:**
```bash
source .venv/bin/activate
python simple_simulation.py    # 30 seconds - understand basics
python extreme_gerrymandering.py  # 4 minutes - see full power
```

**Then explore others based on interest:**
- Curious about geography? → `detect_gerrymandering.py`
- Want to learn tactics? → `working_gerrymander_demo.py`
- Need larger scale? → `gerrymandering_detection.py`
- Building research? → `clear_gerrymander_example.py`

**All files serve a purpose** - they form a complete educational curriculum from beginner to expert level.

---

**Last Updated:** October 4, 2025
**Files Documented:** 7 example scripts
**Recommended Starting Point:** `simple_simulation.py` → `extreme_gerrymandering.py`
