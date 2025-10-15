# Real MGGG Data Examples

This directory contains GerryChain scripts that use **actual election data** from the MGGG States project. These demonstrate working with real-world shapefiles and analyzing actual redistricting scenarios.

---

## Data Source

**MGGG States - Alaska Precincts**
- **Source:** https://github.com/mggg-states/AK-shapefiles
- **Location:** `data/data/AK-shapefiles/alaska_precincts.shp`
- **Precincts:** 437 (4 isolated precincts are automatically removed)
- **Election:** 2016 Presidential (Clinton vs Trump)
- **Districts:** 40 Alaska State House districts
- **Demographics:** Population, race, voting-age population

**What's included:**
- Real precinct boundaries (shapefile)
- Actual 2016 election results by precinct
- Population and demographic data
- Existing district assignments

---

## Scripts in this Directory

### 1. **real_data_simple.py** ⭐ RECOMMENDED
Analyzes actual Alaska election data.

**What it does:**
- Loads Alaska precinct shapefile with real 2016 election results
- Uses existing 40 Alaska State House districts
- Analyzes vote share vs seat share
- Detects potential gerrymandering indicators

**Key findings from Alaska data:**
- **Statewide vote:** 40.0% Democrat, 60.0% Republican
- **District outcomes:** Democrats won only 10/40 districts (25%)
- **Gap:** 15% difference between vote share (40%) and seat share (25%)
- **Analysis:** Suggests potential gerrymandering or geographic clustering

**Run time:** ~5 seconds

**Best for:**
- Understanding real-world redistricting
- Analyzing actual election outcomes
- Working with MGGG shapefiles
- Learning to load and process real data

```bash
# From project root
python scripts/real_data/real_data_simple.py
```

**Example output:**
```
🚀 GerryChain Real Data Analysis (MGGG Alaska)
📂 Loading real data from MGGG States project...
✅ Loaded graph with 441 precincts
   ⚠️  Removing 4 isolated precincts...
   ✅ Graph now has 437 connected precincts

📊 Analyzing Real Election Data (2016 Presidential)...

Statewide vote:
   Democrat: 68,949 (40.0%)
   Republican: 103,422 (60.0%)

District outcomes:
   Democrat wins: 10/40 (25.0%)
   Republican wins: 30/40 (75.0%)

🔍 Analysis:
   ⚠️  Seat share (25.0% DEM) differs significantly
      from vote share (40.0% DEM)
   This could indicate gerrymandering or geographic clustering
```

---

### 2. **real_data_simulation.py** (Advanced) ⚠️
Attempts to run MCMC on real data.

**Status:** EXPERIMENTAL - May encounter errors

**What it tries to do:**
- Load real MGGG Alaska data
- Create new contiguous districts using recursive tree partitioning
- Run MCMC ensemble to generate alternative fair maps

**Known issues:**
- Real-world geography creates contiguity challenges
- Recursive tree partitioning may create non-contiguous districts
- Alaska's geography (islands, disconnected regions) is complex

**Note:** Use `real_data_simple.py` for stable, reliable real data analysis.

```bash
python scripts/real_data/real_data_simulation.py
```

---

## Why Use Real Data?

**Advantages:**
- ✅ Actual election results
- ✅ Real geographic constraints
- ✅ Demonstrates practical applications
- ✅ Can analyze historical redistricting
- ✅ Validates methods on real scenarios
- ✅ More convincing results

**Disadvantages:**
- ❌ Requires external data files
- ❌ More complex to work with
- ❌ Slower to process
- ❌ Geography can cause contiguity issues
- ❌ Data prep is more involved

---

## Working with MGGG Data

### File Structure
```
data/data/AK-shapefiles/
├── alaska_precincts.shp    (main shapefile)
├── alaska_precincts.shx    (shape index)
├── alaska_precincts.dbf    (attribute data)
├── alaska_precincts.prj    (projection info)
└── alaska_precincts.cpg    (encoding)
```

### Loading Data
```python
from gerrychain import Graph

# Load shapefile
graph = Graph.from_file("data/data/AK-shapefiles/alaska_precincts.shp")

# Access node attributes
for node in graph.nodes():
    pop = graph.nodes[node]["TOTPOP"]
    dem_votes = graph.nodes[node]["PRES16D"]
    rep_votes = graph.nodes[node]["PRES16R"]
```

### Available Data Columns
- **Population:** `TOTPOP`, `VAP` (voting age population)
- **2016 Presidential:** `PRES16D`, `PRES16R`, `PRES16L`, `PRES16G`
- **2016 Senate:** `SEN16D`, `SEN16R`, `SEN16L`
- **2018 Governor:** `GOV18D`, `GOV18R`, `GOV18L`
- **2014/2016/2018 US House:** `USH14D`, `USH14R`, etc.
- **Demographics:** `WHITE`, `BLACK`, `AMIN`, `ASIAN`, `NHPI`
- **Districts:** `HDIST` (State House), `DISTRICT`

---

## How to Run

All scripts should be run from the **project root directory**:

```bash
# From /Users/kartikvadhawana/Desktop/FRA/GerryChain/
python scripts/real_data/<script_name>.py
```

**Make sure GerryChain is installed:**
```bash
pip install -e .
```

---

## Understanding Real Data Output

### District Information
```
District 1: 17,726 people | 1,392 vs 1,965 → REP
District 2: 17,738 people | 760 vs 1,837 → REP
```
- Real population counts
- Actual vote totals
- Actual winners

### Statewide Analysis
```
Statewide vote:
   Democrat: 68,949 (40.0%)
   Republican: 103,422 (60.0%)
```
- Total votes cast statewide
- Overall vote percentages

### Seat Share Analysis
```
District outcomes:
   Democrat wins: 10/40 (25.0%)
   Republican wins: 30/40 (75.0%)
```
- Actual district winners
- Percentage of seats won

### Gerrymandering Indicators
```
🔍 Analysis:
   ⚠️  Seat share (25.0% DEM) differs significantly
      from vote share (40.0% DEM)
```
- Compares votes to seats
- Large gaps may indicate gerrymandering or clustering

---

## Alaska-Specific Insights

### Geography Challenges
- **Islands:** Many isolated precincts
- **Disconnected regions:** Creates contiguity issues
- **Low density:** Large geographic areas with small populations
- **Native villages:** Unique demographic patterns

### Political Patterns
- **Urban concentration:** Anchorage and Juneau lean Democratic
- **Rural areas:** Strongly Republican
- **Geographic clustering:** Democrats concentrated in few areas
- **Efficiency gap:** Democratic votes less efficiently distributed

### Why the 15% Gap?
The 15% difference between vote share (40% DEM) and seat share (25% DEM) could be due to:

1. **Geographic clustering** (most likely)
   - Democratic voters concentrated in Anchorage
   - Republican voters spread across rural districts
   - Natural geography, not necessarily manipulation

2. **Intentional gerrymandering**
   - Districts drawn to pack Democrats
   - Would need MCMC ensemble to confirm

3. **Combination of both**
   - Some natural clustering
   - Enhanced by district boundaries

---

## Getting More MGGG Data

Want to analyze other states?

**MGGG States repositories:**
- Pennsylvania: https://github.com/mggg-states/PA-shapefiles
- Wisconsin: https://github.com/mggg-states/WI-shapefiles
- North Carolina: https://github.com/mggg-states/NC-shapefiles
- Many more: https://github.com/mggg-states

**To add a new state:**
```bash
# Example: Pennsylvania
cd data/data
git clone https://github.com/mggg-states/PA-shapefiles.git
cd PA-shapefiles
unzip PA_VTD.zip

# Update script path
shapefile_path = "data/data/PA-shapefiles/PA_VTD.shp"
```

---

## Comparing to Synthetic Data

| Feature | Synthetic Data | Real MGGG Data |
|---------|---------------|----------------|
| **Complexity** | Simple grids | Complex geography |
| **Data prep** | None needed | Requires shapefiles |
| **Results** | Illustrative | Actual outcomes |
| **Speed** | Fast | Slower |
| **Learning** | Concepts | Practice |
| **Contiguity** | Easy | Can be challenging |

**Recommendation:** Start with synthetic data (learn concepts), then move to real data (apply skills).

---

## Troubleshooting

### Shapefile Not Found
```
FileNotFoundError: Shapefile not found
```
**Solution:**
- Run from project root
- Check data path: `data/data/AK-shapefiles/alaska_precincts.shp`
- Verify files were downloaded/extracted

### Isolated Precincts Warning
```
UserWarning: Found islands (degree-0 nodes)
```
**Solution:** This is normal - scripts automatically remove isolated precincts

### Contiguity Errors
```
ValueError: failed constraints were: single_flip_contiguous
```
**Solution:** Use `real_data_simple.py` instead of `real_data_simulation.py`

---

## Next Steps

After mastering real data:
1. Try other MGGG state datasets
2. Experiment with different elections (2018 Governor vs 2016 Presidential)
3. Create custom visualizations
4. Run full MCMC ensembles (if you solve contiguity issues)
5. Compare multiple states

---

## Learn More

- **MGGG States:** https://github.com/mggg-states
- **MGGG Organization:** https://mggg.org
- **GerryChain Docs:** https://gerrychain.readthedocs.io
- **Redistricting Data Hub:** https://redistrictingdatahub.org
