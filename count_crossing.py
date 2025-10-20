from warnings import warn

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


# Type Annotations (using type hinting as of Python 3.10)
NodeLabel = str
ArcTuple = tuple[NodeLabel, NodeLabel]
AdjacencyMatrix = list[list[int]]

def construct_adj_list(
    node_labels: list[NodeLabel] = [],
    arcs: list[ArcTuple] = []
) -> dict[NodeLabel, set[NodeLabel]]:
    """
    Returns the dictionary adjacency list representation of the graph
    ('node_labels', 'arcs'), where 'node_labels' represents the nodes, and
    'arcs' represents the edges.
    """

    # Allocate Dictionary structure
    adj_list = {}

    # Allocate Set structure for adjacency list
    for node in node_labels:
        adj_list[node] = set()

    # Fill adjacency lists
    for node_a, node_b in arcs:
        adj_list[node_a].add(node_b)
        adj_list[node_b].add(node_a)

    return adj_list

def construct_adj_matrix(
    node_labels: list[NodeLabel] = [],
    arcs: list[ArcTuple] = []
) -> AdjacencyMatrix:
    """
    Returns the 2D-list adjacency matrix representation of the graph
    ('node_labels', 'arcs'), where 'node_labels' represents the nodes, and
    'arcs' represents the edges.
    """

    def find_index(node):
        """
        Partial application of the list.index method to the
        node_labels list argument of the construct_adj_matrix
        function.

        It also implements a custom ValueError Exception message.
        """
        try:
            return node_labels.index(node)
        except ValueError:
            raise ValueError("Node not found in the graph.")

    adjacency_matrix = [[0 for _ in node_labels] for _ in node_labels]

    for node_a, node_b in arcs:
        adjacency_matrix[find_index(node_a)][find_index(node_b)] = 1
        adjacency_matrix[find_index(node_b)][find_index(node_a)] = 1

    return adjacency_matrix

def count_graph_crossings(
    node_labels: list[NodeLabel] = [],
    arcs: list[ArcTuple] = []
) -> int:
    """
    Returns the crossing count of the circular drawing of the graph
    ('node_labels', 'arcs'), where 'node_labels' represents the nodes, and
    'arcs' represets the edges.
    """
    adjacency_matrix = construct_adj_matrix(node_labels, arcs)
    # print(adjacency_matrix)

    node_size = len(node_labels)
    # 'node_size' represents the cardiality of the set of nodes in the
    # graph.

    return sum(
        adjacency_matrix[index_i][index_j] * adjacency_matrix[index_k][index_l]
        for index_i in range(node_size - 2)
        for index_j in range(index_i + 2, node_size - 1)
        for index_k in range(index_i + 1, index_j)
        for index_l in range(index_j + 1, node_size)
    )

def count_node_crossings(
    node: NodeLabel,
    node_labels: list[NodeLabel] = [],
    arcs: list[ArcTuple] = []
) -> int:
    # WARN: This algorithm hasn't been fully implemented, and it's output is
    # incorrect.
    warn("Unfinished implementation: this algorithm might not be correct.")
    """
    Returns the count of crossings on the incident edges of 'node' in the
    graph ('node_labels', 'arcs'), where 'node_labels' represents the nodes,
    and 'arcs' represets the edges.
    """
    if node not in node_labels:
        raise ValueError(
            f"Node {node} is not in node_labels: {node_labels}"
        )

    adjacency_matrix = construct_adj_matrix(node_labels, arcs)
    # print(adjacency_matrix)

    node_size = len(node_labels)
    index_i = node_labels.index(node)
    # 'node_size' represents the cardiality of the set of nodes in the
    # graph.

    return sum(
        adjacency_matrix[index_i][index_j] * adjacency_matrix[index_k][index_l]
        for index_j in range(index_i + 2, node_size - 1)
        for index_k in range(index_i + 1, index_j)
        for index_l in range(index_j + 1, node_size)
    )

# Testing the counting algorithm
if __name__ == "__main__":
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

    crossings_pre: int = count_graph_crossings(node_order, arcs)

    from arc_crossing import minimize_crossings
    name_order = minimize_crossings(node_order, arcs)
    crossings_post: int = count_graph_crossings(node_order, arcs)

    print(
        "Count of crossings in circular graph:\n"
        f"  - before minimization: {crossings_pre}\n"
        f"  - after minimization: {crossings_post}"
    )

    print(count_node_crossings("Amina", node_order, arcs), "<- correct")
    print(count_node_crossings("Diego", node_order, arcs), "<- incorrect")
