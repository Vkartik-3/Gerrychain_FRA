# MGGG States Redistricting Data

This directory contains real election and redistricting data from the **MGGG States project** - high-quality, pre-processed shapefiles for analyzing gerrymandering and redistricting across the United States.

**Source:** https://github.com/mggg-states

---

## Directory Structure

```
data/
├── README.md (this file)
└── states/
    ├── alaska/
    ├── arizona/
    ├── connecticut/
    ├── delaware/
    ├── georgia/
    ├── hawaii/
    ├── illinois/
    ├── indiana/
    ├── iowa/
    ├── louisiana/
    ├── maine/
    ├── maryland/
    ├── massachusetts/
    ├── michigan/
    ├── minnesota/
    ├── nebraska/
    ├── new-hampshire/
    ├── new-mexico/
    ├── north-carolina/
    ├── oklahoma/
    ├── oregon/
    ├── pennsylvania/
    ├── puerto-rico/
    ├── rhode-island/
    ├── utah/
    ├── vermont/
    ├── washington/
    └── wisconsin/
```

**Total:** 28 states/territories with 50 shapefiles

---

## States Available

### Complete Inventory

| State | Shapefiles | Key File(s) |
|-------|-----------|-------------|
| **Alaska** | 1 | `alaska_precincts.shp` |
| **Arizona** | 1 | `az_precincts.shp` |
| **Connecticut** | 1 | `CT_precincts.shp` |
| **Delaware** | 1 | `DE_precincts.shp` |
| **Georgia** | 1 | `GA_precincts16.shp` |
| **Hawaii** | 1 | `HI_precincts.shp` |
| **Illinois** | 0 | ⚠️ No shapefiles (data may need processing) |
| **Indiana** | 1 | `Indiana.shp` |
| **Iowa** | 1 | `IA_counties.shp` (county-level) |
| **Louisiana** | 1 | `LA_1519.shp` |
| **Maine** | 1 | `Maine.shp` |
| **Maryland** | 2 | `MD-precincts.shp`, `MD-precincts_abs.shp` |
| **Massachusetts** | 2 | `MA_precincts_02_10.shp`, `MA_precincts_12_16.shp` |
| **Michigan** | 1 | `mi16_results.shp` |
| **Minnesota** | 4 | `mn_precincts12.shp`, `mn_precincts14.shp`, `mn_precincts16.shp`, `mn_precincts12_18.shp` |
| **Nebraska** | 1 | `NE.shp` |
| **New Hampshire** | 1 | `NH.shp` |
| **New Mexico** | 1 | `new_mexico_precincts.shp` |
| **North Carolina** | 1 | `NC_VTD.shp` (Voting Tabulation Districts) |
| **Oklahoma** | 1 | `OK_precincts.shp` |
| **Oregon** | 1 | `OR_precincts.shp` |
| **Pennsylvania** | 2 | `PA.shp`, `PA_pop.shp` |
| **Puerto Rico** | 1 | `PR.shp` |
| **Rhode Island** | 1 | `RI_precincts.shp` |
| **Utah** | 1 | `UT_precincts.shp` |
| **Vermont** | 1 | `VT_town_results.shp` (town-level) |
| **Washington** | 5 | `King_2016.shp`, `Chelan_2016.shp`, `Pierce_2016.shp`, etc. (county-level) |
| **Wisconsin** | 2 | `WI.shp`, `WI_ltsb_corrected_final.shp` |

---

## What's Included

Each state directory typically contains:

### **Shapefiles (.shp + supporting files)**
- `.shp` - Main shapefile with geometry
- `.shx` - Shape index
- `.dbf` - Attribute data (population, voting, demographics)
- `.prj` - Projection information
- `.cpg` - Character encoding

### **Election Data**
- Presidential elections (2012, 2016, 2020)
- Senate elections
- Gubernatorial elections
- US House elections
- State legislative elections

### **Demographic Data**
- Total population (`TOTPOP`)
- Voting Age Population (`VAP`)
- Race/ethnicity breakdowns
- Geographic area

### **District Information**
- Congressional districts
- State legislative districts
- Precinct/VTD boundaries

### **Additional Files**
- README files with state-specific documentation
- CSV files with additional data
- JSON files with dual graphs
- Metadata and data dictionaries

---

## Quick Start

### Loading a State in GerryChain

```python
from gerrychain import Graph

# Example: Load Pennsylvania data
graph = Graph.from_file("data/states/pennsylvania/PA.shp")

# Access attributes
for node in graph.nodes():
    population = graph.nodes[node]["TOTPOP"]
    dem_votes = graph.nodes[node]["PRES16D"]  # 2016 Presidential - Democrat
    rep_votes = graph.nodes[node]["PRES16R"]  # 2016 Presidential - Republican
```

### Using in Scripts

```python
# From project root
shapefile_path = "data/states/pennsylvania/PA.shp"

# Or use dynamic path construction
import os
state = "pennsylvania"
shapefile = "PA.shp"
path = os.path.join("data", "states", state, shapefile)
```

---

## Data Quality & Features

### ✅ MGGG States Advantages

**Pre-processed & Validated:**
- Topology errors corrected
- Dual graphs pre-computed (for some states)
- Consistent attribute naming
- Documented data sources

**Research-Grade:**
- Used in academic redistricting research
- Cited in legal cases
- Maintained by domain experts
- Regular updates

**GerryChain Optimized:**
- Works seamlessly with GerryChain
- Tested for MCMC simulations
- Includes necessary attributes

---

## State-Specific Notes

### **Alaska**
- Includes isolated island precincts
- 2016 Presidential election data
- 40 State House districts

### **Pennsylvania**
- Two versions: `PA.shp` (main) and `PA_pop.shp` (population-focused)
- Comprehensive 2016 election data
- VTD-level (Voting Tabulation Districts)

### **Minnesota**
- Multiple election years: 2012, 2014, 2016, 2012-2018
- Precinct-level data
- Well-documented

### **Massachusetts**
- Two time periods: 2002-2010 and 2012-2016
- Option to exclude islands for contiguity
- Multiple election cycles

### **Washington**
- County-specific files (King, Pierce, Benton, Chelan, Wenatchee)
- 2016 election data
- May need merging for statewide analysis

### **Illinois**
- ⚠️ No extracted shapefiles found
- May require additional processing or different format

---

## Common Attribute Names

While attribute names vary by state, common patterns include:

| Category | Common Attributes |
|----------|-------------------|
| **Population** | `TOTPOP`, `POP`, `POPULATION`, `VAP` |
| **2016 Presidential** | `PRES16D`, `PRES16R`, `PRES16L`, `PRES16G` |
| **2012 Presidential** | `PRES12D`, `PRES12R` |
| **Senate** | `SEN16D`, `SEN16R`, `SEN14D`, `SEN14R` |
| **Governor** | `GOV18D`, `GOV18R`, `GOV14D`, `GOV14R` |
| **US House** | `USH16D`, `USH16R` |
| **Demographics** | `WHITE`, `BLACK`, `ASIAN`, `HISP`, `AMIN` |
| **Districts** | `CD`, `HDIST`, `SDIST`, `DISTRICT` |
| **Geography** | `AREA`, `GEOID`, `NAME` |

**Note:** Always check the README in each state directory for specific attribute documentation.

---

## Data Size

| Category | Count |
|----------|-------|
| **Total States** | 28 (27 states + Puerto Rico) |
| **Total Shapefiles** | 50 |
| **Disk Space** | ~500 MB - 1 GB (after extraction) |
| **Precincts/Units** | Varies (50 to 9,000+ per state) |

---

## Using with Scripts

### Synthetic Data Scripts
Located in `scripts/synthetic_data/` - these don't need real data:
```bash
python scripts/synthetic_data/simple_simulation.py
```

### Real Data Scripts
Located in `scripts/real_data/` - configured to use Alaska by default:
```bash
python scripts/real_data/real_data_simple.py
```

**To use a different state**, modify the `shapefile_path` in the script:
```python
# In real_data_simple.py
shapefile_path = "data/states/pennsylvania/PA.shp"  # Change state here
```

---

## Adding More States

MGGG States has additional repositories not yet downloaded. To add more:

1. Check available states: https://github.com/mggg-states
2. Clone the repository:
   ```bash
   cd data/states
   git clone https://github.com/mggg-states/[STATE]-shapefiles.git [state-name]
   ```
3. Extract any zipped shapefiles:
   ```bash
   cd [state-name]
   unzip *.zip
   ```

---

## Data Updates

MGGG States data is periodically updated. To update:

```bash
cd data/states/[state-name]
git pull
# Re-extract any new zip files if needed
```

---

## Citation

If you use this data in research or publications, please cite:

**MGGG Redistricting Lab**
- Organization: Metric Geometry and Gerrymandering Group
- Website: https://mggg.org
- GitHub: https://github.com/mggg-states
- Individual state repositories have specific README files with citation information

---

## License

Each state's data has its own license (typically MIT or CC). Check the `LICENSE.md` file in each state directory.

---

## Learn More

- **MGGG States:** https://github.com/mggg-states
- **MGGG Organization:** https://mggg.org
- **GerryChain Docs:** https://gerrychain.readthedocs.io
- **Redistricting Data Hub:** https://redistrictingdatahub.org

---

## Troubleshooting

### Shapefile Not Found
```
FileNotFoundError: Shapefile not found
```
**Solution:** Check the exact filename in the state directory - names vary!

### Missing Attributes
```
KeyError: 'PRES16D'
```
**Solution:** Attribute names differ by state. Check the state's README or use:
```python
print(list(graph.nodes[0].keys()))  # List all available attributes
```

### Illinois Has No Shapefiles
Illinois data may require additional processing or may be in a different format. Check the state repository README for instructions.

### Contiguity Issues
Some states have islands or disconnected regions. Scripts automatically remove isolated nodes, but this may affect analysis.

---

## Quick Reference

**Most Popular States for Analysis:**
- Pennsylvania - Competitive, well-studied
- North Carolina - Legal redistricting cases
- Wisconsin - Gerrymandering debates
- Michigan - Citizen redistricting commission
- Georgia - Changing demographics

**Best for Learning:**
- Alaska - Small, manageable (437 precincts)
- Rhode Island - Compact geography
- Delaware - Single congressional district

**Most Complex:**
- Pennsylvania - Large, detailed
- Minnesota - Multiple election years
- Washington - County-specific files
