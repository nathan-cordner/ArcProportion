from count_crossing import construct_adj_matrix
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
    print("====Testing count_graph_crossing====")
    print("Nodes:", node_order)
    from count_crossing import count_graph_crossings

    # Count crossings pre minimization
    crossings_pre: int = count_graph_crossings(
        construct_adj_matrix(node_order, arcs)
    )

    # Count crossings after minimization
    node_order = minimize_crossings(node_order, arcs)
    crossings_post: int = count_graph_crossings(
        construct_adj_matrix(node_order, arcs)
    )

    # Print result
    print(
        "Count of crossings in circular graph:\n"
        f"  - before minimization: {crossings_pre}\n"
        f"  - after minimization: {crossings_post}\n"
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
    print("====Testing count_node_crossing====")
    print("Nodes:", node_order)

    from functools import partial
    from count_crossing import count_node_crossings
    node_crossings = partial(
        count_node_crossings,
        construct_adj_matrix(node_order, arcs)
    )

    for index, interest_node in enumerate(node_order):
        crossings_pre: int = node_crossings(index)
        print(
            f"Count of crossings of edges with node \"{interest_node}\" in circular"
                f" graph: {crossings_pre}."
        )
    print()

# def test_permutator():
#     from .__init__ import permutator
#
#     foo = permutator(5, 2)
#
#     print(foo(1) == 3)
#
#     try: permutator(4, 5)
#     except ValueError: print("Function fails appropriately.")

def test_local_adjusting():
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
    print("Testing local_adjusting")
    print("Nodes:", node_order)

    from count_crossing import local_adjusting
    node_order = minimize_crossings(node_order, arcs)
    print("After AVSDF:", node_order)
    node_order = local_adjusting(node_order, arcs)
    print("After Postprocessing:", node_order)

if __name__ == "__main__":
    # test_graph_count_crossings()
    # test_node_count_crossings()
    # test_permutator()
    test_local_adjusting()
