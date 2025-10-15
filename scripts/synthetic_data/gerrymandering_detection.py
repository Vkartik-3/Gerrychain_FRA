#!/usr/bin/env python3
"""
Gerrymandering Detection Example
===============================

This script demonstrates how GerryChain can detect gerrymandering by:
1. Creating a fair initial map
2. Intentionally gerrymandering it
3. Using MCMC to show the gerrymandered map is an outlier

Think of this as creating evidence for a court case!
"""

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
from gerrychain import Graph, Partition, MarkovChain
from gerrychain.proposals import propose_random_flip
from gerrychain.constraints import single_flip_contiguous
from gerrychain.updaters import cut_edges, Tally
from gerrychain.tree import recursive_tree_part
import random

def create_polarized_city(size=10):
    """
    Create a city where voters are geographically clustered by party
    (like many real cities - Democrats in urban core, Republicans in suburbs)

    Args:
        size (int): Size of the grid

    Returns:
        Graph: City with realistic voter clustering
    """
    print(f"🏙️  Creating {size}x{size} polarized city...")

    grid = nx.grid_2d_graph(size, size)
    graph = Graph(grid)

    center = size // 2
    total_population = 0

    for node in graph.nodes():
        x, y = node
        # Distance from city center
        distance_from_center = ((x - center) ** 2 + (y - center) ** 2) ** 0.5

        # Population: more dense in center
        if distance_from_center < 2:
            population = random.randint(15, 20)  # Dense urban core
        elif distance_from_center < 4:
            population = random.randint(10, 15)  # Suburbs
        else:
            population = random.randint(5, 10)   # Rural areas

        graph.nodes[node]["population"] = population
        total_population += population

        # Voting patterns: Democrats cluster in center, Republicans in outer areas
        if distance_from_center < 2.5:
            # Urban core: 80% Democrat, 20% Republican
            dem_votes = int(population * (0.8 + random.uniform(-0.1, 0.1)))
        elif distance_from_center < 4:
            # Suburbs: 40% Democrat, 60% Republican
            dem_votes = int(population * (0.4 + random.uniform(-0.15, 0.15)))
        else:
            # Rural: 20% Democrat, 80% Republican
            dem_votes = int(population * (0.2 + random.uniform(-0.1, 0.1)))

        rep_votes = population - dem_votes

        # Ensure non-negative votes
        graph.nodes[node]["dem_votes"] = max(0, dem_votes)
        graph.nodes[node]["rep_votes"] = max(0, rep_votes)

    print(f"✅ Created polarized city: {total_population} people in {len(graph.nodes)} blocks")

    # Show overall vote totals
    total_dem = sum(graph.nodes[node]["dem_votes"] for node in graph.nodes())
    total_rep = sum(graph.nodes[node]["rep_votes"] for node in graph.nodes())
    print(f"   City-wide votes: {total_dem} Democratic, {total_rep} Republican")
    print(f"   Democratic percentage: {total_dem/(total_dem + total_rep)*100:.1f}%")

    return graph

def create_fair_districts(graph, num_districts=5):
    """
    Create a fair district map using recursive tree partitioning
    """
    print(f"\n🗺️  Creating {num_districts} FAIR districts...")

    total_pop = sum(graph.nodes[node]["population"] for node in graph.nodes())
    target_pop = total_pop / num_districts

    assignment = recursive_tree_part(
        graph,
        range(num_districts),
        target_pop,
        "population",
        epsilon=0.15  # Allow 15% population deviation
    )

    updaters = {
        "cut_edges": cut_edges,
        "population": Tally("population", alias="population"),
        "dem_votes": Tally("dem_votes", alias="dem_votes"),
        "rep_votes": Tally("rep_votes", alias="rep_votes"),
    }

    partition = Partition(graph, assignment, updaters)

    print("✅ Fair districts created:")
    dem_wins = 0
    for district_id in partition.parts.keys():
        pop = partition["population"][district_id]
        dem = partition["dem_votes"][district_id]
        rep = partition["rep_votes"][district_id]
        winner = "DEM" if dem > rep else "REP"
        if dem > rep:
            dem_wins += 1
        print(f"   District {district_id}: {pop} people, {dem} vs {rep} votes → {winner} wins")

    print(f"   FAIR RESULT: Democrats win {dem_wins} out of {num_districts} districts")
    return partition, dem_wins

def create_gerrymandered_districts(graph, num_districts=5):
    """
    Create an INTENTIONALLY gerrymandered map that favors Republicans
    Strategy: Pack Democrats into few districts, spread Republicans across many
    """
    print(f"\n🐍 Creating {num_districts} GERRYMANDERED districts (favoring Republicans)...")

    # Get all nodes with their voting patterns
    nodes_data = []
    for node in graph.nodes():
        dem_votes = graph.nodes[node]["dem_votes"]
        rep_votes = graph.nodes[node]["rep_votes"]
        total_votes = dem_votes + rep_votes
        dem_percentage = dem_votes / total_votes if total_votes > 0 else 0

        nodes_data.append({
            'node': node,
            'population': graph.nodes[node]["population"],
            'dem_votes': dem_votes,
            'rep_votes': rep_votes,
            'dem_percentage': dem_percentage
        })

    # Sort by Democratic percentage (highest first)
    nodes_data.sort(key=lambda x: x['dem_percentage'], reverse=True)

    # GERRYMANDERING STRATEGY:
    # District 0: Pack as many Democrats as possible
    # Districts 1-4: Spread Republicans to create slight majorities

    assignment = {}
    district_populations = [0] * num_districts
    district_dem_votes = [0] * num_districts
    district_rep_votes = [0] * num_districts

    total_pop = sum(graph.nodes[node]["population"] for node in graph.nodes())
    target_pop = total_pop / num_districts

    # First, create one heavily Democratic district (packing)
    current_district = 0
    for node_data in nodes_data:
        if district_populations[current_district] < target_pop * 1.3:  # Allow overpacking
            node = node_data['node']
            assignment[node] = current_district
            district_populations[current_district] += node_data['population']
            district_dem_votes[current_district] += node_data['dem_votes']
            district_rep_votes[current_district] += node_data['rep_votes']
        else:
            break

    # Now assign remaining nodes to create Republican-leaning districts
    remaining_nodes = [n['node'] for n in nodes_data if n['node'] not in assignment]

    # Distribute remaining nodes to favor Republicans
    for i, node in enumerate(remaining_nodes):
        # Cycle through districts 1-4
        district = (i % (num_districts - 1)) + 1
        assignment[node] = district

        district_populations[district] += graph.nodes[node]["population"]
        district_dem_votes[district] += graph.nodes[node]["dem_votes"]
        district_rep_votes[district] += graph.nodes[node]["rep_votes"]

    # Create the gerrymandered partition
    updaters = {
        "cut_edges": cut_edges,
        "population": Tally("population", alias="population"),
        "dem_votes": Tally("dem_votes", alias="dem_votes"),
        "rep_votes": Tally("rep_votes", alias="rep_votes"),
    }

    partition = Partition(graph, assignment, updaters)

    print("🐍 GERRYMANDERED districts created:")
    dem_wins = 0
    for district_id in partition.parts.keys():
        pop = partition["population"][district_id]
        dem = partition["dem_votes"][district_id]
        rep = partition["rep_votes"][district_id]
        winner = "DEM" if dem > rep else "REP"
        if dem > rep:
            dem_wins += 1
        margin = abs(dem - rep)
        print(f"   District {district_id}: {pop} people, {dem} vs {rep} votes → {winner} wins (margin: {margin})")

    print(f"   GERRYMANDERED RESULT: Democrats win {dem_wins} out of {num_districts} districts")
    return partition, dem_wins

def run_mcmc_analysis(gerrymandered_partition, num_steps=2000):
    """
    Run MCMC to generate fair alternatives and analyze the gerrymandered map
    """
    print(f"\n🎲 Running MCMC analysis with {num_steps} steps...")
    print("   Generating fair alternative maps to compare against...")

    chain = MarkovChain(
        proposal=propose_random_flip,
        constraints=[single_flip_contiguous],
        accept=lambda x: True,
        initial_state=gerrymandered_partition,
        total_steps=num_steps
    )

    dem_wins_list = []

    for i, partition in enumerate(chain):
        # Count Democratic wins in this map
        dem_wins = 0
        for district_id in partition.parts.keys():
            dem_votes = partition["dem_votes"][district_id]
            rep_votes = partition["rep_votes"][district_id]
            if dem_votes > rep_votes:
                dem_wins += 1

        dem_wins_list.append(dem_wins)

        if (i + 1) % 400 == 0:
            print(f"   Step {i + 1}: Generated {i + 1} alternative maps")

    return dem_wins_list

def analyze_gerrymandering(dem_wins_list, original_dem_wins, fair_dem_wins):
    """
    Analyze results to prove gerrymandering occurred
    """
    print(f"\n📊 GERRYMANDERING DETECTION ANALYSIS")
    print("=" * 60)

    df = pd.DataFrame({"dem_districts": dem_wins_list})

    print(f"🐍 Gerrymandered map: Democrats win {original_dem_wins} districts")
    print(f"✅ Fair map (for comparison): Democrats win {fair_dem_wins} districts")
    print(f"\nIn {len(dem_wins_list)} fair alternative maps:")
    print(f"   Average Democratic districts: {df['dem_districts'].mean():.2f}")
    print(f"   Most common result: {df['dem_districts'].mode().iloc[0]} districts")
    print(f"   Range: {df['dem_districts'].min()} - {df['dem_districts'].max()} districts")

    # Distribution analysis
    print(f"\n📈 Distribution of Democratic wins in fair maps:")
    for districts in range(6):
        count = (df['dem_districts'] == districts).sum()
        percentage = (count / len(dem_wins_list)) * 100
        if count > 0:
            marker = "👈 GERRYMANDERED RESULT" if districts == original_dem_wins else ""
            print(f"   {districts} districts: {count} times ({percentage:.1f}%) {marker}")

    # Statistical significance test
    original_count = (df['dem_districts'] == original_dem_wins).sum()
    original_percentile = (original_count / len(dem_wins_list)) * 100

    print(f"\n🔍 SMOKING GUN EVIDENCE:")
    print(f"   The gerrymandered result ({original_dem_wins} Democratic districts)")
    print(f"   occurs in only {original_percentile:.1f}% of fair maps!")

    if original_percentile < 5:
        print(f"   🚨 HIGHLY SUSPICIOUS - less than 5% probability")
        print(f"   🚨 This is strong evidence of gerrymandering!")
    elif original_percentile < 10:
        print(f"   ⚠️  SUSPICIOUS - less than 10% probability")
        print(f"   ⚠️  Likely gerrymandering")
    else:
        print(f"   ✅ Normal result - no gerrymandering detected")

    # Compare to what we'd expect
    expected_dem_districts = df['dem_districts'].mean()
    print(f"\n📏 Expected vs Actual:")
    print(f"   Expected Democratic districts: {expected_dem_districts:.1f}")
    print(f"   Gerrymandered result: {original_dem_wins}")
    print(f"   Difference: {abs(expected_dem_districts - original_dem_wins):.1f} districts")

def main():
    """Run the complete gerrymandering detection demo"""
    print("🕵️  GERRYMANDERING DETECTION DEMONSTRATION")
    print("=" * 70)
    print("We'll create a fair map, then gerrymander it, then use MCMC to prove it!")

    random.seed(12345)  # For reproducible results

    # Step 1: Create a realistic polarized city
    graph = create_polarized_city(size=10)

    # Step 2: Create a fair baseline
    fair_partition, fair_dem_wins = create_fair_districts(graph, num_districts=5)

    # Step 3: Create gerrymandered version
    gerrymandered_partition, gerrymandered_dem_wins = create_gerrymandered_districts(graph, num_districts=5)

    # Step 4: Use MCMC to prove gerrymandering
    dem_wins_list = run_mcmc_analysis(gerrymandered_partition, num_steps=2000)

    # Step 5: Present the evidence
    analyze_gerrymandering(dem_wins_list, gerrymandered_dem_wins, fair_dem_wins)

    print(f"\n🎯 CONCLUSION:")
    print("This demonstrates how GerryChain can provide statistical evidence")
    print("that a district map was gerrymandered. In court, this would be")
    print("powerful evidence that the map violates fair representation!")

if __name__ == "__main__":
    main()