#!/usr/bin/env python3
"""
Extreme Gerrymandering Detection Example
=======================================

This creates a scenario where we manually create an obviously
gerrymandered map and use GerryChain to prove it's unfair.
"""

import networkx as nx
import pandas as pd
from gerrychain import Graph, Partition, MarkovChain
from gerrychain.proposals import propose_random_flip
from gerrychain.constraints import single_flip_contiguous
from gerrychain.updaters import cut_edges, Tally
from gerrychain.tree import recursive_tree_part
import random

def create_competitive_city(size=6):
    """
    Create a city where Democrats have about 55% of votes
    In a fair system, they should win about 55% of districts
    """
    print(f"🏙️  Creating {size}x{size} competitive city...")

    grid = nx.grid_2d_graph(size, size)
    graph = Graph(grid)

    total_population = 0
    total_dem_votes = 0
    total_rep_votes = 0

    for node in graph.nodes():
        # Each block has 20 people
        population = 20
        graph.nodes[node]["population"] = population
        total_population += population

        # Make it competitive: Democrats get about 55% citywide
        # But with STRONG geographic clustering
        x, y = node

        # Create EXTREME geographic patterns for easier gerrymandering
        if x <= 1:
            # LEFT SIDE: Democratic strongholds: 80% Democratic
            dem_votes = int(population * 0.80)
        elif x >= 4:
            # RIGHT SIDE: Republican areas: 25% Democratic
            dem_votes = int(population * 0.25)
        else:
            # CENTER: Competitive swing: 55% Democratic
            dem_votes = int(population * 0.55)

        rep_votes = population - dem_votes

        graph.nodes[node]["dem_votes"] = dem_votes
        graph.nodes[node]["rep_votes"] = rep_votes

        total_dem_votes += dem_votes
        total_rep_votes += rep_votes

    dem_percentage = total_dem_votes / (total_dem_votes + total_rep_votes) * 100

    print(f"✅ Created competitive city:")
    print(f"   {total_population} people in {len(graph.nodes)} blocks")
    print(f"   {total_dem_votes} Democratic votes ({dem_percentage:.1f}%)")
    print(f"   {total_rep_votes} Republican votes ({100-dem_percentage:.1f}%)")

    return graph

def create_fair_districts(graph):
    """
    Create a fair 4-district map using simple geographic division
    """
    print(f"\n✅ Creating FAIR 4-district map (geographic regions)...")

    assignment = {}

    # Simple fair division: quadrants
    for node in graph.nodes():
        x, y = node
        if x < 3 and y < 3:
            assignment[node] = 0  # Bottom-left
        elif x < 3:
            assignment[node] = 1  # Top-left
        elif y < 3:
            assignment[node] = 2  # Bottom-right
        else:
            assignment[node] = 3  # Top-right

    updaters = {
        "cut_edges": cut_edges,
        "population": Tally("population", alias="population"),
        "dem_votes": Tally("dem_votes", alias="dem_votes"),
        "rep_votes": Tally("rep_votes", alias="rep_votes"),
    }

    partition = Partition(graph, assignment, updaters)

    print("Fair districts:")
    dem_wins = 0
    for district_id in sorted(partition.parts.keys()):
        pop = partition["population"][district_id]
        dem = partition["dem_votes"][district_id]
        rep = partition["rep_votes"][district_id]
        winner = "DEM" if dem > rep else "REP"
        margin = abs(dem - rep)

        if dem > rep:
            dem_wins += 1

        print(f"   District {district_id}: {dem} vs {rep} votes → {winner} (margin: {margin})")

    print(f"   Fair result: Democrats win {dem_wins} out of 4 districts")
    return partition, dem_wins

def create_gerrymandered_districts(graph, trials=50):
    """
    Create an obviously gerrymandered map by searching through random seeds
    Uses recursive_tree_part to ensure contiguity
    """
    print(f"\n🐍 Creating GERRYMANDERED 4-district map...")
    print(f"   Searching through {trials} algorithmic alternatives...")

    total_pop = sum(graph.nodes[node]["population"] for node in graph.nodes())
    target_pop = total_pop / 4  # 4 districts

    # Calculate citywide Democratic vote share
    total_dem = sum(graph.nodes[node]["dem_votes"] for node in graph.nodes())
    total_rep = sum(graph.nodes[node]["rep_votes"] for node in graph.nodes())
    citywide_dem_pct = total_dem / (total_dem + total_rep) * 100

    maps_data = []

    for seed in range(trials):
        random.seed(seed)

        try:
            assignment = recursive_tree_part(
                graph,
                range(4),
                target_pop,
                "population",
                epsilon=0.25
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
            for district_id in partition.parts.keys():
                dem = partition["dem_votes"][district_id]
                rep = partition["rep_votes"][district_id]
                if dem > rep:
                    dem_wins += 1

            district_dem_pct = dem_wins / 4 * 100
            gap = abs(district_dem_pct - citywide_dem_pct)

            maps_data.append({
                'seed': seed,
                'partition': partition,
                'dem_wins': dem_wins,
                'gap': gap
            })

        except Exception:
            continue

        random.seed()

    # Find the most biased map (largest gap favoring Republicans)
    # We want to MINIMIZE Democrat wins to show packing/cracking
    maps_data.sort(key=lambda x: x['dem_wins'])
    gerrymander_map = maps_data[0]  # Fewest Democratic wins

    partition = gerrymander_map['partition']
    dem_wins = gerrymander_map['dem_wins']

    print(f"   Selected seed {gerrymander_map['seed']} with maximum bias")
    print("Gerrymandered districts:")
    for district_id in sorted(partition.parts.keys()):
        pop = partition["population"][district_id]
        dem = partition["dem_votes"][district_id]
        rep = partition["rep_votes"][district_id]
        winner = "DEM" if dem > rep else "REP"
        margin = abs(dem - rep)

        print(f"   District {district_id}: {dem} vs {rep} votes → {winner} (margin: {margin})")

    print(f"   Gerrymandered result: Democrats win {dem_wins} out of 4 districts")
    print(f"   (Even though Democrats have {citywide_dem_pct:.1f}% citywide!)")

    return partition, dem_wins

def test_with_mcmc(partition, map_type, num_steps=1500):
    """
    Test a district map using MCMC to see if it's fair
    """
    print(f"\n🎲 Testing {map_type} map with {num_steps} MCMC steps...")

    # Count Democratic wins in original
    original_dem_wins = 0
    for district_id in partition.parts.keys():
        dem_votes = partition["dem_votes"][district_id]
        rep_votes = partition["rep_votes"][district_id]
        if dem_votes > rep_votes:
            original_dem_wins += 1

    # Run MCMC
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

        if (i + 1) % 300 == 0:
            print(f"   Step {i + 1}: Analyzed {i + 1} alternative maps")

    return dem_wins_list, original_dem_wins

def analyze_map_fairness(dem_wins_list, original_dem_wins, map_type):
    """
    Analyze if a map is fair based on MCMC results
    """
    print(f"\n📊 ANALYSIS: {map_type} Map")
    print("=" * 40)

    df = pd.DataFrame({"dem_districts": dem_wins_list})

    print(f"Original map: Democrats win {original_dem_wins} out of 3 districts")
    print(f"\nIn {len(dem_wins_list)} alternative maps:")
    print(f"   Average Democratic wins: {df['dem_districts'].mean():.2f}")
    print(f"   Most common result: {df['dem_districts'].mode().iloc[0]} districts")

    # Show full distribution
    print(f"\nDistribution:")
    for districts in range(4):
        count = (df['dem_districts'] == districts).sum()
        percentage = (count / len(dem_wins_list)) * 100
        indicator = " ← Original" if districts == original_dem_wins else ""
        print(f"   {districts} districts: {count:4d} times ({percentage:5.1f}%){indicator}")

    # Calculate how unusual the original result is
    original_count = (df['dem_districts'] == original_dem_wins).sum()
    original_percentile = (original_count / len(dem_wins_list)) * 100

    print(f"\n🔍 VERDICT:")
    if original_percentile < 5:
        print(f"   🚨 GERRYMANDERED! ({original_percentile:.1f}% of fair maps)")
        print(f"   This result is extremely rare in fair maps")
        return "GERRYMANDERED"
    elif original_percentile < 10:
        print(f"   ⚠️  SUSPICIOUS ({original_percentile:.1f}% of fair maps)")
        return "SUSPICIOUS"
    else:
        print(f"   ✅ FAIR ({original_percentile:.1f}% of fair maps)")
        return "FAIR"

def main():
    """
    Compare fair vs gerrymandered maps
    """
    print("🕵️  EXTREME GERRYMANDERING DETECTION")
    print("=" * 50)

    # Create our competitive city
    graph = create_competitive_city(size=6)

    # Test fair map
    fair_partition, fair_dem_wins = create_fair_districts(graph)
    fair_mcmc_results, _ = test_with_mcmc(fair_partition, "FAIR", num_steps=2500)
    fair_verdict = analyze_map_fairness(fair_mcmc_results, fair_dem_wins, "FAIR")

    # Test gerrymandered map
    gerrymander_partition, gerrymander_dem_wins = create_gerrymandered_districts(graph)
    gerrymander_mcmc_results, _ = test_with_mcmc(gerrymander_partition, "GERRYMANDERED", num_steps=2500)
    gerrymander_verdict = analyze_map_fairness(gerrymander_mcmc_results, gerrymander_dem_wins, "GERRYMANDERED")

    # Final comparison
    print(f"\n🏆 FINAL RESULTS")
    print("=" * 50)
    print(f"Fair map verdict:        {fair_verdict}")
    print(f"Gerrymandered map verdict: {gerrymander_verdict}")

    if gerrymander_verdict == "GERRYMANDERED" and fair_verdict == "FAIR":
        print(f"\n🎯 SUCCESS! GerryChain successfully detected gerrymandering!")
        print(f"The gerrymandered map produces results that are statistically")
        print(f"extremely unlikely in fair redistricting processes.")
    elif gerrymander_verdict == "GERRYMANDERED":
        print(f"\n🔍 GerryChain detected the gerrymandered map!")
        print(f"This shows how statistical analysis can provide evidence of bias.")
    else:
        print(f"\n🤔 The gerrymandering wasn't extreme enough to detect easily.")
        print(f"Real-world gerrymandering is often more subtle.")

    print(f"\nThis demonstrates how GerryChain provides mathematical proof")
    print(f"that can be used in court to challenge unfair district maps!")

if __name__ == "__main__":
    main()