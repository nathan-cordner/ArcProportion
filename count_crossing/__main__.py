from .__init__ import count_graph_crossings, count_node_crossings
from arc_crossing import minimize_crossings

"""
# Counting Crossing Algorithm (and other utilities)
Author: Carlos Rubio

## Notes:

- For now, I decided to follow Dr. C.'s design pattern and have the counting
algorithm generate it's own adjacency list. It was proposed that the data
transformation be abstracted out of the functions, but in order to keep that
avoid irregularities in the API, I decided to keep the design unified.

- Interstingly, I found using an adjacency matrix more useful for the Crossing
Counting algorithm: it was easier to keep track of which pairs of edges
had been visited.

- The postprocessing phase (local adjusting) requires to count the number of
crossings on the incident edges of a node, not the sum total of crossings. Such
algorithm also requires the ASVDF, since it assumes that the adjacency matrix
representation of the graph organizes the rows in decreasing node degree order.

A draft for the implementation of a node crossing counting algorithm can be
found in the 'count_node_crossing'.
"""

# NOTE: Currently, this module is demoing the algorithms, not testing them.
# TODO:
#   [ ] Use a testing module/package (pytest or unittest)

def test_graph_count_crossings():
    """Test graph counting algorithm."""

    # Create graph:
    node_order =  ["Amina", "Diego", "Liam", "Mei", "Zanele"]
    arcs = [
        ("Amina", "Liam"),
        ("Diego", "Zanele"),
        ("Amina", "Mei"),
        ("Mei", "Zanele"),
        ("Liam", "Zanele"),
        ("Diego", "Mei"),
        ("Amina", "Zanele"),
    ]
    print("Nodes:", node_order)

    # Count crossings pre minimization
    crossings_pre: int = count_graph_crossings(node_order, arcs)

    # Count crossings after minimization
    node_order = minimize_crossings(node_order, arcs)
    crossings_post: int = count_graph_crossings(node_order, arcs)

    # Print result
    print(
        "Count of crossings in circular graph:\n"
        f"  - before minimization: {crossings_pre}\n"
        f"  - after minimization: {crossings_post}"
    )

def test_node_count_crossings():
    """Test node counting algorithm."""
    # Create graph:
    node_order =  ["Amina", "Diego", "Liam", "Mei", "Zanele"]
    arcs = [
        ("Amina", "Liam"),
        ("Diego", "Zanele"),
        ("Amina", "Mei"),
        ("Mei", "Zanele"),
        ("Liam", "Zanele"),
        ("Diego", "Mei"),
        ("Amina", "Zanele"),
    ]
    print("Nodes:", node_order)

    for interest_node in node_order:
        crossings_pre: int = count_node_crossings(interest_node, node_order, arcs)
        print(
            f"Count of crossings of edges with node \"{interest_node}\" in circular"
                f" graph: {crossings_pre}."
        )

def test_permutator():
    from .algorithms import permutator

    foo = permutator(5, 2)

    print(foo(1) == 3)

    try: permutator(4, 5)
    except ValueError: print("Function fails appropriately.")

if __name__ == "__main__":
    # test_graph_count_crossings()
    test_node_count_crossings()
    # test_permutator()
