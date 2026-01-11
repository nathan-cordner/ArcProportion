from warnings import warn
from collections.abc import Callable
from math import inf

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
    adj_list = {node: set() for node in node_labels}
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

        Raises ValueError if node is not in graph.
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

def permutator(matrix_size: int, offset: int) -> Callable[[int], int]:
    if offset >= matrix_size: raise ValueError(
            f"Offset {offset} is too large for matrix with size {matrix_size}."
        )

    def permutate(index: int) -> int:
        result = (index + offset) % matrix_size 
        return result

    return permutate

#WARN: Counting crossing functions signature has been updated and the
#      subroutine have been separated. Now fuctions expect a matrix as
#      part of their arguments, instead of building it in situ.
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

    node_size = len(node_labels)

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
    """
    Returns the count of crossings on the incident edges of 'node' in the
    graph ('node_labels', 'arcs'), where 'node_labels' represents the nodes,
    and 'arcs' represets the edges.
    """
    if node not in node_labels: raise ValueError(
            f"Node {node} is not in node_labels: {node_labels}"
        )

    adjacency_matrix = construct_adj_matrix(node_labels, arcs)

    node_size = len(node_labels)
    # 'node_size' represents the cardiality of the set of nodes in the
    # graph.
    index_i = node_labels.index(node)
    p = permutator(node_size, index_i)

    return sum(
        adjacency_matrix[index_i][p(index_j)] * adjacency_matrix[p(index_k)][p(index_l)]
        for index_j in range(2, node_size)
        for index_k in range(1, index_j)
        for index_l in range(index_j + 1, node_size)
    )

def local_adjusting(nodes = [], arcs = []):
    """
    Re-orders the list from higher to lower crossing counts. 
    Then it grabs the the first node and places it in all positions and inserts it in the best position. 
    Repeats for all nodes. Then moves to the next node in the ranked list.
    """

    ranked_by_count_crossing = sorted(
        list(nodes),
        key = lambda x: count_node_crossings(x, nodes, arcs),
        reverse = True
    )

    final_order = list(nodes)
    for node in ranked_by_count_crossing:
        final_order.remove(node)
        best_pos = 0
        graph_cross_counting = inf

        for pos in range(len(nodes)):
            final_order.insert(pos, node)

            current_graph_cross_counting = count_graph_crossings(final_order, arcs)

            if current_graph_cross_counting < graph_cross_counting:
                graph_cross_counting = current_graph_cross_counting
                best_pos = pos
            final_order.pop(pos)

        final_order.insert(best_pos, node)

    return final_order
