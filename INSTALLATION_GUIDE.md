# GerryChain Example Scripts - Installation Guide

Complete step-by-step instructions to set up and run the gerrymandering detection examples.

---

## Quick Start (3 Commands)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt && pip install -e .
```

Then run:
```bash
python test_installation.py    # Verify setup
python simple_simulation.py    # First example (30 sec)
```

---

## Detailed Installation

### Prerequisites

**Required:**
- Python 3.9+ (tested on 3.9, 3.10, 3.11, 3.12, 3.13)
- pip (Python package manager)
- git

**Check your Python version:**
```bash
python3 --version
```

---

### Step 1: Clone the Repository

```bash
git clone https://github.com/Vkartik-3/Gerrychain_FRA.git
cd Gerrychain_FRA
```

---

### Step 2: Create Virtual Environment

**Why?** Isolates dependencies from system Python, prevents version conflicts.

**macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows:**
```cmd
python -m venv .venv
.venv\Scripts\activate
```

**Verify activation:** Your prompt should show `(.venv)`

---

### Step 3: Install Dependencies

**Upgrade pip first:**
```bash
pip install --upgrade pip
```

**Install required packages:**
```bash
pip install -r requirements.txt
```

**Install GerryChain in development mode:**
```bash
pip install -e .
```

**What gets installed:**
- **pandas** (2.0+) - Data analysis
- **scipy** (1.10+) - Scientific computing
- **networkx** (3.0+) - Graph algorithms
- **matplotlib** (3.7+) - Plotting
- **geopandas** (0.12.2+) - Geographic data
- **shapely** (2.0.1+) - Geometric operations
- **pyproj** (3.5.0+) - Coordinate transformations
- **pyogrio** (0.7.2+) - Fast GeoJSON/shapefile I/O
- **numpy** (1.24+) - Numerical operations

---

### Step 4: Configure Reproducibility (Important!)

**Why?** Python's hash randomization affects spanning tree generation. Without this, results vary between runs.

**macOS/Linux:**
```bash
echo 'export PYTHONHASHSEED=0' >> .venv/bin/activate
source .venv/bin/activate  # Reload to apply
```

**Windows:**
Add to `.venv\Scripts\activate.bat`:
```cmd
set PYTHONHASHSEED=0
```

**Verify:**
```bash
echo $PYTHONHASHSEED  # Should print: 0
```

---

### Step 5: Verify Installation

```bash
python test_installation.py
```

**Expected output:**
```
🚀 Testing GerryChain Installation
==================================================
🌍 Testing environment...
   PYTHONHASHSEED: 0
✅ Reproducible environment properly configured

🔍 Testing basic imports...
✅ GerryChain version: X.X.X
✅ Successfully imported core components

🔍 Testing graph creation...
✅ Created graph with 16 nodes and 24 edges

🔍 Testing partition creation...
✅ Created partition with 4 districts
   District sizes: [4, 4, 4, 4]

🎉 All tests passed!
✅ GerryChain is properly installed and ready to use
✅ Environment is configured for reproducible results
```

---

## Running Example Scripts

### Quick Test (30 seconds)
```bash
python simple_simulation.py
```

### Full Power Demonstration (4 minutes)
```bash
python extreme_gerrymandering.py
```

### All Examples
```bash
python test_installation.py              # 5 sec - Verify setup
python simple_simulation.py              # 30 sec - Basic MCMC
python detect_gerrymandering.py          # 2 min - Geographic clustering
python working_gerrymander_demo.py       # 3 min - Pack-and-crack
python gerrymandering_detection.py       # 4 min - Large-scale analysis
python clear_gerrymander_example.py      # 3 min - Seed search
python extreme_gerrymandering.py         # 4 min - Highest power (FIXED!)
```

---

## Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'geopandas'`

**Solution:**
```bash
source .venv/bin/activate  # Make sure venv is activated
pip install geopandas shapely pyproj pyogrio
```

---

### Issue: `ValueError: initial_state is not valid - single_flip_contiguous`

**Cause:** Districts are not geographically connected.

**Solution:** This was fixed in `extreme_gerrymandering.py`. Make sure you're using the latest version from the repository.

---

### Issue: Results vary between runs

**Cause:** `PYTHONHASHSEED` not set.

**Solution:**
```bash
export PYTHONHASHSEED=0  # Add to .venv/bin/activate
source .venv/bin/activate
```

---

### Issue: Scripts take too long

**Solution:** Reduce MCMC steps for faster testing:
```python
# In the script, find this line:
test_with_mcmc(partition, "MAP_TYPE", num_steps=2500)

# Change to:
test_with_mcmc(partition, "MAP_TYPE", num_steps=500)
```

---

### Issue: Import errors on macOS

**Apple Silicon users:** Make sure you're using native ARM64 Python, not Rosetta x86_64.

**Check:**
```bash
python3 -c "import platform; print(platform.machine())"
```

**Should output:** `arm64` (not `x86_64`)

---

### Issue: Installation fails on Windows

**Common issues:**
1. Missing C++ compiler for spatial libraries
2. Long path issues

**Solutions:**
1. Install Visual Studio Build Tools
2. Run PowerShell as Administrator
3. Enable long paths: `git config --system core.longpaths true`

---

## Platform-Specific Notes

### macOS (Apple Silicon / M1/M2/M3)
✅ All dependencies work natively
✅ Fast performance
✅ Tested on macOS Sequoia (Darwin 25.0.0)

### macOS (Intel)
✅ Should work without issues
⚠️ Slightly slower than Apple Silicon

### Linux (Ubuntu/Debian)
✅ Works well
**May need:**
```bash
sudo apt-get install libgeos-dev libproj-dev
```

### Linux (RHEL/CentOS/Fedora)
✅ Works well
**May need:**
```bash
sudo yum install geos-devel proj-devel
```

### Windows 10/11
⚠️ More setup required
**Install:**
1. Visual Studio Build Tools
2. OSGeo4W (for GDAL/PROJ)

---

## Updating Dependencies

```bash
source .venv/bin/activate
pip install --upgrade -r requirements.txt
pip install --upgrade -e .
```

---

## Uninstalling

```bash
deactivate                    # Exit virtual environment
rm -rf .venv                  # Remove virtual environment
# Repository remains intact
```

---

## Environment Details

**Tested Configuration:**
- **OS:** macOS (Darwin 25.0.0)
- **Python:** 3.13.2 (also works on 3.9-3.12)
- **Architecture:** ARM64 (Apple Silicon)
- **Virtual Environment:** Python venv
- **Installation Method:** Development mode (`pip install -e .`)

---

## Additional Resources

### Documentation
- **FILE_EXPLANATIONS.md** - Detailed guide to all 7 example scripts
- **SESSION_CHANGES_README.md** - Technical documentation of bug fixes

### Example Scripts
1. **test_installation.py** - Installation verification
2. **simple_simulation.py** - Basic MCMC (best for learning)
3. **extreme_gerrymandering.py** - Advanced analysis (best results)

### Official GerryChain Docs
- GitHub: https://github.com/mggg/GerryChain
- Docs: https://gerrychain.readthedocs.io/
- MGGG: https://mggg.org/

---

## Quick Reference

| Task | Command |
|------|---------|
| Activate environment | `source .venv/bin/activate` |
| Deactivate environment | `deactivate` |
| Install dependencies | `pip install -r requirements.txt` |
| Verify installation | `python test_installation.py` |
| Run quick demo | `python simple_simulation.py` |
| Run full analysis | `python extreme_gerrymandering.py` |
| Update packages | `pip install --upgrade -r requirements.txt` |

---

## Getting Help

**Installation issues?**
1. Check this guide's troubleshooting section
2. Run `python test_installation.py` for diagnostics
3. Verify Python version: `python3 --version`
4. Check virtual environment: `which python` (should show `.venv` path)

**Script issues?**
1. Read `FILE_EXPLANATIONS.md` for script-specific details
2. Check `SESSION_CHANGES_README.md` for known fixes
3. Verify `PYTHONHASHSEED=0` is set

**Still stuck?**
- Open an issue on GitHub: https://github.com/Vkartik-3/Gerrychain_FRA/issues
- Check official GerryChain documentation

---

**Last Updated:** October 4, 2025
**Version:** 1.0
**Status:** All scripts tested and working ✅
