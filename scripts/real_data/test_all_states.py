#!/usr/bin/env python3
"""
Quick diagnostic script to test all 34 states
Tests loading, column detection, and initial partition creation
Does NOT run full MCMC analysis (fast!)
"""

import os
import sys
from gerrychain import Graph
from gerrychain.tree import recursive_tree_part
from gerrychain.updaters import cut_edges, Tally
from gerrychain import Partition
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, '/Users/kartikvadhawana/Desktop/FRA/GerryChain')

def find_shapefile(state_dir):
    """Find shapefile in state directory"""
    state_configs = {
        'alabama': 'al_2020.shp', 'alaska': 'alaska_precincts.shp',
        'arizona': 'az_precincts.shp', 'california': 'ca_2020.shp',
        'colorado': 'co_2020.shp', 'connecticut': 'CT_precincts.shp',
        'delaware': 'DE_precincts.shp', 'florida': 'fl_2020.shp',
        'georgia': 'GA_precincts16.shp', 'hawaii': 'HI_precincts.shp',
        'illinois': None, 'indiana': 'Indiana.shp', 'iowa': 'IA_counties.shp',
        'louisiana': 'LA_1519.shp', 'maine': 'Maine.shp',
        'maryland': 'MD-precincts.shp', 'massachusetts': 'MA_precincts_12_16.shp',
        'michigan': 'mi16_results.shp', 'minnesota': 'mn_precincts16.shp',
        'nebraska': 'NE.shp', 'new-hampshire': 'NH.shp',
        'new-mexico': 'new_mexico_precincts.shp', 'new-york': 'ny_2020.shp',
        'north-carolina': 'NC_VTD.shp', 'ohio': 'oh_2020.shp',
        'oklahoma': 'OK_precincts.shp', 'oregon': 'OR_precincts.shp',
        'pennsylvania': 'PA.shp', 'puerto-rico': 'PR.shp',
        'rhode-island': 'RI_precincts.shp', 'utah': 'UT_precincts.shp',
        'vermont': 'VT_town_results.shp', 'washington': 'King_2016.shp',
        'wisconsin': 'WI_ltsb_corrected_final.shp',
    }

    state_name = os.path.basename(state_dir.rstrip('/'))
    if state_name in state_configs and state_configs[state_name]:
        shapefile = os.path.join(state_dir, state_configs[state_name])
        if os.path.exists(shapefile):
            return shapefile

    for root, _, files in os.walk(state_dir):
        if '__MACOSX' in root:
            continue
        for file in files:
            if file.endswith('.shp') and not file.startswith('.'):
                return os.path.join(root, file)
    return None

def detect_columns(graph):
    """Detect data columns"""
    if not graph.nodes:
        return None

    sample = list(graph.nodes())[0]
    cols = list(graph.nodes[sample].keys())
    result = {'population': None, 'dem': None, 'rep': None}

    # Population
    for col in cols:
        if any(x in col.upper() for x in ['TOTPOP', 'POP', 'VAP']):
            result['population'] = col
            break

    # Election - Biden/Trump
    biden = [c for c in cols if 'BID' in c.upper() or 'BIDEN' in c.upper()]
    trump = [c for c in cols if 'TRU' in c.upper() or 'TRUMP' in c.upper()]
    if biden and trump:
        result['dem'] = biden[0]
        result['rep'] = trump[0]
        return result if result['dem'] else None

    # Generic patterns
    for prefix in ['PRES', 'PRE', 'SEN', 'USS', 'GOV']:
        dem = [c for c in cols if prefix in c.upper() and 'D' in c.upper()]
        if dem:
            rep = None
            for var in [dem[0].replace('D', 'R'), dem[0].replace('d', 'r')]:
                if var in cols:
                    rep = var
                    break
            if rep:
                result['dem'] = dem[0]
                result['rep'] = rep
                return result if result['dem'] else None

    return None

def test_state(state_name, state_path):
    """Test a single state"""
    result = {'state': state_name, 'status': 'unknown', 'error': None}

    try:
        # Find shapefile
        shapefile = find_shapefile(state_path)
        if not shapefile:
            result['status'] = 'FAIL'
            result['error'] = 'No shapefile found'
            return result

        # Load graph
        graph = Graph.from_file(shapefile)
        isolated = [n for n in graph.nodes() if graph.degree(n) == 0]
        if isolated:
            graph.remove_nodes_from(isolated)

        result['precincts'] = len(graph.nodes)

        # Detect columns
        columns = detect_columns(graph)
        if not columns:
            result['status'] = 'FAIL'
            result['error'] = 'Cannot detect election columns'
            return result

        result['columns'] = f"{columns['dem']} vs {columns['rep']}"
        result['has_pop'] = columns['population'] is not None

        # Try creating partition
        pop_col = columns['population']
        dem_col = columns['dem']
        rep_col = columns['rep']

        # Clean data
        for node in graph.nodes():
            nd = graph.nodes[node]
            for col in [dem_col, rep_col]:
                try:
                    nd[col] = float(nd.get(col, 0))
                except:
                    nd[col] = 0

            if pop_col and pop_col in nd:
                try:
                    nd[pop_col] = float(nd.get(pop_col, 0))
                except:
                    nd[pop_col] = 0
            elif not pop_col:
                nd['synthetic_pop'] = nd.get(dem_col, 0) + nd.get(rep_col, 0)

        if not pop_col:
            pop_col = 'synthetic_pop'

        total_pop = sum(graph.nodes[n].get(pop_col, 0) for n in graph.nodes())
        num_districts = 5
        target_pop = total_pop / num_districts

        assignment = recursive_tree_part(graph, range(num_districts), target_pop, pop_col, epsilon=0.30)

        updaters = {
            "cut_edges": cut_edges,
            "population": Tally(pop_col),
            "dem_votes": Tally(dem_col),
            "rep_votes": Tally(rep_col),
        }
        partition = Partition(graph, assignment, updaters)

        # Check contiguity
        from gerrychain.constraints import contiguous
        result['contiguous'] = contiguous(partition)

        result['status'] = 'OK'
        return result

    except Exception as e:
        result['status'] = 'FAIL'
        result['error'] = str(e)[:100]
        return result

def main():
    data_dir = "data/states"
    if not os.path.exists(data_dir):
        print("ERROR: data/states not found")
        return

    states = sorted([d for d in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, d))])

    print(f"Testing {len(states)} states...\n")

    results = []
    for state in states:
        state_path = os.path.join(data_dir, state)
        print(f"Testing {state}...", end=' ')
        result = test_state(state, state_path)
        results.append(result)

        if result['status'] == 'OK':
            cont = '✓' if result['contiguous'] else '✗'
            pop = '✓' if result['has_pop'] else '✗'
            print(f"OK [prec:{result['precincts']}, pop:{pop}, cont:{cont}]")
        else:
            print(f"FAIL: {result['error']}")

    # Summary
    ok = [r for r in results if r['status'] == 'OK']
    fail = [r for r in results if r['status'] == 'FAIL']
    non_contig = [r for r in ok if not r['contiguous']]
    no_pop = [r for r in ok if not r['has_pop']]

    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    print(f"Total: {len(results)}")
    print(f"Success: {len(ok)}")
    print(f"Failed: {len(fail)}")
    print(f"Non-contiguous: {len(non_contig)}")
    print(f"No population: {len(no_pop)}")

    if fail:
        print(f"\nFailed states:")
        for r in fail:
            print(f"  - {r['state']}: {r['error']}")

    if non_contig:
        print(f"\nNon-contiguous states:")
        for r in non_contig:
            print(f"  - {r['state']}")

if __name__ == "__main__":
    main()
