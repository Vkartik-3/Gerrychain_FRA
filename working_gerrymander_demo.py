#!/usr/bin/env python3
"""
Working Gerrymandering Detection Demo
====================================

This creates two different valid district maps from the same city
and shows how GerryChain can detect which one is more fair.
"""

import networkx as nx
import pandas as pd
from gerrychain import Graph, Partition, MarkovChain
from gerrychain.proposals import propose_random_flip
from gerrychain.constraints import single_flip_contiguous
from gerrychain.updaters import cut_edges, Tally
from gerrychain.tree import recursive_tree_part
import random

def create_test_city():
    """
    Create a 6x6 city where Democrats have slight majority (52%)
    """
    print("🏙️  Creating 6x6 test city...")

    grid = nx.grid_2d_graph(6, 6)
    graph = Graph(grid)

    # Set random seed for reproducible city
    random.seed(12345)

    total_dem = 0
    total_rep = 0

    for node in graph.nodes():
        # Each block has 20 people
        population = 20
        graph.nodes[node]["population"] = population

        # Create realistic geographic voting patterns
        x, y = node

        # Democrats stronger in certain areas, Republicans in others
        if x < 2:  # Left side: Democratic
            dem_pct = 0.65 + random.uniform(-0.1, 0.1)
        elif x >= 4:  # Right side: Republican
            dem_pct = 0.35 + random.uniform(-0.1, 0.1)
        else:  # Middle: Competitive
            dem_pct = 0.50 + random.uniform(-0.15, 0.15)

        dem_pct = max(0.2, min(0.8, dem_pct))  # Keep reasonable bounds

        dem_votes = int(population * dem_pct)
        rep_votes = population - dem_votes

        graph.nodes[node]["dem_votes"] = dem_votes
        graph.nodes[node]["rep_votes"] = rep_votes

        total_dem += dem_votes
        total_rep += rep_votes

    dem_percentage = total_dem / (total_dem + total_rep) * 100

    print(f"✅ City created: 720 people, {total_dem} Dem ({dem_percentage:.1f}%), {total_rep} Rep")

    # Reset random seed
    random.seed()

    return graph

def create_districts_with_seed(graph, seed_value, description):
    """
    Create districts using recursive tree partitioning with a specific seed
    Different seeds can produce dramatically different results!
    """
    print(f"\n🗺️  Creating districts: {description}")

    # The key insight: different random seeds produce different district maps
    random.seed(seed_value)

    total_pop = sum(graph.nodes[node]["population"] for node in graph.nodes())
    target_pop = total_pop / 3  # 3 districts

    assignment = recursive_tree_part(
        graph,
        range(3),
        target_pop,
        "population",
        epsilon=0.2  # Allow 20% population deviation
    )

    updaters = {
        "cut_edges": cut_edges,
        "population": Tally("population", alias="population"),
        "dem_votes": Tally("dem_votes", alias="dem_votes"),
        "rep_votes": Tally("rep_votes", alias="rep_votes"),
    }

    partition = Partition(graph, assignment, updaters)

    # Count Democratic wins
    dem_wins = 0
    total_dem_votes = 0
    total_rep_votes = 0

    print(f"   Districts created:")
    for district_id in sorted(partition.parts.keys()):
        pop = partition["population"][district_id]
        dem = partition["dem_votes"][district_id]
        rep = partition["rep_votes"][district_id]
        winner = "DEM" if dem > rep else "REP"
        margin = abs(dem - rep)

        if dem > rep:
            dem_wins += 1

        total_dem_votes += dem
        total_rep_votes += rep

        print(f"      District {district_id}: {dem} vs {rep} → {winner} (margin: {margin})")

    citywide_dem_pct = total_dem_votes / (total_dem_votes + total_rep_votes) * 100
    district_dem_pct = dem_wins / 3 * 100

    print(f"   Result: Democrats win {dem_wins}/3 districts ({district_dem_pct:.0f}%)")
    print(f"   But Democrats got {citywide_dem_pct:.1f}% of votes citywide")

    if abs(district_dem_pct - citywide_dem_pct) > 15:
        print(f"   ⚠️  Large gap between vote share and district wins!")

    # Reset random seed
    random.seed()

    return partition, dem_wins

def test_map_fairness(partition, map_name, num_steps=1000):
    """
    Use MCMC to test if a district map is fair
    """
    print(f"\n🎲 Testing fairness of {map_name} with {num_steps} MCMC steps...")

    # Get original Democratic wins
    original_dem_wins = 0
    for district_id in partition.parts.keys():
        dem_votes = partition["dem_votes"][district_id]
        rep_votes = partition["rep_votes"][district_id]
        if dem_votes > rep_votes:
            original_dem_wins += 1

    # Run MCMC simulation
    chain = MarkovChain(
        proposal=propose_random_flip,
        constraints=[single_flip_contiguous],
        accept=lambda x: True,
        initial_state=partition,
        total_steps=num_steps
    )

    dem_wins_list = []

    for i, state in enumerate(chain):
        dem_wins = 0
        for district_id in state.parts.keys():
            dem_votes = state["dem_votes"][district_id]
            rep_votes = state["rep_votes"][district_id]
            if dem_votes > rep_votes:
                dem_wins += 1

        dem_wins_list.append(dem_wins)

        if (i + 1) % 250 == 0:
            print(f"      Step {i + 1}: Generated {i + 1} alternative maps")

    return dem_wins_list, original_dem_wins

def analyze_results(dem_wins_list, original_dem_wins, map_name):
    """
    Analyze MCMC results to determine if map is fair
    """
    print(f"\n📊 FAIRNESS ANALYSIS: {map_name}")
    print("=" * 45)

    df = pd.DataFrame({"dem_districts": dem_wins_list})

    avg_dem_wins = df['dem_districts'].mean()
    most_common = df['dem_districts'].mode().iloc[0]

    print(f"📍 {map_name}: Democrats win {original_dem_wins}/3 districts")
    print(f"\n📈 In {len(dem_wins_list)} alternative fair maps:")
    print(f"   Average Democratic wins: {avg_dem_wins:.2f}")
    print(f"   Most common result: {most_common} districts")
    print(f"   Range: {df['dem_districts'].min()} - {df['dem_districts'].max()}")

    print(f"\n📊 Distribution:")
    for districts in range(4):
        count = (df['dem_districts'] == districts).sum()
        percentage = (count / len(dem_wins_list)) * 100
        if count > 0:
            marker = " ← THIS MAP" if districts == original_dem_wins else ""
            print(f"   {districts} districts: {count:3d} times ({percentage:5.1f}%){marker}")

    # Calculate percentile
    original_count = (df['dem_districts'] == original_dem_wins).sum()
    original_percentile = (original_count / len(dem_wins_list)) * 100

    print(f"\n⚖️  VERDICT:")
    print(f"   This result occurs in {original_percentile:.1f}% of fair maps")

    if original_percentile < 5:
        verdict = "🚨 HIGHLY SUSPICIOUS - Likely gerrymandered!"
        suspicion_level = "HIGH"
    elif original_percentile < 10:
        verdict = "⚠️  SUSPICIOUS - Possibly unfair"
        suspicion_level = "MEDIUM"
    elif original_percentile < 25:
        verdict = "🤔 QUESTIONABLE - Worth investigating"
        suspicion_level = "LOW"
    else:
        verdict = "✅ APPEARS FAIR - Normal result"
        suspicion_level = "NONE"

    print(f"   {verdict}")

    return suspicion_level, original_percentile

def main():
    """
    Test two different district maps from the same city
    """
    print("🔍 GERRYMANDERING DETECTION DEMONSTRATION")
    print("=" * 60)

    # Create our test city
    graph = create_test_city()

    # Create two different district maps using different random seeds
    print("\n" + "=" * 60)
    map1, map1_dem_wins = create_districts_with_seed(graph, 42, "Map A (Seed 42)")
    map1_results, _ = test_map_fairness(map1, "Map A", num_steps=800)
    map1_suspicion, map1_pct = analyze_results(map1_results, map1_dem_wins, "Map A")

    print("\n" + "=" * 60)
    map2, map2_dem_wins = create_districts_with_seed(graph, 777, "Map B (Seed 777)")
    map2_results, _ = test_map_fairness(map2, "Map B", num_steps=800)
    map2_suspicion, map2_pct = analyze_results(map2_results, map2_dem_wins, "Map B")

    print("\n" + "=" * 60)
    print("🏆 FINAL COMPARISON")
    print("=" * 60)

    print(f"Map A: {map1_dem_wins}/3 Democratic districts ({map1_pct:.1f}% of fair maps)")
    print(f"Map B: {map2_dem_wins}/3 Democratic districts ({map2_pct:.1f}% of fair maps)")

    print(f"\nSuspicion levels:")
    print(f"   Map A: {map1_suspicion}")
    print(f"   Map B: {map2_suspicion}")

    if map1_suspicion != map2_suspicion:
        print(f"\n🎯 SUCCESS! GerryChain detected different fairness levels!")
        print(f"Even though both maps use the same city and voting data,")
        print(f"different ways of drawing districts can be more or less fair.")

        if map1_suspicion in ["HIGH", "MEDIUM"]:
            print(f"\n📋 Map A appears biased - this could be evidence in court!")
        if map2_suspicion in ["HIGH", "MEDIUM"]:
            print(f"\n📋 Map B appears biased - this could be evidence in court!")

    else:
        print(f"\n🤷 Both maps show similar fairness levels.")
        print(f"Sometimes different district maps produce similar outcomes.")

    print(f"\n💡 KEY INSIGHT:")
    print(f"GerryChain helps us quantify fairness by showing how often")
    print(f"a particular outcome occurs in thousands of alternative fair maps.")
    print(f"Courts can use this statistical evidence to identify gerrymandering!")

if __name__ == "__main__":
    main()