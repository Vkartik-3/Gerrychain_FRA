# Multi-State Gerrymandering Detection

This directory contains scripts for detecting gerrymandering across all 34 states in the data directory.

## Scripts

### `multi_state_detection.py`
**Main script for comprehensive gerrymandering detection across all states**

This script:
- Automatically finds and processes all 34 states in `data/states/`
- Loads each state's shapefile data
- Creates contiguous districts using recursive tree partitioning
- Runs MCMC ensemble (500 steps by default) to generate fair alternative maps
- Compares actual district outcomes to the ensemble distribution
- Flags states with suspicious outlier patterns (< 5th or > 95th percentile)
- Generates comprehensive JSON and CSV reports

**Usage:**
```bash
export PYTHONPATH="/Users/kartikvadhawana/Desktop/FRA/GerryChain:$PYTHONPATH"
python scripts/real_data/multi_state_detection.py
```

**Output:**
- `gerrymandering_results_YYYYMMDD_HHMMSS.json` - Detailed results for each state
- `gerrymandering_results_YYYYMMDD_HHMMSS.csv` - CSV format for easy analysis
- Console output with summary and top 10 most extreme outliers

**Note:** Processing all 34 states with 500 MCMC steps each takes significant time (potentially hours depending on your system).

### `quick_demo.py`
**Quick demonstration version**

Processes just 3 smaller states (Delaware, Rhode Island, Vermont) with 100 MCMC steps each to demonstrate functionality quickly.

**Usage:**
```bash
export PYTHONPATH="/Users/kartikvadhawana/Desktop/FRA/GerryChain:$PYTHONPATH"
python scripts/real_data/quick_demo.py
```

## How It Works

### 1. Data Loading
- Finds shapefile for each state
- Removes isolated nodes (islands) that cause contiguity issues
- Detects available data columns (population, Democratic votes, Republican votes)

### 2. District Creation
- Uses recursive tree partitioning to create contiguous districts
- Allows 30% population deviation for flexibility with real-world geography
- Default: 5 districts per state (can be adjusted)

### 3. MCMC Ensemble
- Runs Markov Chain Monte Carlo simulation
- Uses random flip proposal with single-flip contiguity constraint
- Generates 500 (or 100 for quick demo) alternative fair maps
- Tracks Democratic district wins for each map

### 4. Analysis
- Compares initial map's outcome to ensemble distribution
- Calculates percentile rank of initial outcome
- Flags outliers (< 5th or > 95th percentile) as potentially gerrymandered
- Identifies whether bias favors Democrats or Republicans

## Understanding the Results

### Percentile Interpretation
- **0-5th percentile**: Extreme pro-Republican bias (suspicious)
- **5-45th percentile**: Slight pro-Republican lean (possibly fair)
- **45-55th percentile**: Balanced (likely fair)
- **55-95th percentile**: Slight pro-Democratic lean (possibly fair)
- **95-100th percentile**: Extreme pro-Democratic bias (suspicious)

### Example Output
```
⚠️  DELAWARE          -   0.0% percentile (PRO-REP) - SUSPICIOUS!
✅ MARYLAND           -  42.3% percentile - Looks fair
```

## State Configuration

The script includes a state configuration dictionary that maps state directory names to their primary shapefiles. Some states have multiple shapefiles; the configuration specifies which one to use.

## Common Issues

1. **Contiguity errors**: Some states have non-contiguous geography (islands). The script removes isolated nodes, but this may still cause issues for some states.

2. **Data format variations**: Different states use different column names for election data. The script attempts to detect columns automatically but may fail for unusual formats.

3. **Missing data**: Some states may not have the required election data (need both Democratic and Republican vote counts).

4. **Memory usage**: Processing large states (California, Florida, Texas) requires significant RAM.

## Customization

To modify the analysis parameters, edit these values in the script:

- `num_districts`: Number of districts to create (default: 5)
- `num_steps`: MCMC ensemble size (default: 500)
- `epsilon`: Population deviation tolerance (default: 0.30 = 30%)

## References

This analysis is based on the methodology described in:
- [Measuring Partisan Gerrymandering](https://www.brennancenter.org/sites/default/files/publications/How_the_Efficiency_Gap_Standard_Works.pdf)
- [MGGG Redistricting Lab](https://mggg.org/)
- [GerryChain Documentation](https://gerrychain.readthedocs.io/)

## Data Source

State shapefiles are from the [MGGG States Project](https://github.com/mggg-states/), which provides precinct-level shapefiles with election results and demographic data for redistricting research.
