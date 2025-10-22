#!/usr/bin/env python3
"""
Single-State Gerrymandering Detection
======================================

This script runs gerrymandering detection analysis on a single state specified by the user.
It processes the state's shapefile data and generates a comprehensive report showing
potential gerrymandering.

For the specified state, the script:
1. Loads the shapefile data
2. Creates contiguous districts using recursive tree partitioning
3. Runs MCMC ensemble to generate fair alternative maps
4. Compares the actual results to the ensemble distribution
5. Flags states with suspicious outlier patterns

USAGE:
------
Simply change the STATE_NAME variable below to analyze different states.
Example:
    STATE_NAME = "pennsylvania"
    STATE_NAME = "north-carolina"
    STATE_NAME = "wisconsin"
"""

import os
import sys
import json
import numpy as np
from datetime import datetime
from gerrychain import Graph, Partition, MarkovChain
from gerrychain.proposals import propose_random_flip
from gerrychain.constraints import single_flip_contiguous
from gerrychain.updaters import cut_edges, Tally
from gerrychain.tree import recursive_tree_part
import warnings
warnings.filterwarnings('ignore', category=UserWarning)

# ============================================================================
# CONFIGURATION - CHANGE THESE PARAMETERS
# ============================================================================

STATE_NAME = "pennsylvania"  # ← CHANGE THIS to analyze different states

# Optional: Override number of districts (if None, will auto-detect or use 5)
NUM_DISTRICTS = None  # Set to an integer like 5, 10, etc. or leave as None

# Number of MCMC steps (more steps = more accurate but slower)
NUM_STEPS = 1000  # Default: 1000 (use 500 for faster, 5000 for more accurate)

# Population deviation tolerance
EPSILON = 0.50  # Allow 50% population deviation between districts (needed for small states)

# ============================================================================


# State configuration: maps state directory names to their primary shapefile
STATE_CONFIGS = {
    'alabama': 'al_2020.shp',
    'alaska': 'alaska_precincts.shp',
    'arizona': 'az_precincts.shp',
    'california': 'ca_2020.shp',
    'colorado': 'co_2020.shp',
    'connecticut': 'CT_precincts.shp',
    'delaware': 'DE_precincts.shp',
    'florida': 'fl_2020.shp',
    'georgia': 'GA_precincts16.shp',
    'hawaii': 'HI_precincts.shp',
    'illinois': None,  # Will auto-detect
    'indiana': 'Indiana.shp',
    'iowa': 'IA_counties.shp',
    'louisiana': 'LA_1519.shp',
    'maine': 'Maine.shp',
    'maryland': 'MD-precincts.shp',
    'massachusetts': 'MA_precincts_12_16.shp',
    'michigan': 'mi16_results.shp',
    'minnesota': 'mn_precincts16.shp',
    'nebraska': 'NE.shp',
    'new-hampshire': 'NH.shp',
    'new-mexico': 'new_mexico_precincts.shp',
    'new-york': 'ny_2020.shp',
    'north-carolina': 'NC_VTD.shp',
    'ohio': 'oh_2020.shp',
    'oklahoma': 'OK_precincts.shp',
    'oregon': 'OR_precincts.shp',
    'pennsylvania': 'PA.shp',
    'puerto-rico': 'PR.shp',
    'rhode-island': 'RI_precincts.shp',
    'utah': 'UT_precincts.shp',
    'vermont': 'VT_town_results.shp',
    'washington': 'King_2016.shp',  # Using largest county
    'wisconsin': 'WI_ltsb_corrected_final.shp',
}

# Real congressional district counts (2020+ redistricting)
REAL_DISTRICTS = {
    'alabama': 7,
    'alaska': 1,
    'arizona': 9,
    'california': 52,
    'colorado': 8,
    'connecticut': 5,
    'delaware': 1,
    'florida': 28,
    'georgia': 14,
    'hawaii': 2,
    'illinois': 17,
    'indiana': 9,
    'iowa': 4,
    'louisiana': 6,
    'maine': 2,
    'maryland': 8,
    'massachusetts': 9,
    'michigan': 13,
    'minnesota': 8,
    'nebraska': 3,
    'new-hampshire': 2,
    'new-mexico': 3,
    'new-york': 26,
    'north-carolina': 14,
    'ohio': 15,
    'oklahoma': 5,
    'oregon': 6,
    'pennsylvania': 17,
    'puerto-rico': 1,  # Non-voting resident commissioner
    'rhode-island': 2,
    'utah': 4,
    'vermont': 1,
    'washington': 10,
    'wisconsin': 8,
}


def find_shapefile(state_dir):
    """
    Find the primary shapefile for a state

    Args:
        state_dir (str): Path to state directory

    Returns:
        str: Path to shapefile or None
    """
    state_name = os.path.basename(state_dir.rstrip('/'))

    # Try configured shapefile first
    if state_name in STATE_CONFIGS and STATE_CONFIGS[state_name]:
        shapefile = os.path.join(state_dir, STATE_CONFIGS[state_name])
        if os.path.exists(shapefile):
            return shapefile

    # Auto-detect: find first .shp file (excluding __MACOSX)
    for root, _, files in os.walk(state_dir):
        if '__MACOSX' in root:
            continue
        for file in files:
            if file.endswith('.shp') and not file.startswith('.'):
                return os.path.join(root, file)

    return None


def load_state_data(shapefile_path, state_name=None):
    """
    Load state shapefile data

    Args:
        shapefile_path (str): Path to shapefile
        state_name (str): Name of the state (optional)

    Returns:
        Graph: GerryChain graph or None on error
    """
    try:
        print(f"  Loading {shapefile_path}...")
        try:
            graph = Graph.from_file(shapefile_path)
        except Exception as e:
            if "Invalid geometries" in str(e):
                print(f"  Repairing invalid geometries...")
                import geopandas as gpd
                gdf = gpd.read_file(shapefile_path)
                gdf['geometry'] = gdf['geometry'].buffer(0)
                graph = Graph.from_geodataframe(gdf)
            else:
                raise e

        # Remove isolated nodes
        isolated_nodes = [node for node in graph.nodes() if graph.degree(node) == 0]
        if isolated_nodes:
            print(f"  Removing {len(isolated_nodes)} isolated nodes...")
            graph.remove_nodes_from(isolated_nodes)

        print(f"  Loaded {len(graph.nodes)} precincts")
        return graph

    except Exception as e:
        print(f"  ERROR loading data: {str(e)}")
        return None


def detect_data_columns(graph):
    """
    Detect available population and election data columns

    Args:
        graph: GerryChain graph

    Returns:
        dict: Dictionary with 'population', 'dem', 'rep' column names
    """
    if not graph.nodes:
        return None

    sample_node = list(graph.nodes())[0]
    node_data = graph.nodes[sample_node]
    columns = list(node_data.keys())

    result = {'population': None, 'dem': None, 'rep': None}

    # Find population column
    pop_candidates = ['TOTPOP', 'POP', 'POPULATION', 'TOT_POP', 'PERSONS', 'VAP', 'CVAP']
    for col in columns:
        col_upper = col.upper()
        if any(cand in col_upper for cand in pop_candidates):
            result['population'] = col
            break

    # If no population column found, create synthetic population based on vote totals
    if not result['population']:
        print("  Warning: No population column found, will use vote totals as proxy")

    # Find election columns with multiple strategies

    # Strategy 1: Look for Biden/Trump (2020 data)
    biden_cols = [c for c in columns if 'BID' in c.upper() or 'BIDEN' in c.upper()]
    trump_cols = [c for c in columns if 'TRU' in c.upper() or 'TRUMP' in c.upper()]

    if biden_cols and trump_cols:
        # Prioritize presidential race
        pres_biden = [c for c in biden_cols if 'PRE' in c.upper()]
        pres_trump = [c for c in trump_cols if 'PRE' in c.upper()]
        if pres_biden and pres_trump:
            result['dem'] = pres_biden[0]
            result['rep'] = pres_trump[0]
            return result if result['population'] or result['dem'] else None
        # Otherwise use first match
        result['dem'] = biden_cols[0]
        result['rep'] = trump_cols[0]
        return result if result['population'] or result['dem'] else None

    # Strategy 2: Look for Clinton/Trump or Obama/Romney
    clinton_cols = [c for c in columns if 'CLIN' in c.upper() or 'HRC' in c.upper()]
    obama_cols = [c for c in columns if 'OBA' in c.upper()]
    romney_cols = [c for c in columns if 'ROM' in c.upper()]

    if clinton_cols and trump_cols:
        result['dem'] = clinton_cols[0]
        result['rep'] = trump_cols[0]
        return result if result['population'] or result['dem'] else None

    if obama_cols and romney_cols:
        result['dem'] = obama_cols[0]
        result['rep'] = romney_cols[0]
        return result if result['population'] or result['dem'] else None

    # Strategy 3: Generic pattern matching (PRES16D, PRES12R, etc.)
    election_types = ['PRES', 'PRE', 'SEN', 'USS', 'GOV', 'ATG']

    for election_type in election_types:
        dem_candidates = [c for c in columns if election_type in c.upper() and 'D' in c.upper()]
        if dem_candidates:
            dem_col = dem_candidates[0]
            # Try to find corresponding Republican column
            rep_col = None
            for variant in [dem_col.replace('D', 'R'), dem_col.replace('d', 'r'),
                           dem_col.replace('DEM', 'REP'), dem_col.replace('dem', 'rep')]:
                if variant in columns:
                    rep_col = variant
                    break

            if rep_col:
                result['dem'] = dem_col
                result['rep'] = rep_col
                return result if result['population'] or result['dem'] else None

    # Strategy 4: Look for any columns with DEM/REP or D/R
    dem_generic = [c for c in columns if 'DEM' in c.upper() and any(x in c.upper() for x in ['VOTE', 'TOTAL', 'COUNT'])]
    rep_generic = [c for c in columns if 'REP' in c.upper() and any(x in c.upper() for x in ['VOTE', 'TOTAL', 'COUNT'])]

    if dem_generic and rep_generic:
        result['dem'] = dem_generic[0]
        result['rep'] = rep_generic[0]
        return result if result['population'] or result['dem'] else None

    return None


def create_initial_partition(graph, columns, num_districts=5, epsilon=0.30):
    """
    Create initial district partition

    Args:
        graph: GerryChain graph
        columns (dict): Data column names
        num_districts (int): Number of districts
        epsilon (float): Population deviation tolerance

    Returns:
        Partition: Initial partition or None on error
    """
    try:
        pop_col = columns['population']
        dem_col = columns['dem']
        rep_col = columns['rep']

        # Ensure all data is numeric (convert strings to numbers)
        for node in graph.nodes():
            node_data = graph.nodes[node]

            # Convert dem votes to numeric
            if dem_col in node_data:
                try:
                    node_data[dem_col] = float(node_data[dem_col])
                except (ValueError, TypeError):
                    node_data[dem_col] = 0

            # Convert rep votes to numeric
            if rep_col in node_data:
                try:
                    node_data[rep_col] = float(node_data[rep_col])
                except (ValueError, TypeError):
                    node_data[rep_col] = 0

            # Handle population column
            if pop_col and pop_col in node_data:
                try:
                    node_data[pop_col] = float(node_data[pop_col])
                except (ValueError, TypeError):
                    node_data[pop_col] = 0
            elif not pop_col:
                # Use vote total as proxy for population
                node_data['synthetic_pop'] = node_data.get(dem_col, 0) + node_data.get(rep_col, 0)

        # Use synthetic population if no population column
        if not pop_col:
            pop_col = 'synthetic_pop'
            columns['population'] = pop_col
            print("  Using total votes as population proxy")

        total_pop = sum(graph.nodes[node].get(pop_col, 0) for node in graph.nodes())
        target_pop = total_pop / num_districts

        print(f"  Total population: {total_pop:,.0f}")
        print(f"  Target population per district: {target_pop:,.0f}")

        # Create partition with recursive tree - try multiple times if needed
        max_attempts = 10
        assignment = None

        for attempt in range(max_attempts):
            try:
                assignment = recursive_tree_part(
                    graph,
                    range(num_districts),
                    target_pop,
                    pop_col,
                    epsilon=epsilon
                )
                break
            except Exception as e:
                if attempt < max_attempts - 1:
                    print(f"  Attempt {attempt + 1} failed, retrying...")
                    continue
                else:
                    raise e

        if assignment is None:
            raise Exception("Could not create valid partition after multiple attempts")

        # Set up updaters
        updaters = {
            "cut_edges": cut_edges,
            "population": Tally(pop_col, alias="population"),
            "dem_votes": Tally(dem_col, alias="dem_votes"),
            "rep_votes": Tally(rep_col, alias="rep_votes"),
        }

        partition = Partition(graph, assignment, updaters)
        return partition

    except Exception as e:
        print(f"  ERROR creating partition: {str(e)}")
        return None


def run_ensemble(initial_partition, num_steps=1000, use_contiguity=True):
    """
    Run MCMC ensemble

    Args:
        initial_partition: Starting partition
        num_steps (int): Number of steps
        use_contiguity (bool): Whether to enforce contiguity constraint

    Returns:
        list: Democratic district wins for each step
    """
    try:
        # First verify the initial partition is contiguous if we're enforcing it
        from gerrychain.constraints import contiguous

        is_contiguous = contiguous(initial_partition)

        if use_contiguity and not is_contiguous:
            print(f"\n  ⚠️  Warning: Initial partition is not contiguous")
            print(f"  This typically indicates:")
            print(f"    - Islands or disconnected geography (Alaska, Hawaii)")
            print(f"    - Data quality issues")
            print(f"  Relaxing contiguity constraint for this analysis")
            print(f"  NOTE: Results may be less reliable for detecting gerrymandering")
            use_contiguity = False

        # Set up constraints based on whether we can use contiguity
        if use_contiguity:
            constraints = [single_flip_contiguous]
            print(f"  ✓ Using contiguity constraint (standard for gerrymandering detection)")
        else:
            constraints = []  # No constraints for disconnected geographies
            print(f"  Running ensemble without contiguity constraint")

        chain = MarkovChain(
            proposal=propose_random_flip,
            constraints=constraints,
            accept=lambda _: True,
            initial_state=initial_partition,
            total_steps=num_steps
        )

        dem_wins_list = []
        print(f"  Progress: ", end='', flush=True)
        for i, partition in enumerate(chain):
            # Print progress every 10%
            if (i + 1) % (num_steps // 10) == 0:
                print(f"{(i+1)*100//num_steps}%...", end='', flush=True)

            dem_wins = sum(
                1 for district in partition.parts.keys()
                if partition["dem_votes"][district] > partition["rep_votes"][district]
            )
            dem_wins_list.append(dem_wins)

        print(" Done!")
        return dem_wins_list

    except Exception as e:
        print(f"\n  ERROR running ensemble: {str(e)}")
        return None


def analyze_state(state_name, shapefile_path, num_districts=None, num_steps=1000, epsilon=0.30):
    """
    Run full gerrymandering detection for a state

    Args:
        state_name (str): State name
        shapefile_path (str): Path to shapefile
        num_districts (int): Number of districts to create (None to auto-detect)
        num_steps (int): MCMC steps
        epsilon (float): Population deviation tolerance

    Returns:
        dict: Analysis results or None on error
    """
    print(f"\n{'='*70}")
    print(f"GERRYMANDERING DETECTION ANALYSIS: {state_name.upper()}")
    print(f"{'='*70}")

    # Load data
    graph = load_state_data(shapefile_path, state_name)
    if not graph:
        return None

    # Detect columns
    columns = detect_data_columns(graph)
    if not columns:
        print(f"  ERROR: Could not find required data columns")
        print(f"  Available columns: {list(graph.nodes[list(graph.nodes())[0]].keys())}")
        return None

    print(f"  Using columns:")
    print(f"    Population: {columns['population']}")
    print(f"    Democratic votes: {columns['dem']}")
    print(f"    Republican votes: {columns['rep']}")

    # Auto-detect number of districts if not specified
    if num_districts is None:
        # Use real congressional district counts if available
        if state_name in REAL_DISTRICTS:
            num_districts = REAL_DISTRICTS[state_name]
            print(f"  Using real congressional districts: {num_districts}")
        else:
            # Fallback to size-based estimation
            num_precincts = len(graph.nodes)
            if num_precincts < 100:
                num_districts = 3
            elif num_precincts < 500:
                num_districts = 5
            elif num_precincts < 2000:
                num_districts = 8
            else:
                num_districts = 10
            print(f"  Auto-detected number of districts: {num_districts} (no real count available)")
    else:
        print(f"  Using manually configured number of districts: {num_districts}")

    # Create initial partition
    partition = create_initial_partition(graph, columns, num_districts, epsilon)
    if not partition:
        return None

    # Calculate initial statistics
    initial_dem_wins = sum(
        1 for district in partition.parts.keys()
        if partition["dem_votes"][district] > partition["rep_votes"][district]
    )

    total_dem = sum(partition["dem_votes"].values())
    total_rep = sum(partition["rep_votes"].values())
    dem_vote_share = total_dem / (total_dem + total_rep) * 100

    print(f"\n  INITIAL MAP STATISTICS:")
    print(f"    Democratic districts: {initial_dem_wins}/{num_districts}")
    print(f"    Republican districts: {num_districts - initial_dem_wins}/{num_districts}")
    print(f"    Statewide Democratic vote share: {dem_vote_share:.1f}%")
    print(f"    Statewide Republican vote share: {100-dem_vote_share:.1f}%")

    # Run ensemble
    print(f"\n  Running {num_steps}-step MCMC ensemble...")
    dem_wins_list = run_ensemble(partition, num_steps)
    if not dem_wins_list:
        return None

    # Analyze results
    mean_dem = np.mean(dem_wins_list)
    std_dem = np.std(dem_wins_list)
    min_dem = min(dem_wins_list)
    max_dem = max(dem_wins_list)

    # Calculate percentile (using midpoint method for ties)
    below_initial = sum(1 for x in dem_wins_list if x < initial_dem_wins)
    equal_initial = sum(1 for x in dem_wins_list if x == initial_dem_wins)
    percentile = ((below_initial + 0.5 * equal_initial) / len(dem_wins_list)) * 100

    # Calculate z-score
    z_score = (initial_dem_wins - mean_dem) / std_dem if std_dem > 0 else 0

    # Determine if suspicious (outlier if < 5th or > 95th percentile)
    is_outlier = percentile < 5 or percentile > 95

    print(f"\n  ENSEMBLE STATISTICS:")
    print(f"    Mean Democratic districts: {mean_dem:.2f}")
    print(f"    Standard deviation: {std_dem:.2f}")
    print(f"    Range: {min_dem} - {max_dem}")
    print(f"    Initial map percentile: {percentile:.1f}%")
    print(f"    Z-score: {z_score:.2f}")

    print(f"\n  ANALYSIS:")
    if is_outlier:
        direction = "PRO-DEMOCRATIC" if percentile > 50 else "PRO-REPUBLICAN"
        print(f"    ⚠️  SUSPICIOUS: Potential {direction} gerrymandering detected!")
        print(f"    The initial map is at the {percentile:.1f}% percentile,")
        print(f"    which is a significant outlier compared to fair redistricting.")
    else:
        print(f"    ✅ Appears consistent with fair redistricting")
        print(f"    The initial map is within expected range of neutral maps.")

    # Check if contiguity was used
    from gerrychain.constraints import contiguous
    if not contiguous(partition):
        print(f"\n    ℹ️  Note: Analysis was performed without contiguity constraint")
        print(f"    This is typically due to islands or disconnected geography.")
        print(f"    Results should be interpreted with caution.")

    # Create histogram data
    histogram = {}
    for wins in dem_wins_list:
        histogram[wins] = histogram.get(wins, 0) + 1

    # Print distribution
    print(f"\n  DISTRIBUTION OF DEMOCRATIC DISTRICTS:")
    for wins in sorted(histogram.keys()):
        bar_length = int(histogram[wins] / num_steps * 50)
        bar = '█' * bar_length
        marker = ' ←' if wins == initial_dem_wins else ''
        print(f"    {wins:2d} districts: {bar} ({histogram[wins]:4d} times){marker}")

    return {
        'state': state_name,
        'precincts': len(graph.nodes),
        'num_districts': num_districts,
        'initial_dem_wins': initial_dem_wins,
        'dem_vote_share': round(dem_vote_share, 2),
        'ensemble_mean': round(mean_dem, 2),
        'ensemble_std': round(std_dem, 2),
        'ensemble_min': min_dem,
        'ensemble_max': max_dem,
        'percentile': round(percentile, 1),
        'z_score': round(z_score, 2),
        'is_outlier': is_outlier,
        'ensemble_steps': num_steps,
        'histogram': histogram
    }


def main():
    """Run single-state gerrymandering detection"""
    print("="*70)
    print("SINGLE-STATE GERRYMANDERING DETECTION")
    print("="*70)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Analyzing state: {STATE_NAME.upper()}")

    # Find data directory
    data_dir = "data/states"
    if not os.path.exists(data_dir):
        # Try from scripts directory
        data_dir = "../../data/states"

    if not os.path.exists(data_dir):
        print(f"ERROR: Could not find data directory")
        print(f"Expected: {os.path.abspath(data_dir)}")
        sys.exit(1)

    # Find state directory
    state_path = os.path.join(data_dir, STATE_NAME)
    if not os.path.exists(state_path):
        print(f"ERROR: State directory not found: {state_path}")
        print(f"\nAvailable states:")
        available_states = sorted([d for d in os.listdir(data_dir)
                                  if os.path.isdir(os.path.join(data_dir, d))])
        for state in available_states:
            print(f"  - {state}")
        sys.exit(1)

    # Find shapefile
    shapefile = find_shapefile(state_path)
    if not shapefile:
        print(f"ERROR: No shapefile found in {state_path}")
        sys.exit(1)

    # Determine number of districts
    num_districts = NUM_DISTRICTS

    # Run analysis
    result = analyze_state(
        STATE_NAME,
        shapefile,
        num_districts=num_districts,
        num_steps=NUM_STEPS,
        epsilon=EPSILON
    )

    if result:
        print(f"\n{'='*70}")
        print(f"SUMMARY")
        print(f"{'='*70}")
        print(f"State: {STATE_NAME.upper()}")
        print(f"Precincts analyzed: {result['precincts']}")
        print(f"Districts: {result['num_districts']}")
        print(f"Initial Democratic wins: {result['initial_dem_wins']}")
        print(f"Ensemble mean: {result['ensemble_mean']}")
        print(f"Percentile: {result['percentile']}%")
        print(f"Outlier: {'YES ⚠️' if result['is_outlier'] else 'NO ✅'}")

        print(f"\n✅ Analysis complete at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print(f"\n❌ Analysis failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
