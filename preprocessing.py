from count_crossing import NodeLabel, construct_adj_list

def path_traversal(
    traversal_stack, explored, branches,
    adj_list, node_deg
):
    """
    DFS a branch (tail) of the graph, collecting nodes with degree <= 2.
    Traversal stops the moment it hits a node of degree > 2, which marks the
    edge of the branch and the start of a denser subgraph. Nodes passed
    through are added to ``branches`` so the caller can exclude them from
    layout.

    Inputs:
        traversal_stack:  seed stack of node labels to explore (mutated)
        explored:         set of already-visited labels (mutated)
        branches:         list of branch nodes collected so far (mutated)
        adj_list:         adjacency list {node: set(neighbors)}
        node_deg:         degree lookup {node: int}

    Output:
        None — ``branches`` and ``explored`` are updated in place.

    """
    while traversal_stack:
        current_node = traversal_stack.pop()

        if node_deg[current_node] > 2: break

        branches.append(current_node)

        if current_node not in explored:
            explored.add(current_node)
            traversal_stack.extend(adj_list[current_node])


def exclude_branches(node_labels = [], arcs = []):
    """
    Drop leaf branches (degree-1 tails) from a node list so only nodes that
    participate in the graph's denser core remain. Useful as a preprocessing
    step before an expensive crossing-reduction pass — nodes on a branch
    can't be reordered to reduce crossings, so excluding them shrinks the
    problem size.

    Inputs:
        node_labels:  list of node labels
        arcs:         list of (source, dest) tuples

    Output:
        list of node labels with all branch nodes removed; preserves the
        relative ordering of ``node_labels``.

    """
    adj_list: dict[NodeLabel, set[NodeLabel]] = construct_adj_list(
        node_labels, arcs
    )

    node_deg: dict[NodeLabel, int] = {
        node: len(adj) for node, adj in adj_list.items()
    }

    branches = []
    explored = set()
    for node, deg in node_deg.items():
        if deg == 1 and node not in explored:
            path_traversal(
                [node], explored, branches, adj_list, node_deg
            )

    return [node for node in node_labels if node not in branches]


if __name__ == "__main__":
    # Test case 1
    # NOTE: exclude_branches is stable and doesn't change original order
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

    
    print(exclude_branches(node_order, arcs))

    # Test case 2
    # NOTE: Branch: E-F-G. Dense subset: ABCD
    node_order =  ["A", "B", "C", "D", "E", "F", "G"]
    arcs = [
        ("A", "B"),
        ("A", "C"),
        ("A", "D"),
        ("B", "C"),
        ("C", "D"),
        ("D", "E"),
        ("E", "F"),
        ("F", "G"),
    ]

    print(exclude_branches(node_order, arcs))

    # Test case 3
    # NOTE: Branches: EFG, XYZ. Dense subset: ABCD
    node_order += ["X", "Y", "Z"]
    arcs = [
        ("A", "B"),
        ("A", "C"),
        ("A", "D"),
        ("B", "C"),
        ("C", "D"),
        ("D", "E"),
        ("E", "F"),
        ("F", "G"),
        ("A", "X"),
        ("X", "Y"),
        ("Y", "Z"),
    ]

    print(exclude_branches(node_order, arcs))

    # Test case 4
    # NOTE: Branches: EFG, YZ. Dense subset: ABCDXMNOP
    node_order += ["M", "N", "O", "P"]
    arcs = [
        ("A", "B"),
        ("A", "C"),
        ("A", "D"),
        ("B", "C"),
        ("C", "D"),
        ("D", "E"),
        ("E", "F"),
        ("F", "G"),
        ("A", "X"),
        ("X", "Y"),
        ("Y", "Z"),
        ("X", "M"),
        ("M", "N"),
        ("M", "O"),
        ("N", "O"),
        ("N", "P"),
        ("O", "P")
    ]

    print(exclude_branches(node_order, arcs))
