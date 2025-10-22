#!/usr/bin/env python3
"""
Enhanced Single-State Gerrymandering Detection
===============================================

This script runs gerrymandering detection analysis on a single state with improved
MCMC chain exploration and detailed statistics output.

FIXES FROM ORIGINAL VERSION:
- Uses ReCom proposal instead of random flip for proper ensemble exploration
- Better data column detection to avoid using same column for both parties
- Detailed voting statistics and district breakdowns
- Side-by-side comparison of actual vs ensemble average maps
- More sensitive gerrymandering detection

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
from functools import partial
from gerrychain import Graph, Partition, MarkovChain
from gerrychain.proposals import recom
from gerrychain.constraints import contiguous, within_percent_of_ideal_population
from gerrychain.updaters import cut_edges, Tally
from gerrychain.tree import recursive_tree_part
from gerrychain.accept import always_accept
import warnings
warnings.filterwarnings('ignore', category=UserWarning)

# ============================================================================
# CONFIGURATION - CHANGE THESE PARAMETERS
# ============================================================================

STATE_NAME = "wisconsin"  # ← CHANGE THIS to analyze different states

# Optional: Override number of districts (if None, will auto-detect)
NUM_DISTRICTS = 8  # Set to an integer like 5, 10, etc. or leave as None

# Use actual district assignments if available (set column name or None)
# Examples: "CD_2011" for Pennsylvania 2012, "CON" for Wisconsin, "CONG_DIST" for NC
ACTUAL_DISTRICTS_COLUMN = "CON"  # Set to None to generate random districts

# Number of MCMC steps (more steps = more accurate but slower)
NUM_STEPS = 2000  # Increased from 1000 for better exploration

# Population deviation tolerance (lower = stricter district equality)
EPSILON = 0.05  # 5% deviation

# Gerrymandering detection threshold (percentile cutoffs)
OUTLIER_THRESHOLD = 10  # Flag if < 10th or > 90th percentile (was 5%)

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
    'north-carolina-2022': 'nc_2022_enhanced.shp',
    'ohio': 'oh_2020.shp',
    'ohio-2022': 'oh_2022_enhanced.shp',
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
    'north-carolina-2022': 14,
    'ohio': 15,
    'ohio-2022': 15,
    'oklahoma': 5,
    'oregon': 6,
    'pennsylvania': 18,  # Was 18 in 2012, reduced to 17 after 2020 census
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
    Detect available population and election data columns with improved logic

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
    # IMPORTANT: Make sure we don't use the same column for both parties!

    # Strategy 1: Look for Biden/Trump (2020 data)
    biden_cols = [c for c in columns if 'BID' in c.upper() or 'BIDEN' in c.upper()]
    trump_cols = [c for c in columns if 'TRU' in c.upper() or 'TRUMP' in c.upper()]

    if biden_cols and trump_cols:
        # Make sure they're different columns!
        if biden_cols[0] != trump_cols[0]:
            # Prioritize presidential race
            pres_biden = [c for c in biden_cols if 'PRE' in c.upper()]
            pres_trump = [c for c in trump_cols if 'PRE' in c.upper()]
            if pres_biden and pres_trump and pres_biden[0] != pres_trump[0]:
                result['dem'] = pres_biden[0]
                result['rep'] = pres_trump[0]
                return result if result['population'] or result['dem'] else None
            # Otherwise use first match if they're different
            result['dem'] = biden_cols[0]
            result['rep'] = trump_cols[0]
            return result if result['population'] or result['dem'] else None

    # Strategy 2: Look for Clinton/Trump or Obama/Romney
    clinton_cols = [c for c in columns if 'CLIN' in c.upper() or 'HRC' in c.upper()]
    obama_cols = [c for c in columns if 'OBA' in c.upper()]
    romney_cols = [c for c in columns if 'ROM' in c.upper()]

    if clinton_cols and trump_cols and clinton_cols[0] != trump_cols[0]:
        result['dem'] = clinton_cols[0]
        result['rep'] = trump_cols[0]
        return result if result['population'] or result['dem'] else None

    if obama_cols and romney_cols and obama_cols[0] != romney_cols[0]:
        result['dem'] = obama_cols[0]
        result['rep'] = romney_cols[0]
        return result if result['population'] or result['dem'] else None

    # Strategy 3: Generic pattern matching (PRES16D, PRES12R, etc.)
    # Look for paired D/R columns with the same base name
    election_types = ['PRES', 'PRE', 'SEN', 'USS', 'GOV', 'ATG']

    for election_type in election_types:
        # Find all columns with this election type
        type_cols = [c for c in columns if election_type in c.upper()]

        # Look for D/R pairs
        for col in type_cols:
            col_upper = col.upper()
            # Check if this is a Democratic column
            if 'D' in col_upper and 'DEM' not in col_upper:
                # Try to find matching Republican column
                for rep_variant in [col.replace('D', 'R'), col.replace('d', 'r')]:
                    if rep_variant in columns and rep_variant != col:
                        result['dem'] = col
                        result['rep'] = rep_variant
                        return result if result['population'] or result['dem'] else None
            elif 'DEM' in col_upper:
                # Try to find matching Republican column
                for rep_variant in [col.replace('DEM', 'REP'), col.replace('Dem', 'Rep'),
                                   col.replace('dem', 'rep')]:
                    if rep_variant in columns and rep_variant != col:
                        result['dem'] = col
                        result['rep'] = rep_variant
                        return result if result['population'] or result['dem'] else None

    # Strategy 4: Look for any columns with DEM/REP or D/R that are paired
    dem_generic = [c for c in columns if 'DEM' in c.upper()]
    rep_generic = [c for c in columns if 'REP' in c.upper() and 'GREP' not in c.upper()]

    for dem_col in dem_generic:
        for rep_col in rep_generic:
            # Make sure they're different and likely from same race
            if dem_col != rep_col:
                # Check if they have similar base names
                dem_base = dem_col.upper().replace('DEM', '').replace('D', '')
                rep_base = rep_col.upper().replace('REP', '').replace('R', '')
                if dem_base == rep_base or len(dem_base) > 3 and dem_base[:3] == rep_base[:3]:
                    result['dem'] = dem_col
                    result['rep'] = rep_col
                    return result if result['population'] or result['dem'] else None

    return None


def create_initial_partition(graph, columns, num_districts=5, epsilon=0.05, actual_districts_col=None):
    """
    Create initial district partition

    Args:
        graph: GerryChain graph
        columns (dict): Data column names
        num_districts (int): Number of districts
        epsilon (float): Population deviation tolerance
        actual_districts_col (str): Column name for actual district assignments (None to generate)

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
        print(f"  Population deviation allowed: ±{epsilon*100:.1f}%")

        # Check if we should use actual district assignments
        assignment = None
        if actual_districts_col:
            # Try to use actual district assignments from the data
            sample_node = list(graph.nodes())[0]
            if actual_districts_col in graph.nodes[sample_node]:
                print(f"  Using ACTUAL district assignments from column: {actual_districts_col}")
                assignment = {}
                for node in graph.nodes():
                    district = graph.nodes[node][actual_districts_col]
                    # Handle various district formats (strings, floats, ints)
                    try:
                        if isinstance(district, str):
                            district = int(district) if district.isdigit() else district
                        elif isinstance(district, float):
                            district = int(district)
                        assignment[node] = district
                    except (ValueError, TypeError):
                        print(f"  Warning: Invalid district value '{district}' for node {node}")
                        assignment = None
                        break

                if assignment:
                    # Verify we got the expected number of districts
                    unique_districts = len(set(assignment.values()))
                    print(f"  Found {unique_districts} actual districts in the data")
                    if unique_districts != num_districts:
                        print(f"  Warning: Expected {num_districts} districts but found {unique_districts}")
                        print(f"  Adjusting number of districts to match data...")
                        num_districts = unique_districts
            else:
                print(f"  Warning: Column '{actual_districts_col}' not found in data")
                print(f"  Will generate random districts instead")

        # If we don't have actual assignments, create partition with recursive tree
        if assignment is None:
            print(f"  Generating RANDOM initial districts using recursive tree partitioning...")
            max_attempts = 20

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
                        if attempt % 5 == 0:
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
        import traceback
        traceback.print_exc()
        return None


def run_ensemble(initial_partition, pop_col_name, num_steps=5000, epsilon=0.05):
    """
    Run MCMC ensemble using ReCom for proper exploration

    Args:
        initial_partition: Starting partition
        pop_col_name (str): Name of the population column in the graph
        num_steps (int): Number of steps
        epsilon (float): Population deviation tolerance

    Returns:
        tuple: (list of dem_wins, list of partitions for analysis)
    """
    try:
        # Check if initial partition is contiguous
        from gerrychain.constraints import contiguous as is_contiguous

        use_contiguity = is_contiguous(initial_partition)

        if not use_contiguity:
            print(f"\n  ⚠️  Warning: Initial partition is not contiguous")
            print(f"  This typically indicates disconnected geography or data issues")
            print(f"  Skipping contiguity constraint for ensemble")
            print(f"  Results may be less reliable for detecting gerrymandering\n")

        # Calculate ideal population
        total_pop = sum(initial_partition["population"].values())
        num_districts = len(initial_partition.parts)
        ideal_pop = total_pop / num_districts

        # Set up constraints for ReCom - only use contiguity if initial partition is contiguous
        constraints = [
            within_percent_of_ideal_population(initial_partition, epsilon)
        ]
        if use_contiguity:
            constraints.append(contiguous)

        # Create ReCom proposal using partial - use the actual column name from the graph
        proposal = partial(
            recom,
            pop_col=pop_col_name,
            pop_target=ideal_pop,
            epsilon=epsilon,
            node_repeats=2
        )

        # Create Markov chain
        chain = MarkovChain(
            proposal=proposal,
            constraints=constraints,
            accept=always_accept,
            initial_state=initial_partition,
            total_steps=num_steps
        )

        dem_wins_list = []
        partitions_sample = []  # Store some partitions for comparison
        sample_interval = max(1, num_steps // 100)  # Store ~100 samples

        if use_contiguity:
            print(f"  ✓ Using ReCom proposal with contiguity and {epsilon*100:.1f}% population constraint")
        else:
            print(f"  ✓ Using ReCom proposal with {epsilon*100:.1f}% population constraint (no contiguity)")
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

            # Store sample partitions for later analysis
            if i % sample_interval == 0:
                partitions_sample.append(partition)

        print(" Done!")

        # Check if chain is working properly
        if len(set(dem_wins_list)) == 1:
            print(f"\n  ⚠️  WARNING: Ensemble produced identical results every time!")
            print(f"  This suggests the MCMC chain is stuck and not exploring properly.")
            print(f"  Possible causes:")
            print(f"    - Graph connectivity issues")
            print(f"    - Population constraint too strict")
            print(f"    - Too many districts for the number of precincts")
            print(f"  Results should be interpreted with EXTREME caution.\n")

        return dem_wins_list, partitions_sample

    except Exception as e:
        print(f"\n  ERROR running ensemble: {str(e)}")
        import traceback
        traceback.print_exc()
        return None, None


def get_district_statistics(partition):
    """
    Get detailed statistics for each district in a partition

    Args:
        partition: GerryChain partition

    Returns:
        list: List of district stats (sorted by district number)
    """
    district_stats = []

    for district in sorted(partition.parts.keys()):
        dem_votes = partition["dem_votes"][district]
        rep_votes = partition["rep_votes"][district]
        total_votes = dem_votes + rep_votes

        if total_votes > 0:
            dem_pct = (dem_votes / total_votes) * 100
            rep_pct = (rep_votes / total_votes) * 100
        else:
            dem_pct = rep_pct = 0

        winner = "DEM" if dem_votes > rep_votes else "REP"
        margin = abs(dem_votes - rep_votes)
        margin_pct = (margin / total_votes * 100) if total_votes > 0 else 0

        district_stats.append({
            'district': district,
            'dem_votes': dem_votes,
            'rep_votes': rep_votes,
            'total_votes': total_votes,
            'dem_pct': dem_pct,
            'rep_pct': rep_pct,
            'winner': winner,
            'margin': margin,
            'margin_pct': margin_pct,
            'population': partition["population"][district]
        })

    return district_stats


def calculate_ensemble_average_map(partitions_sample):
    """
    Calculate the average district composition from ensemble samples

    Args:
        partitions_sample: List of partition samples from ensemble

    Returns:
        dict: Average statistics per district
    """
    if not partitions_sample:
        return None

    # Get all unique districts from the first partition
    all_districts = list(partitions_sample[0].parts.keys())

    # Accumulate statistics
    avg_stats = {}
    for district in all_districts:
        avg_stats[district] = {
            'dem_votes': [],
            'rep_votes': [],
            'population': []
        }

    # Collect all samples
    for partition in partitions_sample:
        for district in partition.parts.keys():
            if district in avg_stats:  # Safety check
                avg_stats[district]['dem_votes'].append(partition["dem_votes"][district])
                avg_stats[district]['rep_votes'].append(partition["rep_votes"][district])
                avg_stats[district]['population'].append(partition["population"][district])

    # Calculate averages
    result = []
    for district in sorted(avg_stats.keys()):
        dem_avg = np.mean(avg_stats[district]['dem_votes'])
        rep_avg = np.mean(avg_stats[district]['rep_votes'])
        total_avg = dem_avg + rep_avg

        dem_pct = (dem_avg / total_avg * 100) if total_avg > 0 else 0
        rep_pct = (rep_avg / total_avg * 100) if total_avg > 0 else 0

        winner = "DEM" if dem_avg > rep_avg else "REP"
        margin = abs(dem_avg - rep_avg)
        margin_pct = (margin / total_avg * 100) if total_avg > 0 else 0

        result.append({
            'district': district,
            'dem_votes': dem_avg,
            'rep_votes': rep_avg,
            'total_votes': total_avg,
            'dem_pct': dem_pct,
            'rep_pct': rep_pct,
            'winner': winner,
            'margin': margin,
            'margin_pct': margin_pct,
            'population': np.mean(avg_stats[district]['population'])
        })

    return result


def print_detailed_statistics(initial_stats, ensemble_avg_stats, state_name):
    """
    Print detailed side-by-side comparison of actual vs ensemble maps

    Args:
        initial_stats: Statistics for the actual/initial map
        ensemble_avg_stats: Average statistics from ensemble
        state_name: Name of the state
    """
    print(f"\n  {'='*90}")
    print(f"  DETAILED DISTRICT-BY-DISTRICT COMPARISON")
    print(f"  {'='*90}")
    print(f"\n  ACTUAL MAP (potentially gerrymandered):")
    print(f"  {'-'*90}")
    print(f"  {'Dist':>4} | {'Dem Votes':>12} | {'Rep Votes':>12} | {'Dem %':>7} | {'Rep %':>7} | {'Winner':>6} | {'Margin':>8}")
    print(f"  {'-'*90}")

    actual_dem_wins = 0
    actual_rep_wins = 0

    for stats in initial_stats:
        if stats['winner'] == 'DEM':
            actual_dem_wins += 1
        else:
            actual_rep_wins += 1

        print(f"  {stats['district']:>4} | {stats['dem_votes']:>12,.0f} | {stats['rep_votes']:>12,.0f} | "
              f"{stats['dem_pct']:>6.1f}% | {stats['rep_pct']:>6.1f}% | {stats['winner']:>6} | "
              f"{stats['margin_pct']:>6.1f}%")

    print(f"  {'-'*90}")
    print(f"  TOTALS: {actual_dem_wins} DEM seats, {actual_rep_wins} REP seats")

    if ensemble_avg_stats:
        print(f"\n  ENSEMBLE AVERAGE MAP (expected from fair redistricting):")
        print(f"  {'-'*90}")
        print(f"  {'Dist':>4} | {'Dem Votes':>12} | {'Rep Votes':>12} | {'Dem %':>7} | {'Rep %':>7} | {'Winner':>6} | {'Margin':>8}")
        print(f"  {'-'*90}")

        ensemble_dem_wins = 0
        ensemble_rep_wins = 0

        for stats in ensemble_avg_stats:
            if stats['winner'] == 'DEM':
                ensemble_dem_wins += 1
            else:
                ensemble_rep_wins += 1

            print(f"  {stats['district']:>4} | {stats['dem_votes']:>12,.0f} | {stats['rep_votes']:>12,.0f} | "
                  f"{stats['dem_pct']:>6.1f}% | {stats['rep_pct']:>6.1f}% | {stats['winner']:>6} | "
                  f"{stats['margin_pct']:>6.1f}%")

        print(f"  {'-'*90}")
        print(f"  TOTALS: {ensemble_dem_wins} DEM seats, {ensemble_rep_wins} REP seats")

        # Show the difference
        print(f"\n  DIFFERENCE (Actual - Ensemble Average):")
        print(f"  {'-'*90}")
        seat_diff_dem = actual_dem_wins - ensemble_dem_wins
        seat_diff_rep = actual_rep_wins - ensemble_rep_wins

        if seat_diff_dem > 0:
            print(f"  Actual map gives Democrats {seat_diff_dem} MORE seat(s) than expected")
        elif seat_diff_dem < 0:
            print(f"  Actual map gives Democrats {abs(seat_diff_dem)} FEWER seat(s) than expected")
        else:
            print(f"  Actual map matches ensemble average")

        if seat_diff_rep > 0:
            print(f"  Actual map gives Republicans {seat_diff_rep} MORE seat(s) than expected")
        elif seat_diff_rep < 0:
            print(f"  Actual map gives Republicans {abs(seat_diff_rep)} FEWER seat(s) than expected")


def analyze_state(state_name, shapefile_path, num_districts=None, num_steps=5000, epsilon=0.05, actual_districts_col=None):
    """
    Run full gerrymandering detection for a state

    Args:
        state_name (str): State name
        shapefile_path (str): Path to shapefile
        num_districts (int): Number of districts to create (None to auto-detect)
        num_steps (int): MCMC steps
        epsilon (float): Population deviation tolerance
        actual_districts_col (str): Column name for actual districts (None to generate random)

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

    # Verify we're not using the same column for both parties
    if columns['dem'] == columns['rep']:
        print(f"\n  ❌ ERROR: Same column detected for both Democratic and Republican votes!")
        print(f"  This is a data issue. Cannot proceed with analysis.")
        return None

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
    partition = create_initial_partition(graph, columns, num_districts, epsilon, actual_districts_col)
    if not partition:
        return None

    # Get detailed district statistics for initial map
    initial_district_stats = get_district_statistics(partition)

    # Calculate initial statistics
    initial_dem_wins = sum(
        1 for district in partition.parts.keys()
        if partition["dem_votes"][district] > partition["rep_votes"][district]
    )

    total_dem = sum(partition["dem_votes"].values())
    total_rep = sum(partition["rep_votes"].values())
    total_votes = total_dem + total_rep
    dem_vote_share = total_dem / total_votes * 100 if total_votes > 0 else 0
    rep_vote_share = total_rep / total_votes * 100 if total_votes > 0 else 0

    print(f"\n  STATEWIDE VOTING STATISTICS:")
    print(f"  {'-'*70}")
    print(f"    Total Democratic votes: {total_dem:>15,.0f} ({dem_vote_share:>5.1f}%)")
    print(f"    Total Republican votes: {total_rep:>15,.0f} ({rep_vote_share:>5.1f}%)")
    print(f"    Total votes cast:       {total_votes:>15,.0f}")
    print(f"  {'-'*70}")

    print(f"\n  INITIAL MAP SEAT DISTRIBUTION:")
    print(f"  {'-'*70}")
    print(f"    Democratic districts: {initial_dem_wins}/{num_districts} ({initial_dem_wins/num_districts*100:.1f}%)")
    print(f"    Republican districts: {num_districts - initial_dem_wins}/{num_districts} ({(num_districts-initial_dem_wins)/num_districts*100:.1f}%)")
    print(f"  {'-'*70}")

    # Calculate seats-votes gap
    seat_vote_gap_dem = (initial_dem_wins/num_districts*100) - dem_vote_share
    seat_vote_gap_rep = ((num_districts-initial_dem_wins)/num_districts*100) - rep_vote_share

    print(f"\n  SEATS-VOTES RELATIONSHIP:")
    print(f"  {'-'*70}")
    print(f"    Democratic: {dem_vote_share:.1f}% votes → {initial_dem_wins/num_districts*100:.1f}% seats (gap: {seat_vote_gap_dem:+.1f}%)")
    print(f"    Republican: {rep_vote_share:.1f}% votes → {(num_districts-initial_dem_wins)/num_districts*100:.1f}% seats (gap: {seat_vote_gap_rep:+.1f}%)")
    print(f"  {'-'*70}")

    # Run ensemble
    print(f"\n  Running {num_steps}-step MCMC ensemble...")
    dem_wins_list, partitions_sample = run_ensemble(partition, columns['population'], num_steps, epsilon)
    if not dem_wins_list:
        return None

    # Calculate ensemble average map
    ensemble_avg_stats = calculate_ensemble_average_map(partitions_sample)

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

    # ENHANCED GERRYMANDERING DETECTION with multiple criteria

    # Criterion 1: Percentile test (original)
    percentile_outlier = percentile < OUTLIER_THRESHOLD or percentile > (100 - OUTLIER_THRESHOLD)

    # Criterion 2: Seats-votes gap test (NEW!)
    # If one party gets significantly fewer seats than their vote share, it's suspicious
    seats_votes_gap_threshold = 15  # Flag if gap > 15%
    large_seats_votes_gap = abs(seat_vote_gap_dem) > seats_votes_gap_threshold or abs(seat_vote_gap_rep) > seats_votes_gap_threshold

    # Criterion 3: Efficiency gap / packing test (NEW!)
    # Check if one party has districts with very high margins (>65%) = "packing"
    dem_packing = any(stats['dem_pct'] > 65 and stats['winner'] == 'DEM' for stats in initial_district_stats)
    rep_packing = any(stats['rep_pct'] > 65 and stats['winner'] == 'REP' for stats in initial_district_stats)
    has_packing = dem_packing or rep_packing

    # Criterion 4: Expected vs actual seat difference (NEW!)
    # If actual seats differ from expected by more than 2, it's suspicious
    seat_difference = abs(initial_dem_wins - mean_dem)
    large_seat_difference = seat_difference >= 2.0

    # COMBINED VERDICT
    is_gerrymandered = percentile_outlier or (large_seats_votes_gap and has_packing) or (large_seat_difference and large_seats_votes_gap)

    # Determine which party benefits
    if is_gerrymandered:
        if seat_vote_gap_dem < 0:
            favored_party = "REPUBLICAN"
            disfavored_party = "DEMOCRATIC"
        else:
            favored_party = "DEMOCRATIC"
            disfavored_party = "REPUBLICAN"

    print(f"\n  ENSEMBLE STATISTICS:")
    print(f"  {'-'*70}")
    print(f"    Mean Democratic districts: {mean_dem:.2f}")
    print(f"    Standard deviation: {std_dem:.2f}")
    print(f"    Range: {min_dem} - {max_dem}")
    print(f"    Initial map percentile: {percentile:.1f}%")
    print(f"    Z-score: {z_score:.2f}")
    print(f"  {'-'*70}")

    print(f"\n  GERRYMANDERING DETECTION (Multi-Criteria Analysis):")
    print(f"  {'-'*70}")
    print(f"    Criterion 1 - Percentile Test:")
    print(f"      Percentile: {percentile:.1f}% (threshold: <{OUTLIER_THRESHOLD}% or >{100-OUTLIER_THRESHOLD}%)")
    print(f"      Status: {'⚠️  SUSPICIOUS' if percentile_outlier else '✓ Pass'}")
    print(f"")
    print(f"    Criterion 2 - Seats-Votes Gap Test:")
    print(f"      Democratic gap: {seat_vote_gap_dem:+.1f}% (vote% - seat%)")
    print(f"      Republican gap: {seat_vote_gap_rep:+.1f}% (vote% - seat%)")
    print(f"      Threshold: ±{seats_votes_gap_threshold}%")
    print(f"      Status: {'⚠️  SUSPICIOUS' if large_seats_votes_gap else '✓ Pass'}")
    print(f"")
    print(f"    Criterion 3 - Packing Test (districts won with >65% margin):")
    if dem_packing:
        packed_districts = [stats['district'] for stats in initial_district_stats if stats['dem_pct'] > 65 and stats['winner'] == 'DEM']
        print(f"      Democratic packing detected in district(s): {packed_districts}")
    if rep_packing:
        packed_districts = [stats['district'] for stats in initial_district_stats if stats['rep_pct'] > 65 and stats['winner'] == 'REP']
        print(f"      Republican packing detected in district(s): {packed_districts}")
    print(f"      Status: {'⚠️  SUSPICIOUS' if has_packing else '✓ Pass'}")
    print(f"")
    print(f"    Criterion 4 - Expected vs Actual Seats:")
    print(f"      Expected Democratic seats: {mean_dem:.1f}")
    print(f"      Actual Democratic seats: {initial_dem_wins}")
    print(f"      Difference: {seat_difference:.1f} seats")
    print(f"      Status: {'⚠️  SUSPICIOUS' if large_seat_difference else '✓ Pass'}")
    print(f"  {'-'*70}")

    print(f"\n  FINAL VERDICT:")
    print(f"  {'-'*70}")
    if is_gerrymandered:
        print(f"    🚨 GERRYMANDERING DETECTED 🚨")
        print(f"    ")
        print(f"    This map shows signs of PRO-{favored_party} gerrymandering:")
        if large_seats_votes_gap:
            print(f"      • Large seats-votes gap: {favored_party}s get {abs(seat_vote_gap_rep if favored_party == 'REPUBLICAN' else seat_vote_gap_dem):.1f}% more seats than vote share")
        if has_packing:
            print(f"      • Packing strategy detected: {disfavored_party} voters concentrated in few districts")
        if seat_difference >= 2:
            print(f"      • {favored_party}s gained {seat_difference:.0f} more seat(s) than expected from fair redistricting")
        if percentile_outlier:
            print(f"      • Extreme outlier: at {percentile:.1f}% percentile (very unusual)")
    else:
        print(f"    ✅ NO SIGNIFICANT GERRYMANDERING DETECTED")
        print(f"    ")
        print(f"    The map appears generally fair:")
        print(f"      • Seats-votes gap: {abs(seat_vote_gap_dem):.1f}% (acceptable)")
        print(f"      • District margins appear reasonable")
        print(f"      • Seat distribution within expected range")
    print(f"  {'-'*70}")

    # Print detailed district comparison
    print_detailed_statistics(initial_district_stats, ensemble_avg_stats, state_name)

    # Create histogram data
    histogram = {}
    for wins in dem_wins_list:
        histogram[wins] = histogram.get(wins, 0) + 1

    # Print distribution
    print(f"\n  DISTRIBUTION OF DEMOCRATIC SEATS IN ENSEMBLE:")
    print(f"  {'-'*70}")
    for wins in sorted(histogram.keys()):
        bar_length = int(histogram[wins] / num_steps * 50)
        bar = '█' * bar_length
        marker = ' ← ACTUAL MAP' if wins == initial_dem_wins else ''
        pct = histogram[wins] / num_steps * 100
        print(f"    {wins:2d} seats: {bar} ({histogram[wins]:5d} = {pct:4.1f}%){marker}")
    print(f"  {'-'*70}")

    return {
        'state': state_name,
        'precincts': len(graph.nodes),
        'num_districts': num_districts,
        'initial_dem_wins': initial_dem_wins,
        'dem_vote_share': round(dem_vote_share, 2),
        'rep_vote_share': round(rep_vote_share, 2),
        'total_dem_votes': int(total_dem),
        'total_rep_votes': int(total_rep),
        'ensemble_mean': round(mean_dem, 2),
        'ensemble_std': round(std_dem, 2),
        'ensemble_min': min_dem,
        'ensemble_max': max_dem,
        'percentile': round(percentile, 1),
        'z_score': round(z_score, 2),
        'is_gerrymandered': is_gerrymandered,
        'percentile_outlier': percentile_outlier,
        'large_seats_votes_gap': large_seats_votes_gap,
        'has_packing': has_packing,
        'large_seat_difference': large_seat_difference,
        'ensemble_steps': num_steps,
        'histogram': histogram,
        'seat_vote_gap_dem': round(seat_vote_gap_dem, 1),
        'seat_vote_gap_rep': round(seat_vote_gap_rep, 1)
    }


def main():
    """Run single-state gerrymandering detection"""
    print("="*70)
    print("ENHANCED SINGLE-STATE GERRYMANDERING DETECTION v2.0")
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
        epsilon=EPSILON,
        actual_districts_col=ACTUAL_DISTRICTS_COLUMN
    )

    if result:
        print(f"\n{'='*70}")
        print(f"FINAL SUMMARY")
        print(f"{'='*70}")
        print(f"State: {STATE_NAME.upper()}")
        print(f"Precincts analyzed: {result['precincts']}")
        print(f"Districts: {result['num_districts']}")
        print(f"")
        print(f"Vote Share:")
        print(f"  Democratic: {result['dem_vote_share']}% ({result['total_dem_votes']:,} votes)")
        print(f"  Republican: {result['rep_vote_share']}% ({result['total_rep_votes']:,} votes)")
        print(f"")
        print(f"Seat Distribution:")
        print(f"  Actual: {result['initial_dem_wins']} DEM, {result['num_districts']-result['initial_dem_wins']} REP")
        print(f"  Expected: {result['ensemble_mean']:.1f} DEM (±{result['ensemble_std']:.1f})")
        print(f"")
        print(f"Analysis:")
        print(f"  Percentile: {result['percentile']}%")
        print(f"  Z-score: {result['z_score']}")
        print(f"  Gerrymandering detected: {'YES 🚨' if result['is_gerrymandered'] else 'NO ✅'}")

        print(f"\n✅ Analysis complete at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print(f"\n❌ Analysis failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
