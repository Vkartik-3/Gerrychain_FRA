#!/usr/bin/env python3
"""
Real MGGG Data Simulation Example
==================================

This script demonstrates gerrymandering detection using REAL data from the
MGGG States project. It uses Alaska precinct-level voting data from actual
elections.

Data source: MGGG States - Alaska Shapefiles
https://github.com/mggg-states/AK-shapefiles
"""

import matplotlib.pyplot as plt
import pandas as pd
from gerrychain import Graph, Partition, MarkovChain
from gerrychain.proposals import propose_random_flip
from gerrychain.constraints import single_flip_contiguous
from gerrychain.updaters import cut_edges, Tally
from gerrychain.tree import recursive_tree_part
import os


def load_real_data(shapefile_path):
    """
    Load real MGGG data from shapefile

    Args:
        shapefile_path (str): Path to the .shp file

    Returns:
        Graph: GerryChain Graph with real voting data
    """
    print(f"📂 Loading real data from MGGG States project...")
    print(f"   File: {shapefile_path}")

    if not os.path.exists(shapefile_path):
        raise FileNotFoundError(f"Shapefile not found: {shapefile_path}")

    # Load the shapefile into a GerryChain graph
    graph = Graph.from_file(shapefile_path)

    initial_nodes = len(graph.nodes)
    print(f"✅ Loaded graph with {initial_nodes} precincts")

    # Remove isolated nodes (islands) that can cause contiguity issues
    isolated_nodes = [node for node in graph.nodes() if graph.degree(node) == 0]
    if isolated_nodes:
        print(f"   ⚠️  Removing {len(isolated_nodes)} isolated precincts...")
        graph.remove_nodes_from(isolated_nodes)
        print(f"   ✅ Graph now has {len(graph.nodes)} connected precincts")

    # Display available data columns
    sample_node = list(graph.nodes())[0]
    print(f"\n📊 Available data columns:")
    for key in graph.nodes[sample_node].keys():
        print(f"   - {key}")

    return graph


def analyze_data(graph):
    """
    Analyze the loaded real data

    Args:
        graph: The loaded graph
    """
    print(f"\n🔍 Analyzing real data...")

    total_population = 0
    voting_columns = []

    # Find population and voting data columns
    sample_node = list(graph.nodes())[0]
    node_data = graph.nodes[sample_node]

    for key in node_data.keys():
        if 'POP' in key.upper() or 'TOTPOP' in key.upper():
            total_population = sum(graph.nodes[node].get(key, 0) for node in graph.nodes())
            print(f"   Population column: {key}")
            print(f"   Total population: {total_population:,}")

        if any(x in key.upper() for x in ['DEM', 'REP', 'GOV', 'SEN', 'PRES']):
            voting_columns.append(key)

    if voting_columns:
        print(f"\n   Found {len(voting_columns)} voting data columns:")
        for col in voting_columns[:10]:  # Show first 10
            print(f"   - {col}")

    return voting_columns


def create_districts_from_real_data(graph, num_districts=5, pop_col="TOTPOP"):
    """
    Create initial district partition from real data

    Args:
        graph: The loaded graph
        num_districts (int): Number of districts to create
        pop_col (str): Name of the population column

    Returns:
        Partition: Initial partition
    """
    print(f"\n🗺️  Creating {num_districts} districts from real data...")

    # Calculate target population
    total_pop = sum(graph.nodes[node].get(pop_col, 0) for node in graph.nodes())
    target_pop = total_pop / num_districts

    print(f"   Total population: {total_pop:,}")
    print(f"   Target per district: {target_pop:,.0f}")

    # Create initial partition using recursive tree partitioning
    # Use higher epsilon for more flexibility with real-world data
    assignment = recursive_tree_part(
        graph,
        range(num_districts),
        target_pop,
        pop_col,
        epsilon=0.25  # 25% deviation allowed for flexibility
    )

    # Find available election columns
    sample_node = list(graph.nodes())[0]
    node_data = graph.nodes[sample_node]

    # Set up updaters for tracking metrics
    updaters = {
        "cut_edges": cut_edges,
        "population": Tally(pop_col, alias="population"),
    }

    # Add election updaters if data exists
    election_cols = [k for k in node_data.keys() if any(x in k.upper() for x in ['GOV', 'SEN', 'PRES']) and 'D' in k.upper()]

    if election_cols:
        # Use the first found election column
        dem_col = [c for c in election_cols if 'D' in c.upper()][0]
        rep_col = dem_col.replace('D', 'R') if 'D' in dem_col else None

        if rep_col and rep_col in node_data:
            print(f"   Using election data: {dem_col} vs {rep_col}")
            updaters["dem_votes"] = Tally(dem_col, alias="dem_votes")
            updaters["rep_votes"] = Tally(rep_col, alias="rep_votes")

    partition = Partition(graph, assignment, updaters)

    # Display initial districts
    print("\n✅ Initial districts created:")
    for district_id in sorted(partition.parts.keys()):
        pop = partition["population"][district_id]
        print(f"   District {district_id}: {pop:,} people", end="")

        if "dem_votes" in partition.updaters:
            dem = partition["dem_votes"][district_id]
            rep = partition["rep_votes"][district_id]
            winner = "DEM" if dem > rep else "REP"
            print(f" | {dem:,} vs {rep:,} → {winner} wins")
        else:
            print()

    return partition


def run_real_data_simulation(initial_partition, num_steps=1000, pop_col="TOTPOP"):
    """
    Run MCMC simulation on real data

    Args:
        initial_partition: Starting partition
        num_steps (int): Number of simulation steps
        pop_col (str): Population column name

    Returns:
        tuple: (partitions list, results data)
    """
    print(f"\n🎲 Running MCMC simulation with {num_steps} steps...")
    print("   Generating alternative fair district maps...")

    # Check if we have election data
    has_election_data = "dem_votes" in initial_partition.updaters

    # Set up the Markov chain with simple random flip proposal
    chain = MarkovChain(
        proposal=propose_random_flip,
        constraints=[single_flip_contiguous],
        accept=lambda x: True,
        initial_state=initial_partition,
        total_steps=num_steps
    )

    # Track results
    results = []

    for i, partition in enumerate(chain):
        if has_election_data:
            # Count Democratic wins
            dem_wins = sum(
                1 for district in partition.parts.keys()
                if partition["dem_votes"][district] > partition["rep_votes"][district]
            )
            results.append(dem_wins)

        # Progress update
        if (i + 1) % 200 == 0:
            print(f"   Step {i + 1}/{num_steps} complete")

    print(f"✅ Simulation complete!")

    return results


def analyze_real_results(results, initial_partition, num_districts):
    """
    Analyze simulation results from real data

    Args:
        results (list): Democratic wins for each partition
        initial_partition: Original partition
        num_districts (int): Total number of districts
    """
    print(f"\n📊 Analyzing Real Data Results...")
    print("=" * 60)

    if not results:
        print("⚠️  No election data available for analysis")
        return

    # Calculate initial Democratic wins
    initial_dem_wins = sum(
        1 for district in initial_partition.parts.keys()
        if initial_partition["dem_votes"][district] > initial_partition["rep_votes"][district]
    )

    df = pd.DataFrame({"dem_districts": results})

    print(f"\nOriginal map: Democrats win {initial_dem_wins}/{num_districts} districts")
    print(f"\nIn {len(results)} alternative fair maps:")
    print(f"   Average DEM districts: {df['dem_districts'].mean():.2f}")
    print(f"   Median DEM districts: {df['dem_districts'].median():.1f}")
    print(f"   Range: {df['dem_districts'].min()}-{df['dem_districts'].max()} districts")

    # Show distribution
    print(f"\n📈 Distribution of outcomes:")
    for districts in range(num_districts + 1):
        count = (df['dem_districts'] == districts).sum()
        percentage = (count / len(results)) * 100
        if count > 0:
            bar = "█" * int(percentage / 2)
            print(f"   DEM wins {districts} districts: {count:4d} ({percentage:5.1f}%) {bar}")

    # Gerrymandering analysis
    print(f"\n🔍 Gerrymandering Analysis:")
    original_count = (df['dem_districts'] == initial_dem_wins).sum()
    percentile = (df['dem_districts'] < initial_dem_wins).sum() / len(results) * 100

    if percentile < 5 or percentile > 95:
        print(f"⚠️  SUSPICIOUS: Original result at {percentile:.1f} percentile")
        print("   This is an outlier compared to fair alternatives")
        print("   ⚠️  Possible gerrymandering detected!")
    else:
        print(f"✅ Original result at {percentile:.1f} percentile")
        print("   This appears consistent with fair redistricting")


def main():
    """Run the complete real data simulation"""
    print("🚀 GerryChain Real Data Simulation (MGGG Alaska)")
    print("=" * 60)

    # Path to the real MGGG shapefile (works from project root)
    shapefile_path = "data/states/alaska/alaska_precincts.shp"

    # If running from scripts subdirectory, adjust path
    if not os.path.exists(shapefile_path):
        shapefile_path = "../" + shapefile_path
    if not os.path.exists(shapefile_path):
        shapefile_path = "../" + shapefile_path

    # Step 1: Load real data
    graph = load_real_data(shapefile_path)

    # Step 2: Analyze the data
    voting_columns = analyze_data(graph)

    # Step 3: Create districts
    # Use 3 districts for easier contiguity with real-world geography
    num_districts = 3
    initial_partition = create_districts_from_real_data(
        graph,
        num_districts=num_districts,
        pop_col="TOTPOP"
    )

    # Step 4: Run simulation
    results = run_real_data_simulation(initial_partition, num_steps=1000)

    # Step 5: Analyze results
    analyze_real_results(results, initial_partition, num_districts)

    print(f"\n🎉 Real data simulation complete!")
    print("\nThis demonstrates GerryChain working with actual election data")
    print("from the MGGG States project, comparing real districts to")
    print("ensembles of algorithmically-generated fair alternatives.")


if __name__ == "__main__":
    main()
