#!/usr/bin/env python3
"""
Gerrymandering Detection Example
===============================

This creates a realistic scenario where we start with a fair map,
then show how MCMC can detect if that map was actually gerrymandered.
"""

import networkx as nx
import pandas as pd
from gerrychain import Graph, Partition, MarkovChain
from gerrychain.proposals import propose_random_flip
from gerrychain.constraints import single_flip_contiguous
from gerrychain.updaters import cut_edges, Tally
from gerrychain.tree import recursive_tree_part
import random

def create_realistic_city(size=8):
    """
    Create a city with realistic geographic voting patterns
    """
    print(f"🏙️  Creating {size}x{size} city with geographic voting patterns...")

    grid = nx.grid_2d_graph(size, size)
    graph = Graph(grid)

    center = size // 2
    total_population = 0

    for node in graph.nodes():
        x, y = node
        distance_from_center = ((x - center) ** 2 + (y - center) ** 2) ** 0.5

        # Population density
        population = random.randint(12, 18)
        graph.nodes[node]["population"] = population
        total_population += population

        # Voting patterns based on geography
        # Center-left: urban core leans Democratic
        # Outer areas: suburbs lean Republican
        if distance_from_center < 2:
            # Urban core: 70% Democratic
            dem_pct = 0.70 + random.uniform(-0.15, 0.15)
        elif distance_from_center < 3:
            # Inner suburbs: 45% Democratic
            dem_pct = 0.45 + random.uniform(-0.20, 0.20)
        else:
            # Outer suburbs: 30% Democratic
            dem_pct = 0.30 + random.uniform(-0.15, 0.15)

        # Ensure valid percentages
        dem_pct = max(0.1, min(0.9, dem_pct))

        dem_votes = int(population * dem_pct)
        rep_votes = population - dem_votes

        graph.nodes[node]["dem_votes"] = dem_votes
        graph.nodes[node]["rep_votes"] = rep_votes

    total_dem = sum(graph.nodes[node]["dem_votes"] for node in graph.nodes())
    total_rep = sum(graph.nodes[node]["rep_votes"] for node in graph.nodes())

    print(f"✅ Created city: {total_population} people in {len(graph.nodes)} blocks")
    print(f"   Overall: {total_dem} Democratic ({total_dem/(total_dem+total_rep)*100:.1f}%), {total_rep} Republican")

    return graph

def create_initial_districts(graph, num_districts=4, biased=False):
    """
    Create initial districts - can be fair or biased depending on random seed
    """
    print(f"\n🗺️  Creating {num_districts} districts...")

    total_pop = sum(graph.nodes[node]["population"] for node in graph.nodes())
    target_pop = total_pop / num_districts

    # The key insight: different random seeds in recursive_tree_part
    # can produce different district maps, some more fair than others
    if biased:
        # Use a seed that tends to create less fair maps
        random.seed(999)
        print("   (Using parameters that may create biased districts)")
    else:
        # Use a seed that creates fairer maps
        random.seed(42)
        print("   (Using parameters for fair districts)")

    assignment = recursive_tree_part(
        graph,
        range(num_districts),
        target_pop,
        "population",
        epsilon=0.15
    )

    updaters = {
        "cut_edges": cut_edges,
        "population": Tally("population", alias="population"),
        "dem_votes": Tally("dem_votes", alias="dem_votes"),
        "rep_votes": Tally("rep_votes", alias="rep_votes"),
    }

    partition = Partition(graph, assignment, updaters)

    print("✅ Districts created:")
    dem_wins = 0
    total_dem_votes = 0
    total_rep_votes = 0

    for district_id in partition.parts.keys():
        pop = partition["population"][district_id]
        dem = partition["dem_votes"][district_id]
        rep = partition["rep_votes"][district_id]
        winner = "DEM" if dem > rep else "REP"
        margin = abs(dem - rep)

        if dem > rep:
            dem_wins += 1

        total_dem_votes += dem
        total_rep_votes += rep

        print(f"   District {district_id}: {pop} people, {dem} vs {rep} → {winner} (margin: {margin})")

    dem_pct = total_dem_votes / (total_dem_votes + total_rep_votes) * 100
    print(f"\n📊 Summary:")
    print(f"   Democrats win {dem_wins} out of {num_districts} districts ({dem_wins/num_districts*100:.1f}%)")
    print(f"   But Democrats got {dem_pct:.1f}% of total votes")

    # Reset random seed
    random.seed()

    return partition, dem_wins

def run_fairness_test(test_partition, num_steps=1500):
    """
    Test if the given partition is fair by comparing to MCMC alternatives
    """
    print(f"\n🎲 Running fairness test with {num_steps} MCMC steps...")
    print("   Generating alternative fair district maps...")

    # Count Democratic wins in the test map
    test_dem_wins = 0
    for district_id in test_partition.parts.keys():
        dem_votes = test_partition["dem_votes"][district_id]
        rep_votes = test_partition["rep_votes"][district_id]
        if dem_votes > rep_votes:
            test_dem_wins += 1

    # Run MCMC to generate alternatives
    chain = MarkovChain(
        proposal=propose_random_flip,
        constraints=[single_flip_contiguous],
        accept=lambda x: True,
        initial_state=test_partition,
        total_steps=num_steps
    )

    dem_wins_list = []

    for i, partition in enumerate(chain):
        dem_wins = 0
        for district_id in partition.parts.keys():
            dem_votes = partition["dem_votes"][district_id]
            rep_votes = partition["rep_votes"][district_id]
            if dem_votes > rep_votes:
                dem_wins += 1

        dem_wins_list.append(dem_wins)

        if (i + 1) % 300 == 0:
            print(f"   Step {i + 1}: Analyzed {i + 1} alternative maps")

    return dem_wins_list, test_dem_wins

def analyze_fairness(dem_wins_list, original_dem_wins, num_districts):
    """
    Determine if the original map was likely gerrymandered
    """
    print(f"\n📊 FAIRNESS ANALYSIS")
    print("=" * 50)

    df = pd.DataFrame({"dem_districts": dem_wins_list})

    print(f"🔍 Original map: Democrats win {original_dem_wins} out of {num_districts} districts")
    print(f"\nIn {len(dem_wins_list)} alternative fair maps:")
    print(f"   Average Democratic wins: {df['dem_districts'].mean():.2f}")
    print(f"   Most common result: {df['dem_districts'].mode().iloc[0]} districts")
    print(f"   Range: {df['dem_districts'].min()} - {df['dem_districts'].max()} districts")

    # Show distribution
    print(f"\n📈 Distribution of Democratic wins:")
    for districts in range(num_districts + 1):
        count = (df['dem_districts'] == districts).sum()
        percentage = (count / len(dem_wins_list)) * 100
        if count > 0:
            indicator = " ← Original result" if districts == original_dem_wins else ""
            print(f"   {districts} districts: {count:4d} times ({percentage:5.1f}%){indicator}")

    # Calculate percentile
    original_count = (df['dem_districts'] == original_dem_wins).sum()
    original_percentile = (original_count / len(dem_wins_list)) * 100

    # Verdict
    print(f"\n⚖️  VERDICT:")
    print(f"   The original result occurs in {original_percentile:.1f}% of fair maps")

    if original_percentile < 2.5:
        print("   🚨 HIGHLY SUSPICIOUS - Strong evidence of gerrymandering!")
        print("   🚨 This map is a statistical outlier (< 2.5%)")
        verdict = "GERRYMANDERED"
    elif original_percentile < 5:
        print("   ⚠️  SUSPICIOUS - Likely gerrymandering (< 5%)")
        print("   ⚠️  This result is quite rare in fair maps")
        verdict = "LIKELY GERRYMANDERED"
    elif original_percentile < 10:
        print("   🤔 QUESTIONABLE - Somewhat unusual (< 10%)")
        print("   🤔 Worth investigating further")
        verdict = "QUESTIONABLE"
    else:
        print("   ✅ FAIR - This appears to be a normal result")
        print("   ✅ No evidence of gerrymandering")
        verdict = "FAIR"

    return verdict

def main():
    """
    Run two scenarios: a fair map and a potentially biased map
    """
    print("🕵️  GERRYMANDERING DETECTION WITH GERRYCHAIN")
    print("=" * 60)

    # Create our city
    graph = create_realistic_city(size=8)

    print("\n" + "="*60)
    print("SCENARIO 1: Testing a 'Fair' District Map")
    print("="*60)

    # Test a fair map
    fair_partition, fair_dem_wins = create_initial_districts(graph, num_districts=4, biased=False)
    fair_results, _ = run_fairness_test(fair_partition, num_steps=1200)
    fair_verdict = analyze_fairness(fair_results, fair_dem_wins, num_districts=4)

    print("\n" + "="*60)
    print("SCENARIO 2: Testing a 'Suspicious' District Map")
    print("="*60)

    # Test a potentially biased map
    biased_partition, biased_dem_wins = create_initial_districts(graph, num_districts=4, biased=True)
    biased_results, _ = run_fairness_test(biased_partition, num_steps=1200)
    biased_verdict = analyze_fairness(biased_results, biased_dem_wins, num_districts=4)

    print("\n" + "="*60)
    print("FINAL COMPARISON")
    print("="*60)
    print(f"📊 'Fair' map verdict:      {fair_verdict}")
    print(f"📊 'Suspicious' map verdict: {biased_verdict}")

    print(f"\n🎯 KEY INSIGHT:")
    print("Even with the same city and voting patterns, different ways of")
    print("drawing districts can produce very different outcomes. GerryChain")
    print("helps us detect when a map produces unusually biased results!")

    if biased_verdict in ["GERRYMANDERED", "LIKELY GERRYMANDERED"] and fair_verdict == "FAIR":
        print("\n✅ SUCCESS: GerryChain successfully distinguished between")
        print("   fair and unfair district maps!")
    elif fair_verdict != "FAIR":
        print("\n🤔 Interesting: Even our 'fair' map shows some bias.")
        print("   This demonstrates how tricky fair redistricting can be!")
    else:
        print("\n🤷 Both maps appear fair. Sometimes random variation")
        print("   doesn't produce dramatically different outcomes.")

if __name__ == "__main__":
    main()