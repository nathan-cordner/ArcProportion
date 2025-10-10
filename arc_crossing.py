"""
Algorithms to reduce arc crossings

Author:  Nathan Cordner

"""

from basic_arc import basic_arc_plot
import matplotlib.pyplot as plt


def dfs(dfs_stack, order, explored, adj_list):
    """
    DFS subroutine to run AVSDF
    
    Nodes are placed on stack in reverse order of degree
    
    """
    
    while dfs_stack:
        cur_node = dfs_stack.pop()
        if not cur_node in explored:
            order.append(cur_node)
            explored.add(cur_node)
            
            node_degs = []
            
            for node in adj_list[cur_node]:
                if not node in explored:
                    node_degs.append((len(adj_list[node]), node))
            node_degs.sort(reverse = True)
            for node in node_degs:
                dfs_stack.append(node[1])


def minimize_crossings(node_labels = [], arcs = []):
    """
    
    Implementation of "Adjacent vertex with smallest degree first" (AVSDF)
    -- from "New circular drawing algorithms" by He and Sykora
    -- https://itat.ics.upjs.sk/proceedings/itat2004-proceedings.pdf#page=20
    
    Inputs:
    -- node_labels:  a list of unique strings that define node positions
    -- arcs:  a list of tuples of format (node_label_1, node_label_2)
    
    Note:  Algorithm assumes unique node labels    
    TODO:  assign unique labels, then revert back original labels?
    
    """
    
    # Construct adjacency list
    adj_list = {}
    for n in node_labels:
        adj_list[n] = set()
    for arc in arcs:
        adj_list[arc[0]].add(arc[1])
        adj_list[arc[1]].add(arc[0])
        
    order = []
    explored = set()
    
    # Sort this, then iterate by degree low to high
    node_degs = []
    for n in node_labels:
        node_degs.append((len(adj_list[n]), n))
    node_degs.sort()
    
    for node in node_degs:
        if not node[1] in explored:
            dfs([node[1]], order, explored, adj_list)
    
    # Minimized arc crossing order
    return order           
            

if __name__ == "__main__":
    # Test case    
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
    
    # Comment out this line of code to see the original order
    node_order = minimize_crossings(node_order, arcs)
    
    basic_arc_plot(node_labels = node_order, arcs = arcs)
    plt.show()
    
    
    