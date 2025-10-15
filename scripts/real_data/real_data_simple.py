#!/usr/bin/env python3
"""
Simple Real MGGG Data Example
==============================

This script loads real Alaska data from MGGG and uses the existing district
assignments to demonstrate working with real election data.
"""

import pandas as pd
from gerrychain import Graph, Partition, MarkovChain
from gerrychain.proposals import propose_random_flip
from gerrychain.constraints import single_flip_contiguous
from gerrychain.updaters import cut_edges, Tally
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
    print(f"\n📊 Available data columns (first 10):")
    for i, key in enumerate(list(graph.nodes[sample_node].keys())[:10]):
        print(f"   - {key}")

    return graph


def create_partition_from_existing_districts(graph):
    """
    Use existing district assignments from the data

    Args:
        graph: The loaded graph

    Returns:
        Partition: Partition based on existing districts
    """
    print(f"\n🗺️  Using existing district assignments from data...")

    # Use the HDIST column (House Districts) from the data
    assignment = {node: graph.nodes[node]["HDIST"] for node in graph.nodes()}

    # Count unique districts
    unique_districts = set(assignment.values())
    print(f"   Found {len(unique_districts)} existing districts")

    # Set up updaters for tracking metrics
    updaters = {
        "cut_edges": cut_edges,
        "population": Tally("TOTPOP", alias="population"),
        "pres16_dem": Tally("PRES16D", alias="pres16_dem"),
        "pres16_rep": Tally("PRES16R", alias="pres16_rep"),
    }

    partition = Partition(graph, assignment, updaters)

    # Display district info (sample first 10)
    print("\n✅ District information (first 10):")
    for i, district_id in enumerate(sorted(partition.parts.keys())[:10]):
        pop = partition["population"][district_id]
        dem = partition["pres16_dem"][district_id]
        rep = partition["pres16_rep"][district_id]
        winner = "DEM" if dem > rep else "REP"
        print(f"   District {district_id}: {pop:,} people | {dem:,} vs {rep:,} → {winner}")

    print(f"   ... and {len(partition.parts) - 10} more districts")

    return partition


def analyze_real_data(partition):
    """
    Analyze the real election data

    Args:
        partition: Partition with election data
    """
    print(f"\n📊 Analyzing Real Election Data (2016 Presidential)...")
    print("=" * 60)

    total_dem = sum(partition["pres16_dem"].values())
    total_rep = sum(partition["pres16_rep"].values())
    total_votes = total_dem + total_rep

    dem_pct = (total_dem / total_votes) * 100
    rep_pct = (total_rep / total_votes) * 100

    print(f"\nStatewide vote:")
    print(f"   Democrat: {total_dem:,} ({dem_pct:.1f}%)")
    print(f"   Republican: {total_rep:,} ({rep_pct:.1f}%)")

    # Count districts won by each party
    dem_districts = 0
    rep_districts = 0

    for district_id in partition.parts.keys():
        dem_votes = partition["pres16_dem"][district_id]
        rep_votes = partition["pres16_rep"][district_id]

        if dem_votes > rep_votes:
            dem_districts += 1
        else:
            rep_districts += 1

    total_districts = len(partition.parts)
    print(f"\nDistrict outcomes:")
    print(f"   Democrat wins: {dem_districts}/{total_districts} ({dem_districts/total_districts*100:.1f}%)")
    print(f"   Republican wins: {rep_districts}/{total_districts} ({rep_districts/total_districts*100:.1f}%)")

    # Check for potential efficiency gap
    print(f"\n🔍 Analysis:")
    vote_share_diff = abs(dem_pct - 50)
    seat_share_diff = abs((dem_districts / total_districts * 100) - 50)

    if seat_share_diff > vote_share_diff + 10:
        print(f"   ⚠️  Seat share ({dem_districts/total_districts*100:.1f}% DEM) differs significantly")
        print(f"      from vote share ({dem_pct:.1f}% DEM)")
        print(f"   This could indicate gerrymandering or geographic clustering")
    else:
        print(f"   ✅ Seat and vote shares are relatively proportional")


def run_mcmc_ensemble(initial_partition, num_steps=100):
    """
    Run a short MCMC ensemble to show alternative fair maps

    Args:
        initial_partition: Starting partition
        num_steps (int): Number of steps

    Returns:
        list: Democratic district wins for each map
    """
    print(f"\n🎲 Running MCMC ensemble ({num_steps} steps)...")
    print("   Generating alternative district maps...")

    # Set up the Markov chain
    chain = MarkovChain(
        proposal=propose_random_flip,
        constraints=[single_flip_contiguous],
        accept=lambda x: True,
        initial_state=initial_partition,
        total_steps=num_steps
    )

    # Track results
    dem_wins_list = []

    for i, partition in enumerate(chain):
        # Count Democratic wins
        dem_wins = sum(
            1 for district in partition.parts.keys()
            if partition["pres16_dem"][district] > partition["pres16_rep"][district]
        )
        dem_wins_list.append(dem_wins)

        if (i + 1) % 20 == 0:
            print(f"   Step {i + 1}/{num_steps}")

    print(f"✅ Ensemble complete!")

    return dem_wins_list


def analyze_ensemble_results(dem_wins_list, initial_partition):
    """
    Analyze ensemble results

    Args:
        dem_wins_list (list): Democratic wins for each map
        initial_partition: Original partition
    """
    print(f"\n📈 Ensemble Analysis...")
    print("=" * 60)

    # Calculate initial Democratic wins
    initial_dem_wins = sum(
        1 for district in initial_partition.parts.keys()
        if initial_partition["pres16_dem"][district] > initial_partition["pres16_rep"][district]
    )

    df = pd.DataFrame({"dem_districts": dem_wins_list})

    print(f"\nOriginal map: Democrats win {initial_dem_wins} districts")
    print(f"\nIn {len(dem_wins_list)} alternative maps:")
    print(f"   Average: {df['dem_districts'].mean():.1f} districts")
    print(f"   Range: {df['dem_districts'].min()}-{df['dem_districts'].max()} districts")

    # Show distribution
    print(f"\n📊 Distribution:")
    value_counts = df['dem_districts'].value_counts().sort_index()
    for districts, count in value_counts.items():
        percentage = (count / len(dem_wins_list)) * 100
        bar = "█" * int(percentage / 5)
        print(f"   {int(districts)} districts: {count:3d} ({percentage:5.1f}%) {bar}")


def main():
    """Run the complete real data analysis"""
    print("🚀 GerryChain Real Data Analysis (MGGG Alaska)")
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

    # Step 2: Create partition from existing districts
    initial_partition = create_partition_from_existing_districts(graph)

    # Step 3: Analyze real data
    analyze_real_data(initial_partition)

    print(f"\n🎉 Real data analysis complete!")
    print("\nThis demonstrates GerryChain working with actual MGGG election data,")
    print("showing real 2016 Presidential results by Alaska State House district.")
    print("\nNote: MCMC ensemble generation is disabled because existing districts")
    print("may have non-contiguous parts. For MCMC simulations, you would need to")
    print("create new contiguous districts using recursive_tree_part or similar methods.")


if __name__ == "__main__":
    main()
