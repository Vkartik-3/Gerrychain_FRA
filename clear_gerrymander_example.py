#!/usr/bin/env python3
"""
Clear Gerrymandering Example
===========================

This creates a scenario where we start with a clearly fair map,
then compare it to multiple alternatives to find one that's obviously biased.
"""

import networkx as nx
import pandas as pd
from gerrychain import Graph, Partition, MarkovChain
from gerrychain.proposals import propose_random_flip
from gerrychain.constraints import single_flip_contiguous
from gerrychain.updaters import cut_edges, Tally
from gerrychain.tree import recursive_tree_part
import random

def create_balanced_city():
    """
    Create a 6x6 city where Democrats should win about 50% in a fair system
    """
    print("🏙️  Creating 6x6 balanced city...")

    grid = nx.grid_2d_graph(6, 6)
    graph = Graph(grid)

    random.seed(2024)  # Fixed seed for reproducible city

    total_dem = 0
    total_rep = 0

    for node in graph.nodes():
        population = 20  # Each block: 20 people
        graph.nodes[node]["population"] = population

        x, y = node

        # Create a city where Democrats should win ~50% in fair districts
        # But with some geographic clustering (realistic)
        if x <= 1:  # Left edge: Strong Democratic
            dem_pct = 0.70 + random.uniform(-0.05, 0.05)
        elif x >= 4:  # Right edge: Strong Republican
            dem_pct = 0.30 + random.uniform(-0.05, 0.05)
        elif y <= 1 or y >= 4:  # Top/bottom: Lean Republican
            dem_pct = 0.40 + random.uniform(-0.10, 0.10)
        else:  # Center: Competitive
            dem_pct = 0.52 + random.uniform(-0.15, 0.15)

        dem_pct = max(0.15, min(0.85, dem_pct))

        dem_votes = int(population * dem_pct)
        rep_votes = population - dem_votes

        graph.nodes[node]["dem_votes"] = dem_votes
        graph.nodes[node]["rep_votes"] = rep_votes

        total_dem += dem_votes
        total_rep += rep_votes

    dem_percentage = total_dem / (total_dem + total_rep) * 100
    print(f"✅ Balanced city: {total_dem} Dem ({dem_percentage:.1f}%), {total_rep} Rep")

    random.seed()  # Reset seed
    return graph

def find_fair_and_biased_maps(graph, trials=10):
    """
    Try multiple random seeds to find both fair and biased district maps
    """
    print(f"\n🔍 Searching through {trials} different district maps...")

    maps_data = []

    for seed in range(trials):
        random.seed(seed)

        total_pop = sum(graph.nodes[node]["population"] for node in graph.nodes())
        target_pop = total_pop / 4  # 4 districts

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
            total_dem_votes = 0
            total_rep_votes = 0

            for district_id in partition.parts.keys():
                dem = partition["dem_votes"][district_id]
                rep = partition["rep_votes"][district_id]
                if dem > rep:
                    dem_wins += 1
                total_dem_votes += dem
                total_rep_votes += rep

            citywide_dem_pct = total_dem_votes / (total_dem_votes + total_rep_votes) * 100
            district_dem_pct = dem_wins / 4 * 100
            gap = abs(district_dem_pct - citywide_dem_pct)

            maps_data.append({
                'seed': seed,
                'partition': partition,
                'dem_wins': dem_wins,
                'citywide_dem_pct': citywide_dem_pct,
                'district_dem_pct': district_dem_pct,
                'gap': gap
            })

            print(f"   Seed {seed}: {dem_wins}/4 districts ({district_dem_pct:.0f}%), gap: {gap:.1f}%")

        except Exception as e:
            print(f"   Seed {seed}: Failed ({e})")
            continue

        random.seed()

    # Find the most fair and most biased maps
    maps_data.sort(key=lambda x: x['gap'])

    fair_map = maps_data[0]  # Smallest gap
    biased_map = maps_data[-1]  # Largest gap

    print(f"\n📊 Best and worst maps found:")
    print(f"   Most fair:  Seed {fair_map['seed']} - {fair_map['dem_wins']}/4 districts (gap: {fair_map['gap']:.1f}%)")
    print(f"   Most biased: Seed {biased_map['seed']} - {biased_map['dem_wins']}/4 districts (gap: {biased_map['gap']:.1f}%)")

    return fair_map, biased_map

def test_map_with_mcmc(partition, map_name, num_steps=1200):
    """
    Test a map using MCMC
    """
    print(f"\n🎲 Testing {map_name} with {num_steps} MCMC steps...")

    # Original Democratic wins
    original_dem_wins = 0
    for district_id in partition.parts.keys():
        dem_votes = partition["dem_votes"][district_id]
        rep_votes = partition["rep_votes"][district_id]
        if dem_votes > rep_votes:
            original_dem_wins += 1

    # MCMC chain
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
            print(f"      Generated {i + 1} alternative maps")

    return dem_wins_list, original_dem_wins

def detailed_analysis(dem_wins_list, original_dem_wins, map_name, citywide_dem_pct):
    """
    Detailed analysis with clear verdict
    """
    print(f"\n📊 DETAILED ANALYSIS: {map_name}")
    print("=" * 50)

    df = pd.DataFrame({"dem_districts": dem_wins_list})

    print(f"🏛️  Original Map Results:")
    print(f"   Democrats win {original_dem_wins} out of 4 districts ({original_dem_wins/4*100:.0f}%)")
    print(f"   Democrats got {citywide_dem_pct:.1f}% of votes citywide")
    print(f"   Representation gap: {abs(original_dem_wins/4*100 - citywide_dem_pct):.1f} percentage points")

    print(f"\n📈 Alternative Fair Maps Analysis:")
    print(f"   Analyzed {len(dem_wins_list)} alternative district maps")
    print(f"   Average Democratic districts: {df['dem_districts'].mean():.2f}")
    print(f"   Expected based on vote share: {citywide_dem_pct/100*4:.2f} districts")

    print(f"\n📊 Complete Distribution:")
    for districts in range(5):
        count = (df['dem_districts'] == districts).sum()
        percentage = (count / len(dem_wins_list)) * 100
        if count > 0:
            marker = " ← ACTUAL RESULT" if districts == original_dem_wins else ""
            print(f"   {districts} districts: {count:4d} maps ({percentage:5.1f}%){marker}")

    # Statistical analysis
    original_count = (df['dem_districts'] == original_dem_wins).sum()
    original_percentile = (original_count / len(dem_wins_list)) * 100

    # Calculate how extreme this result is
    expected_districts = citywide_dem_pct / 100 * 4
    deviation = abs(original_dem_wins - expected_districts)

    print(f"\n🔬 Statistical Evidence:")
    print(f"   This exact result occurs in {original_percentile:.1f}% of fair maps")
    print(f"   Result deviates by {deviation:.1f} districts from expected")

    # Clear verdict with legal implications
    print(f"\n⚖️  LEGAL VERDICT:")
    if original_percentile < 2:
        verdict = "🚨 CLEAR GERRYMANDERING"
        print(f"   {verdict} - Extremely strong evidence (< 2%)")
        print(f"   🏛️  This would likely succeed in court!")
        legal_strength = "VERY STRONG"
    elif original_percentile < 5:
        verdict = "🚨 LIKELY GERRYMANDERING"
        print(f"   {verdict} - Strong evidence (< 5%)")
        print(f"   🏛️  Good case for legal challenge")
        legal_strength = "STRONG"
    elif original_percentile < 10:
        verdict = "⚠️  SUSPICIOUS"
        print(f"   {verdict} - Moderate evidence (< 10%)")
        print(f"   🏛️  Worth investigating further")
        legal_strength = "MODERATE"
    elif original_percentile < 25:
        verdict = "🤔 QUESTIONABLE"
        print(f"   {verdict} - Weak evidence (< 25%)")
        legal_strength = "WEAK"
    else:
        verdict = "✅ APPEARS FAIR"
        print(f"   {verdict} - Normal result")
        legal_strength = "NONE"

    return legal_strength, original_percentile

def main():
    """
    Full demonstration of gerrymandering detection
    """
    print("🕵️  COMPREHENSIVE GERRYMANDERING DETECTION")
    print("=" * 70)

    # Create balanced city
    graph = create_balanced_city()

    # Find fair and biased district maps
    fair_map_data, biased_map_data = find_fair_and_biased_maps(graph, trials=15)

    # Test the fair map
    print("\n" + "=" * 70)
    print("TESTING THE 'FAIR' MAP")
    print("=" * 70)
    fair_results, _ = test_map_with_mcmc(fair_map_data['partition'], "Fair Map")
    fair_strength, fair_pct = detailed_analysis(
        fair_results,
        fair_map_data['dem_wins'],
        "Fair Map",
        fair_map_data['citywide_dem_pct']
    )

    # Test the biased map
    print("\n" + "=" * 70)
    print("TESTING THE 'BIASED' MAP")
    print("=" * 70)
    biased_results, _ = test_map_with_mcmc(biased_map_data['partition'], "Biased Map")
    biased_strength, biased_pct = detailed_analysis(
        biased_results,
        biased_map_data['dem_wins'],
        "Biased Map",
        biased_map_data['citywide_dem_pct']
    )

    # Final comparison
    print("\n" + "=" * 70)
    print("🏆 FINAL COURT-READY EVIDENCE")
    print("=" * 70)

    print(f"📋 CASE SUMMARY:")
    print(f"   Same city, same voters, different district boundaries")
    print(f"   Democrats represent {fair_map_data['citywide_dem_pct']:.1f}% of voters")
    print()
    print(f"   Fair Map:   {fair_map_data['dem_wins']}/4 districts ({fair_pct:.1f}% of fair alternatives)")
    print(f"   Biased Map: {biased_map_data['dem_wins']}/4 districts ({biased_pct:.1f}% of fair alternatives)")
    print()
    print(f"📊 EVIDENCE STRENGTH:")
    print(f"   Fair Map:   {fair_strength} evidence of bias")
    print(f"   Biased Map: {biased_strength} evidence of bias")

    if biased_strength in ["VERY STRONG", "STRONG"] and fair_strength in ["NONE", "WEAK"]:
        print(f"\n🎯 SMOKING GUN FOUND!")
        print(f"GerryChain successfully identified gerrymandering!")
        print(f"The biased map would be strong evidence in court.")
    elif biased_strength in ["VERY STRONG", "STRONG"]:
        print(f"\n🔍 GERRYMANDERING DETECTED!")
        print(f"The biased map shows clear statistical bias.")
    else:
        print(f"\n🤷 No clear gerrymandering found in this example.")
        print(f"Sometimes the difference isn't dramatic enough to detect.")

    print(f"\n💼 This demonstrates how mathematical analysis can provide")
    print(f"objective evidence for courts deciding redistricting cases!")

if __name__ == "__main__":
    main()