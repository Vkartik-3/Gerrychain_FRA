#!/usr/bin/env python3
"""
Quick Demo: Multi-State Gerrymandering Detection
=================================================

This is a quick demo version that processes just a few states with fewer MCMC steps
to demonstrate the functionality quickly.
"""

import sys
sys.path.insert(0, '/Users/kartikvadhawana/Desktop/FRA/GerryChain')

from scripts.real_data.multi_state_detection import (
    find_shapefile, analyze_state
)
import os

def main():
    """Run quick demo on 3 states"""
    print("="*70)
    print("QUICK DEMO: Multi-State Gerrymandering Detection")
    print("="*70)
    print("Processing 3 states with 100 MCMC steps each for demonstration")
    print()

    # Test on 3 states with different characteristics
    test_states = [
        ('delaware', 3),
        ('connecticut', 5),
        ('iowa', 4)
    ]
    data_dir = "data/states"

    results = []
    failed_states = []

    for state_name, num_districts in test_states:
        state_path = os.path.join(data_dir, state_name)
        shapefile = find_shapefile(state_path)

        if not shapefile:
            print(f"\n❌ {state_name}: No shapefile found")
            failed_states.append((state_name, "No shapefile found"))
            continue

        try:
            # Run analysis with fewer steps for demo
            result = analyze_state(state_name, shapefile, num_districts=num_districts, num_steps=100)

            if result:
                results.append(result)
            else:
                failed_states.append((state_name, "Analysis returned None"))
        except Exception as e:
            print(f"\n❌ {state_name}: Unexpected error - {str(e)}")
            failed_states.append((state_name, f"Error: {str(e)}"))

    # Summary
    print("\n" + "="*70)
    print("DEMO SUMMARY")
    print("="*70)

    if results:
        print(f"\n✅ Successfully analyzed {len(results)} state(s):\n")
        for result in results:
            state = result['state']
            percentile = result['percentile']
            is_outlier = result['is_outlier']
            flag = "⚠️ " if is_outlier else "✅"

            print(f"{flag} {state.upper():20s} - {percentile:5.1f}% percentile", end="")
            if is_outlier:
                direction = "PRO-DEM" if percentile > 50 else "PRO-REP"
                print(f" ({direction}) - SUSPICIOUS!")
            else:
                print(" - Looks fair")

    if failed_states:
        print(f"\n❌ Failed to analyze {len(failed_states)} state(s):\n")
        for state_name, reason in failed_states:
            print(f"   {state_name.upper()}: {reason}")

    print("\n" + "="*70)
    print(f"✅ Quick demo complete! ({len(results)}/{len(test_states)} states succeeded)")
    print("="*70)
    print("\nThe full script (multi_state_detection.py) will process all 34 states")
    print("with 500 MCMC steps each. This takes longer but gives more accurate results.")


if __name__ == "__main__":
    main()
