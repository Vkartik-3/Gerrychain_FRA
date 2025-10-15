# Synthetic Data Examples

This directory contains GerryChain example scripts that use **randomly generated data**. These scripts are perfect for learning and demos since they don't require any external data files.

---

## Scripts in this Directory

### 1. **simple_simulation.py** 🌟 START HERE
Basic introduction to GerryChain.

**What it does:**
- Creates an 8×8 grid city (64 neighborhoods)
- Generates random population and voting data
- Divides into 4 districts
- Runs 1000 MCMC steps to generate alternative fair maps
- Analyzes results to detect potential gerrymandering

**Run time:** ~10 seconds

**Best for:** First-time GerryChain users

```bash
# From project root
python scripts/synthetic_data/simple_simulation.py
```

**Example output:**
```
🚀 GerryChain Gerrymandering Detection Simulation
🏙️  Creating 8x8 city grid...
✅ Created city with 64 blocks and 638 people
🗺️  Dividing city into 4 districts...
✅ Initial districts created
🎲 Running MCMC simulation for 1000 steps...
✅ Simulation complete!
📊 Analyzing Results...
```

---

### 2. **detect_gerrymandering.py**
Gerrymandering detection with realistic geographic voting patterns.

**What it does:**
- Creates a city with geographic voting patterns (urban core vs suburbs)
- Urban core: leans Democratic (~70%)
- Suburbs: lean Republican (~30%)
- Shows how to identify gerrymandered maps using MCMC ensembles
- Analyzes statistical outliers

**Best for:** Understanding how geography affects redistricting

```bash
python scripts/synthetic_data/detect_gerrymandering.py
```

---

### 3. **gerrymandering_detection.py**
Alternative implementation of gerrymandering detection.

**What it does:**
- Similar to `detect_gerrymandering.py`
- Different code structure/approach
- Good for comparing implementation styles

```bash
python scripts/synthetic_data/gerrymandering_detection.py
```

---

### 4. **clear_gerrymander_example.py**
Demonstrates an obviously gerrymandered map.

**What it does:**
- Intentionally creates unfair, biased districts
- Shows how MCMC ensembles detect manipulation
- Demonstrates statistical analysis of outliers
- Clear example of what gerrymandering looks like in data

**Best for:** Understanding how gerrymandering appears statistically

```bash
python scripts/synthetic_data/clear_gerrymander_example.py
```

---

### 5. **extreme_gerrymandering.py**
Extreme gerrymandering scenarios.

**What it does:**
- Creates severely biased district maps
- Shows statistical signatures of extreme gerrymandering
- Compares to neutral alternatives
- Demonstrates "packing" and "cracking" techniques

**Best for:** Seeing worst-case gerrymandering scenarios

```bash
python scripts/synthetic_data/extreme_gerrymandering.py
```

---

### 6. **working_gerrymander_demo.py**
General demonstration of gerrymandering concepts.

```bash
python scripts/synthetic_data/working_gerrymander_demo.py
```

---

## Why Use Synthetic Data?

**Advantages:**
- ✅ No external files needed
- ✅ Fast to run
- ✅ Easy to understand
- ✅ Reproducible (can set random seed)
- ✅ Great for learning concepts
- ✅ Can create "perfect" scenarios for testing

**Disadvantages:**
- ❌ Not real-world data
- ❌ Simplified geography (grids)
- ❌ May not capture all complexities
- ❌ Results are illustrative, not actual

---

## How to Run

All scripts should be run from the **project root directory**:

```bash
# From /Users/kartikvadhawana/Desktop/FRA/GerryChain/
python scripts/synthetic_data/<script_name>.py
```

**Make sure GerryChain is installed:**
```bash
pip install -e .
```

---

## Learning Path

**Recommended order for learning:**

1. **Start:** `simple_simulation.py`
   - Learn basic GerryChain workflow
   - Understand MCMC ensembles
   - See how analysis works

2. **Next:** `detect_gerrymandering.py`
   - Add realistic geographic patterns
   - Understand urban vs suburban voting
   - See how patterns affect redistricting

3. **Then:** `clear_gerrymander_example.py`
   - See obvious gerrymandering
   - Learn statistical detection methods
   - Understand outlier analysis

4. **Advanced:** `extreme_gerrymandering.py`
   - Explore worst-case scenarios
   - Understand "packing" and "cracking"
   - See extreme statistical signatures

---

## Understanding the Output

### Key Metrics to Watch:

**🏙️ City Creation**
```
✅ Created city with 64 blocks and 638 people
```
- Shows grid size and total population

**🗺️ Initial Districts**
```
District 0: 149 people, 73 vs 76 votes → Party B wins
District 1: 160 people, 87 vs 73 votes → Party A wins
```
- Shows the starting district configuration
- Vote counts for each party

**🎲 MCMC Simulation**
```
✅ Generated 1000 alternative district maps
```
- Creates ensemble of "fair" alternatives

**📊 Results Analysis**
```
Average Party A districts: 3.51
Most common result: 4 districts
Range: 2 - 4 districts
```
- Shows what's typical in fair maps

**🔍 Gerrymandering Detection**
```
✅ Original result occurs in 47.1% of fair maps
   This appears normal

⚠️ SUSPICIOUS: Original result occurs in only 2.3% of fair maps!
   This could indicate gerrymandering
```
- Flags outliers (< 5% or > 95%)
- Indicates potential manipulation

---

## Customization

You can modify these scripts to:
- Change grid size
- Adjust voting patterns
- Modify number of districts
- Increase/decrease MCMC steps
- Experiment with different scenarios

**Example modification:**
```python
# In simple_simulation.py
graph = create_city_graph(size=10)  # Change from 8 to 10
partition = create_initial_districts(graph, num_districts=5)  # Change from 4 to 5
partitions = run_simulation(partition, num_steps=5000)  # More steps
```

---

## Next Steps

After mastering synthetic data examples, explore **real data analysis**:

```bash
python scripts/real_data/real_data_simple.py
```

This uses actual MGGG Alaska election data to analyze real-world redistricting.

---

## Questions?

- **GerryChain Docs:** https://gerrychain.readthedocs.io
- **MGGG:** https://mggg.org
- **Main README:** `../README.md`
