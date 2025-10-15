# GerryChain Example Scripts

This directory contains example scripts demonstrating various GerryChain features for gerrymandering detection and redistricting analysis.

Scripts are organized into two categories:
- **`synthetic_data/`** - Scripts using randomly generated data for learning and demos
- **`real_data/`** - Scripts using actual MGGG Alaska election data

---

## Directory Structure

```
scripts/
├── README.md                    (this file)
├── synthetic_data/              🎲 Synthetic data examples
│   ├── README.md
│   ├── simple_simulation.py
│   ├── detect_gerrymandering.py
│   ├── gerrymandering_detection.py
│   ├── clear_gerrymander_example.py
│   ├── extreme_gerrymandering.py
│   └── working_gerrymander_demo.py
└── real_data/                   📊 Real MGGG data examples
    ├── README.md
    ├── real_data_simple.py
    └── real_data_simulation.py
```

---

## Running Scripts

All scripts should be run from the **project root directory**:

```bash
# From /Users/kartikvadhawana/Desktop/FRA/GerryChain/

# Synthetic data examples
python scripts/synthetic_data/simple_simulation.py
python scripts/synthetic_data/detect_gerrymandering.py

# Real data examples
python scripts/real_data/real_data_simple.py
```

Make sure GerryChain is installed:
```bash
pip install -e .
```

---

## Quick Start

**New to GerryChain?** Start here:

### 1. Basic Synthetic Data Demo
Start with a simple simulation to understand the concepts:
```bash
python scripts/synthetic_data/simple_simulation.py
```
**Run time:** ~10 seconds

### 2. Real Data Analysis ⭐
See it work with actual election data:
```bash
python scripts/real_data/real_data_simple.py
```
**Run time:** ~5 seconds

### 3. Gerrymandering Detection
Explore how to detect manipulation:
```bash
python scripts/synthetic_data/detect_gerrymandering.py
```

---

## Synthetic Data Scripts (`synthetic_data/`)

These scripts use randomly generated data to demonstrate GerryChain concepts without requiring external files.

### **simple_simulation.py**
Basic introduction to GerryChain with synthetic data.

**What it does:**
- Creates 8×8 grid city (64 neighborhoods)
- Generates random population and voting data
- Divides into 4 districts
- Runs 1000 MCMC steps to generate alternative fair maps
- Analyzes results to detect potential gerrymandering

**Best for:** First-time users learning GerryChain basics

```bash
python scripts/synthetic_data/simple_simulation.py
```

### **detect_gerrymandering.py**
Demonstrates gerrymandering detection with realistic geographic voting patterns.

**What it does:**
- Creates city with geographic voting patterns (urban vs suburban)
- Shows how to identify gerrymandered maps using MCMC ensembles
- Analyzes statistical outliers

```bash
python scripts/synthetic_data/detect_gerrymandering.py
```

### **gerrymandering_detection.py**
Alternative implementation of gerrymandering detection.

```bash
python scripts/synthetic_data/gerrymandering_detection.py
```

### **clear_gerrymander_example.py**
Creates an obviously gerrymandered map to demonstrate detection.

**What it does:**
- Intentionally creates unfair districts
- Shows how MCMC ensembles detect manipulation
- Demonstrates statistical analysis

**Best for:** Understanding how gerrymandering appears in data

```bash
python scripts/synthetic_data/clear_gerrymander_example.py
```

### **extreme_gerrymandering.py**
Demonstrates extreme gerrymandering scenarios.

**What it does:**
- Creates severely biased district maps
- Shows statistical signatures of extreme gerrymandering
- Compares to neutral alternatives

```bash
python scripts/synthetic_data/extreme_gerrymandering.py
```

### **working_gerrymander_demo.py**
Working demonstration of gerrymandering concepts.

```bash
python scripts/synthetic_data/working_gerrymander_demo.py
```

---

## Real Data Scripts (`real_data/`)

These scripts use actual election data from the MGGG States project.

**Data source:** Alaska precincts shapefile
- 437 precincts
- 2016 Presidential election results (Trump vs Clinton)
- Real demographic data
- 40 Alaska State House districts

**Data location:** `data/data/AK-shapefiles/alaska_precincts.shp`

### **real_data_simple.py** ⭐ RECOMMENDED
Analyzes actual election data from MGGG States project.

**What it does:**
- Loads Alaska precinct shapefile with real 2016 election results
- Uses existing 40 Alaska State House districts
- Analyzes vote share vs seat share
- Detects potential gerrymandering indicators

**Key findings:**
- Statewide: 40% Democrat, 60% Republican
- District outcomes: Democrats won only 25% of districts
- **15% gap** suggests potential gerrymandering or geographic clustering

**Best for:** Working with real-world redistricting data

```bash
python scripts/real_data/real_data_simple.py
```

### **real_data_simulation.py** (Advanced) ⚠️
Attempts to run MCMC on real data (may have contiguity issues).

**Status:** Experimental - may encounter errors due to non-contiguous districts

**What it tries to do:**
- Load real MGGG data
- Create new contiguous districts using recursive tree partitioning
- Run MCMC ensemble

**Note:** Use `real_data_simple.py` for stable real data analysis.

```bash
python scripts/real_data/real_data_simulation.py
```

---

## Understanding the Output

### Common Output Sections:

**📊 District Information**
- Shows population and vote counts per district
- Identifies which party wins each district

**📈 Distribution of Results**
- Shows how often each outcome occurs in fair alternatives
- Helps identify if original map is an outlier

**🔍 Gerrymandering Analysis**
- Compares original map to ensemble of fair alternatives
- Flags suspicious outliers (< 5% or > 95% percentile)
- Statistical evidence of potential manipulation

---

## Troubleshooting

### Import Errors
```
ModuleNotFoundError: No module named 'gerrychain'
```
**Solution:** Install GerryChain from project root:
```bash
pip install -e .
```

### File Not Found (Real Data Scripts)
```
FileNotFoundError: Shapefile not found
```
**Solution:** Run from project root, not from subdirectories:
```bash
# ✅ Correct
python scripts/real_data/real_data_simple.py

# ❌ Wrong
cd scripts/real_data && python real_data_simple.py
```

### Contiguity Errors
```
ValueError: failed constraints were: single_flip_contiguous
```
**Solution:** This is a known issue with some real-world district data. Use `real_data_simple.py` instead of `real_data_simulation.py`.

---

## Learn More

- **GerryChain Documentation:** https://gerrychain.readthedocs.io
- **MGGG States Project:** https://github.com/mggg-states
- **Metric Geometry and Gerrymandering Group:** https://mggg.org

---

## Contributing

To add a new example script:
1. Create your script in the appropriate subdirectory (`synthetic_data/` or `real_data/`)
2. Add description to this README and the subdirectory README
3. Test from project root
4. Update path handling if using external data files
