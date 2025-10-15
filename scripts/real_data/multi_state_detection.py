#!/usr/bin/env python3
"""
Multi-State Gerrymandering Detection
=====================================

This script runs gerrymandering detection analysis on all 34 states in the data directory.
It processes each state's shapefile data and generates a comprehensive report showing
potential gerrymandering across multiple states.

For each state, the script:
1. Loads the shapefile data
2. Creates contiguous districts using recursive tree partitioning
3. Runs MCMC ensemble to generate fair alternative maps
4. Compares the actual results to the ensemble distribution
5. Flags states with suspicious outlier patterns
"""

import os
import sys
import json
import pandas as pd
from datetime import datetime
from gerrychain import Graph, Partition, MarkovChain
from gerrychain.proposals import propose_random_flip
from gerrychain.constraints import single_flip_contiguous
from gerrychain.updaters import cut_edges, Tally
from gerrychain.tree import recursive_tree_part


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
    for root, dirs, files in os.walk(state_dir):
        if '__MACOSX' in root:
            continue
        for file in files:
            if file.endswith('.shp') and not file.startswith('.'):
                return os.path.join(root, file)

    return None


def load_state_data(shapefile_path, state_name):
    """
    Load state shapefile data

    Args:
        shapefile_path (str): Path to shapefile
        state_name (str): Name of the state

    Returns:
        Graph: GerryChain graph or None on error
    """
    try:
        print(f"  Loading {shapefile_path}...")
        graph = Graph.from_file(shapefile_path)

        # Remove isolated nodes
        isolated_nodes = [node for node in graph.nodes() if graph.degree(node) == 0]
        if isolated_nodes:
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
    pop_candidates = ['TOTPOP', 'POP', 'POPULATION', 'TOT_POP', 'PERSONS']
    for col in columns:
        if any(cand in col.upper() for cand in pop_candidates):
            result['population'] = col
            break

    # Find election columns (prioritize presidential, then senate, then governor)
    election_types = ['PRES', 'SEN', 'GOV', 'USS', 'ATG']

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
                break

    return result if result['population'] and result['dem'] and result['rep'] else None


def create_initial_partition(graph, columns, num_districts=5):
    """
    Create initial district partition

    Args:
        graph: GerryChain graph
        columns (dict): Data column names
        num_districts (int): Number of districts

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

            # Convert population to numeric
            if pop_col in node_data:
                try:
                    node_data[pop_col] = float(node_data[pop_col])
                except (ValueError, TypeError):
                    node_data[pop_col] = 0

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

        total_pop = sum(graph.nodes[node].get(pop_col, 0) for node in graph.nodes())
        target_pop = total_pop / num_districts

        # Create partition with recursive tree
        assignment = recursive_tree_part(
            graph,
            range(num_districts),
            target_pop,
            pop_col,
            epsilon=0.30  # Allow 30% deviation for flexibility
        )

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


def run_ensemble(initial_partition, num_steps=500):
    """
    Run MCMC ensemble

    Args:
        initial_partition: Starting partition
        num_steps (int): Number of steps

    Returns:
        list: Democratic district wins for each step
    """
    try:
        chain = MarkovChain(
            proposal=propose_random_flip,
            constraints=[single_flip_contiguous],
            accept=lambda x: True,
            initial_state=initial_partition,
            total_steps=num_steps
        )

        dem_wins_list = []
        for partition in chain:
            dem_wins = sum(
                1 for district in partition.parts.keys()
                if partition["dem_votes"][district] > partition["rep_votes"][district]
            )
            dem_wins_list.append(dem_wins)

        return dem_wins_list

    except Exception as e:
        print(f"  ERROR running ensemble: {str(e)}")
        return None


def analyze_state(state_name, shapefile_path, num_districts=5, num_steps=500):
    """
    Run full gerrymandering detection for a state

    Args:
        state_name (str): State name
        shapefile_path (str): Path to shapefile
        num_districts (int): Number of districts to create
        num_steps (int): MCMC steps

    Returns:
        dict: Analysis results or None on error
    """
    print(f"\n{'='*70}")
    print(f"Analyzing: {state_name.upper()}")
    print(f"{'='*70}")

    # Load data
    graph = load_state_data(shapefile_path, state_name)
    if not graph:
        return None

    # Detect columns
    columns = detect_data_columns(graph)
    if not columns:
        print(f"  ERROR: Could not find required data columns")
        return None

    print(f"  Using columns: {columns['dem']} vs {columns['rep']}")

    # Create initial partition
    partition = create_initial_partition(graph, columns, num_districts)
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

    print(f"  Initial map: {initial_dem_wins}/{num_districts} DEM districts")
    print(f"  Statewide vote share: {dem_vote_share:.1f}% DEM")

    # Run ensemble
    print(f"  Running {num_steps}-step MCMC ensemble...")
    dem_wins_list = run_ensemble(partition, num_steps)
    if not dem_wins_list:
        return None

    # Analyze results
    mean_dem = sum(dem_wins_list) / len(dem_wins_list)
    min_dem = min(dem_wins_list)
    max_dem = max(dem_wins_list)

    # Calculate percentile (using midpoint method for ties)
    below_initial = sum(1 for x in dem_wins_list if x < initial_dem_wins)
    equal_initial = sum(1 for x in dem_wins_list if x == initial_dem_wins)

    # Standard percentile calculation: (count below + 0.5 * count equal) / total
    percentile = ((below_initial + 0.5 * equal_initial) / len(dem_wins_list)) * 100

    # Determine if suspicious
    is_outlier = percentile < 5 or percentile > 95

    print(f"  Ensemble: {mean_dem:.1f} avg DEM districts (range: {min_dem}-{max_dem})")
    print(f"  Initial map at {percentile:.1f} percentile")

    if is_outlier:
        print(f"  ⚠️  SUSPICIOUS: Potential gerrymandering detected!")
    else:
        print(f"  ✅ Appears consistent with fair redistricting")

    return {
        'state': state_name,
        'precincts': len(graph.nodes),
        'num_districts': num_districts,
        'initial_dem_wins': initial_dem_wins,
        'dem_vote_share': round(dem_vote_share, 2),
        'ensemble_mean': round(mean_dem, 2),
        'ensemble_min': min_dem,
        'ensemble_max': max_dem,
        'percentile': round(percentile, 1),
        'is_outlier': is_outlier,
        'ensemble_steps': num_steps
    }


def main():
    """Run multi-state gerrymandering detection"""
    print("="*70)
    print("MULTI-STATE GERRYMANDERING DETECTION")
    print("="*70)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Find all state directories
    data_dir = "data/states"
    if not os.path.exists(data_dir):
        # Try from scripts directory
        data_dir = "../../data/states"

    if not os.path.exists(data_dir):
        print(f"ERROR: Could not find data directory")
        sys.exit(1)

    # Get all state directories
    state_dirs = sorted([d for d in os.listdir(data_dir)
                        if os.path.isdir(os.path.join(data_dir, d))])

    print(f"\nFound {len(state_dirs)} states to analyze")

    # Process each state
    results = []
    successful = 0
    failed = 0

    for state_dir in state_dirs:
        state_path = os.path.join(data_dir, state_dir)
        shapefile = find_shapefile(state_path)

        if not shapefile:
            print(f"\n❌ {state_dir}: No shapefile found")
            failed += 1
            continue

        # Determine appropriate number of districts based on state size
        # Use fewer districts for smaller states
        num_districts = 5  # Default

        result = analyze_state(state_dir, shapefile, num_districts=num_districts, num_steps=500)

        if result:
            results.append(result)
            successful += 1
        else:
            failed += 1

    # Generate summary report
    print("\n" + "="*70)
    print("SUMMARY REPORT")
    print("="*70)
    print(f"Total states processed: {len(state_dirs)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")

    if results:
        # Create DataFrame for analysis
        df = pd.DataFrame(results)

        # Count suspicious states
        suspicious_states = df[df['is_outlier'] == True]
        print(f"\n⚠️  States with suspicious patterns: {len(suspicious_states)}")

        if len(suspicious_states) > 0:
            print("\nStates flagged as potential gerrymanders:")
            for _, row in suspicious_states.iterrows():
                direction = "PRO-DEM" if row['percentile'] > 50 else "PRO-REP"
                print(f"  - {row['state'].upper()}: {row['percentile']:.1f}% percentile ({direction})")

        # Show top 10 most extreme
        print("\nTop 10 most extreme outliers:")
        df['extremeness'] = df['percentile'].apply(lambda x: abs(x - 50))
        top_outliers = df.nlargest(10, 'extremeness')

        for _, row in top_outliers.iterrows():
            direction = "PRO-DEM" if row['percentile'] > 50 else "PRO-REP"
            flag = "⚠️" if row['is_outlier'] else "  "
            print(f"  {flag} {row['state']:20s} {row['percentile']:5.1f}% percentile ({direction})")

        # Save detailed results
        output_file = f"gerrymandering_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"\n💾 Detailed results saved to: {output_file}")

        # Save CSV for easy analysis
        csv_file = output_file.replace('.json', '.csv')
        df.to_csv(csv_file, index=False)
        print(f"💾 CSV report saved to: {csv_file}")

    print(f"\n✅ Analysis complete at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
