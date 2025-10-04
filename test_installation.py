#!/usr/bin/env python3
"""
Test script to verify GerryChain installation and basic functionality
"""

import os
import sys

def test_basic_imports():
    """Test that we can import GerryChain components"""
    print("🔍 Testing basic imports...")

    try:
        import gerrychain
        print(f"✅ GerryChain version: {gerrychain.__version__}")
    except ImportError as e:
        print(f"❌ Failed to import gerrychain: {e}")
        return False

    try:
        from gerrychain import Graph, Partition, MarkovChain
        from gerrychain.proposals import propose_random_flip
        from gerrychain.constraints import single_flip_contiguous
        from gerrychain.updaters import cut_edges
        from gerrychain.tree import recursive_tree_part
        print("✅ Successfully imported core components")
    except ImportError as e:
        print(f"❌ Failed to import components: {e}")
        return False

    return True

def test_graph_creation():
    """Test creating a simple graph"""
    print("\n🔍 Testing graph creation...")

    try:
        import networkx as nx
        from gerrychain import Graph

        # Create a simple 4x4 grid
        grid = nx.grid_2d_graph(4, 4)
        graph = Graph(grid)

        # Add population data
        for node in graph.nodes():
            graph.nodes[node]["population"] = 1

        print(f"✅ Created graph with {len(graph.nodes)} nodes and {len(graph.edges)} edges")
        return True, graph
    except Exception as e:
        print(f"❌ Failed to create graph: {e}")
        return False, None

def test_partition_creation(graph):
    """Test creating a partition"""
    print("\n🔍 Testing partition creation...")

    try:
        from gerrychain import Partition
        from gerrychain.updaters import cut_edges
        from gerrychain.tree import recursive_tree_part

        # Create initial districts (divide into 4 districts of 4 nodes each)
        assignment = recursive_tree_part(graph, range(4), 4, "population", epsilon=0.1)
        partition = Partition(graph, assignment, {"cut_edges": cut_edges})

        print(f"✅ Created partition with {len(partition.parts)} districts")
        print(f"   District sizes: {[len(part) for part in partition.parts.values()]}")
        return True, partition
    except Exception as e:
        print(f"❌ Failed to create partition: {e}")
        return False, None

def test_environment():
    """Test environment setup"""
    print("\n🔍 Testing environment...")

    hash_seed = os.environ.get('PYTHONHASHSEED', 'Not Set')
    print(f"   PYTHONHASHSEED: {hash_seed}")

    if hash_seed == '0':
        print("✅ Reproducible environment properly configured")
        return True
    else:
        print("⚠️  PYTHONHASHSEED not set to 0 - results may not be reproducible")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing GerryChain Installation")
    print("=" * 50)

    # Test environment
    env_ok = test_environment()

    # Test imports
    import_ok = test_basic_imports()
    if not import_ok:
        print("\n❌ Installation test failed - imports not working")
        sys.exit(1)

    # Test graph creation
    graph_ok, graph = test_graph_creation()
    if not graph_ok:
        print("\n❌ Installation test failed - graph creation not working")
        sys.exit(1)

    # Test partition creation
    partition_ok, partition = test_partition_creation(graph)
    if not partition_ok:
        print("\n❌ Installation test failed - partition creation not working")
        sys.exit(1)

    print("\n🎉 All tests passed!")
    print("✅ GerryChain is properly installed and ready to use")

    if env_ok:
        print("✅ Environment is configured for reproducible results")
    else:
        print("⚠️  Remember to set PYTHONHASHSEED=0 for reproducible results")

    return True

if __name__ == "__main__":
    main()