from count_crossing import NodeLabel, construct_adj_list

def path_traversal(
    traversal_stack, explored, branches,
    adj_list, node_deg
):
    while traversal_stack:
        current_node = traversal_stack.pop()

        if node_deg[current_node] > 2: break

        branches.append(current_node)

        if current_node not in explored:
            explored.add(current_node)
            traversal_stack.extend(adj_list[current_node])


def exclude_branches(node_labels = [], arcs = []):
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
