#!/usr/bin/env python3
"""
Simple GerryChain Simulation Example
====================================

This script demonstrates how to run a basic gerrymandering detection simulation
using GerryChain. It creates a simple grid city and runs MCMC to generate
alternative district maps for comparison.

Think of this like:
1. Creating a small city with a 8x8 grid (64 neighborhoods)
2. Dividing it into 4 voting districts (16 neighborhoods each)
3. Running 1000 different "fair" ways to draw the districts
4. Analyzing the results
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



def create_city_graph(size=8):
    """
    Create a simple city as a grid graph

    Args:
        size (int): Size of the grid (size x size)

    Returns:
        Graph: A GerryChain Graph representing our city
    """
    print(f"🏙️  Creating {size}x{size} city grid...")

    # Create a grid (like city blocks)
    grid = nx.grid_2d_graph(size, size)
    graph = Graph(grid)

    # Add population data (each block has some people)
    total_population = 0
    for node in graph.nodes():
        # Random population between 8-12 people per block
        pop = random.randint(8, 12)
        graph.nodes[node]["population"] = pop

        # Add some fake voting data for analysis
        # 60% vote for Party A, 40% for Party B (with some randomness)
        party_a_votes = int(pop * (0.6 + random.uniform(-0.2, 0.2)))
        party_b_votes = pop - party_a_votes

        graph.nodes[node]["party_a"] = max(0, party_a_votes)
        graph.nodes[node]["party_b"] = max(0, party_b_votes)

        total_population += pop

    print(f"✅ Created city with {len(graph.nodes)} blocks and {total_population} people")
    return graph

def create_initial_districts(graph, num_districts=4):
    """
    Create initial district assignment

    Args:
        graph: The city graph
        num_districts (int): Number of districts to create

    Returns:
        Partition: Initial district partition
    """
    print(f"🗺️  Dividing city into {num_districts} districts...")

    # Calculate target population per district
    total_pop = sum(graph.nodes[node]["population"] for node in graph.nodes())
    target_pop = total_pop / num_districts

    print(f"   Target population per district: {target_pop:.1f}")

    # Create districts using recursive tree partitioning
    assignment = recursive_tree_part(
        graph,
        range(num_districts),
        target_pop,
        "population",
        epsilon=0.1  # Allow 10% population deviation
    )

    # Set up updaters to track useful metrics
    updaters = {
        "cut_edges": cut_edges,
        "population": Tally("population", alias="population"),
        "party_a_votes": Tally("party_a", alias="party_a_votes"),
        "party_b_votes": Tally("party_b", alias="party_b_votes"),
    }

    partition = Partition(graph, assignment, updaters)

    # Print initial district info
    print("✅ Initial districts created:")
    for i, (district_id, pop) in enumerate(partition["population"].items()):
        a_votes = partition["party_a_votes"][district_id]
        b_votes = partition["party_b_votes"][district_id]
        winner = "Party A" if a_votes > b_votes else "Party B"
        print(f"   District {district_id}: {pop} people, {a_votes} vs {b_votes} votes → {winner} wins")

    return partition

def run_simulation(initial_partition, num_steps=1000):
    """
    Run the MCMC simulation to generate alternative district maps

    Args:
        initial_partition: Starting district map
        num_steps (int): Number of simulation steps

    Returns:
        list: List of all generated partitions
    """
    print(f"\n🎲 Running MCMC simulation for {num_steps} steps...")
    print("   This generates alternative 'fair' ways to draw districts")

    # Set up the Markov chain
    chain = MarkovChain(
        proposal=propose_random_flip,        # How to suggest boundary changes
        constraints=[single_flip_contiguous], # Keep districts connected
        accept=lambda x: True,               # Accept all valid proposals
        initial_state=initial_partition,     # Starting point
        total_steps=num_steps               # Number of alternatives to generate
    )

    # Run the simulation and collect results
    partitions = []
    party_a_wins = []

    for i, partition in enumerate(chain):
        partitions.append(partition)

        # Count how many districts Party A wins in this map
        a_wins = 0
        for district_id in partition.parts.keys():
            a_votes = partition["party_a_votes"][district_id]
            b_votes = partition["party_b_votes"][district_id]
            if a_votes > b_votes:
                a_wins += 1

        party_a_wins.append(a_wins)

        # Progress update
        if (i + 1) % 200 == 0:
            print(f"   Step {i + 1}: Generated {i + 1} alternative maps")

    print(f"✅ Simulation complete! Generated {len(partitions)} alternative district maps")

    return partitions, party_a_wins

def analyze_results(party_a_wins, initial_a_wins):
    """
    Analyze the simulation results to detect potential gerrymandering

    Args:
        party_a_wins (list): Number of districts Party A wins in each map
        initial_a_wins (int): Number of districts Party A wins in original map
    """
    print(f"\n📊 Analyzing Results...")
    print("=" * 50)

    # Calculate statistics
    df = pd.DataFrame({"party_a_districts": party_a_wins})

    print(f"Original map: Party A wins {initial_a_wins} out of 4 districts")
    print(f"\nIn {len(party_a_wins)} alternative fair maps:")
    print(f"   Average Party A districts: {df['party_a_districts'].mean():.2f}")
    print(f"   Most common result: {df['party_a_districts'].mode().iloc[0]} districts")
    print(f"   Range: {df['party_a_districts'].min()} - {df['party_a_districts'].max()} districts")

    # Count frequency of each outcome
    print(f"\n📈 Distribution of results:")
    for districts in range(5):  # 0-4 districts
        count = (df['party_a_districts'] == districts).sum()
        percentage = (count / len(party_a_wins)) * 100
        if count > 0:
            print(f"   Party A wins {districts} districts: {count} times ({percentage:.1f}%)")

    # Gerrymandering analysis
    print(f"\n🔍 Gerrymandering Analysis:")
    original_frequency = (df['party_a_districts'] == initial_a_wins).sum()
    original_percentile = (original_frequency / len(party_a_wins)) * 100

    if original_percentile < 5 or original_percentile > 95:
        print(f"⚠️  SUSPICIOUS: Original result occurs in only {original_percentile:.1f}% of fair maps!")
        print("   This could indicate gerrymandering")
    else:
        print(f"✅ Original result occurs in {original_percentile:.1f}% of fair maps")
        print("   This appears normal")

def main():
    """Run the complete simulation"""
    print("🚀 GerryChain Gerrymandering Detection Simulation")
    print("=" * 60)

    # Set random seed for reproducibility
    random.seed(42)

    # Step 1: Create our simulated city
    graph = create_city_graph(size=8)  # 8x8 = 64 blocks

    # Step 2: Create initial districts
    initial_partition = create_initial_districts(graph, num_districts=4)

    # Calculate initial Party A wins
    initial_a_wins = 0
    for district_id in initial_partition.parts.keys():
        a_votes = initial_partition["party_a_votes"][district_id]
        b_votes = initial_partition["party_b_votes"][district_id]
        if a_votes > b_votes:
            initial_a_wins += 1

    # Step 3: Run simulation
    partitions, party_a_wins = run_simulation(initial_partition, num_steps=1000)

    # Step 4: Analyze results
    analyze_results(party_a_wins, initial_a_wins)

    print(f"\n🎉 Simulation complete!")
    print("This demonstrates how GerryChain can detect gerrymandering by comparing")
    print("original district maps to ensembles of fair alternatives.")

if __name__ == "__main__":
    main()