"""
Proportional Arc Charts
-- Multi source, multi destination flow
-- Arc width proportional to amount of flow
-- Flows sum up to 100% (allows for self-edges)

Example use cases:
-- Showing immigration and emigration between countries
-- Showing resource sharing 

Author:  Nathan Cordner

"""

import pandas as pd
import matplotlib.pyplot as plt
from helper import auto_resize, draw_arc, shade_arc

from count_crossing import count_graph_crossings, local_adjusting, cluster_local_adjusting
from arc_crossing import minimize_crossings

# test code
from basic_arc import basic_arc_plot
import time


def convert_to_basic_arc(nodes, arcs, title = ""):
    
    node_count = {x : 1 for x in nodes}
    
    # Create new nodes and edges
    new_nodes = []
    new_arcs = []
    
    clean_arcs = []
    
    # Map new nodes back to old groups
    new_node_map = {}
    
    
    for a in arcs:
        node1 = a[0] + str(node_count[a[0]])
        new_node_map[node1] = a[0]
        node_count[a[0]] += 1       
        
        node2 = a[1] + str(node_count[a[1]])        
        new_node_map[node2] = a[1]
        node_count[a[1]] += 1 

        # TODO:  maintain weights with arcs, or create separate set        
        
        new_nodes += [node1, node2]
        new_arcs += [(node1, node2, a[2])]
        clean_arcs += [(node1, node2)]
        
        
    new_nodes.sort() 
                
    # now reorder new_nodes based on list given in nodes
    
    tmp_new_nodes = []
    for n in nodes:
        for x in new_nodes:
            if new_node_map[x] == n:
                tmp_new_nodes.append(x)
    
    return tmp_new_nodes, new_arcs, new_node_map
    
        
def local_search_inside_clusters(start_index, cur_crossings, nodes, clean_arcs, node_map):
    end_index = start_index
    cur_group = node_map[nodes[start_index]]
    while end_index < len(nodes) and node_map[nodes[end_index]] == cur_group:
        end_index += 1

    
    # Local search loop
    for i in range(start_index, end_index):
        for j in range(start_index,end_index):
            if not i == j:
                # Try swapping
                nodes[i], nodes[j] = nodes[j], nodes[i]
                new_crossings = count_graph_crossings(nodes, clean_arcs)
                if new_crossings < cur_crossings:
                    cur_crossings = new_crossings
                else:
                    # Swap back
                    nodes[i], nodes[j] = nodes[j], nodes[i]  
    return end_index, cur_crossings


def grouped_node_order(node_groups, nodes, arcs, node_map, method):
    """
        node_groups:  labels of node clusters
        nodes:  cluster_label followed by integer
        arcs:  shows edges and weights between individual nodes
        node_map:  maps node labels back to node cluster labels
    """
    
    clean_arcs = [(a[0], a[1]) for a in arcs]
    
    if method == "LS":
        
        # LOCAL SEARCH METHOD
        cur_crossings = count_graph_crossings(nodes, clean_arcs)
        # print(cur_crossings)
        
        # just swap order inside clusters
        start_index = 0
        
        while start_index < len(nodes):
            start_index, cur_crossings = local_search_inside_clusters(start_index, cur_crossings, nodes, clean_arcs, node_map)
            
    elif method == "LA":
        # CLUSTER LOCAL ADJUSTING
        
        start_index = 0
        cluster_sizes = []
        
        while start_index < len(nodes):
            end_index = start_index
            cur_group = node_map[nodes[start_index]]
            while end_index < len(nodes) and node_map[nodes[end_index]] == cur_group:
                end_index += 1
            
            nodes = cluster_local_adjusting(start_index, end_index - 1, nodes = nodes, arcs = clean_arcs)
            cluster_sizes.append(end_index - start_index)
            
            start_index = end_index
        print("num clusters:", len(cluster_sizes))
        print("cluster sizes", sorted(cluster_sizes, reverse = True))        

    return clean_arcs
    
def node_cluster_order(nodes, arcs):
    """
        Compute best of AVSDF, Local Adjusting 
        
        Edit node order accordingly    
    
    """

    clean_arcs = [(a[0], a[1]) for a in arcs]        
    before_crossings = count_graph_crossings(nodes, clean_arcs)
        
    # AVSDF
    avsdf_order = minimize_crossings(nodes, clean_arcs)
    avsdf_crossings = count_graph_crossings(avsdf_order, clean_arcs)
           
    # Local Adjusting    
    local_order = local_adjusting(nodes, clean_arcs)
    local_crossings = count_graph_crossings(local_order, clean_arcs)
        
    # Find best
    candidates = [(before_crossings, nodes),
                  (avsdf_crossings, avsdf_order),
                  (local_crossings, local_order)]
    
    # print(before_crossings, avsdf_crossings, local_crossings)
    
    # return node order of smallest number of crossings
    return min(candidates)[1]
    
def proportion_arc_chart(nodes, arcs, crossing_method = "LS", figsize = "auto", title: str = "", x_label_padding: float = 1.05):
    """
    Inputs:
    -- nodes:  input nodes (previously split)
    -- arcs  list of tuples to specify arcs (undirected)
      -- Index 0:  label of node 1
      -- Index 1:  label of node 2
      -- Index 2:  arc value (total or percentage)
    -- crossing_method:  LS for local search, LA for local adjusting, None for neither
    
    Output: proportional arc chart showing flow from sources to destinations

    """
    
    start = time.time()
    
    # Find total resource flow
    loc_totals = {x: 0 for x in nodes}
    for a in arcs:
        loc_totals[a[0]] += a[2]
        loc_totals[a[1]] += a[2]   
    total = max(loc_totals.values())
    
    # compute clustered node order
    if crossing_method:
        nodes = node_cluster_order(nodes, arcs)
    
    # Split nodes by arcs
    new_nodes, new_arcs, new_node_map = convert_to_basic_arc(nodes, arcs)
    print(f"Transformed graph. {len(new_nodes)} nodes and {len(new_arcs)} edges")

    # Redo node order
    clean_arcs = grouped_node_order(nodes, new_nodes, new_arcs, new_node_map, crossing_method)

    stop = time.time()
    print("Proportion Arc Crossing Reduction Time:", stop - start)
    # print(new_nodes)
    # print(clean_arcs)
    print("Final number of crossings:", count_graph_crossings(new_nodes, clean_arcs))

    
    # Node groups shall be preserved 
    cur_node = new_node_map[new_nodes[0]]
    temp_nodes = [cur_node]
    for n in new_nodes:
        if new_node_map[n] != cur_node:
            cur_node = new_node_map[n]
            temp_nodes += [cur_node]
            
    # print(temp_nodes)
    # print(nodes)
    assert(len(temp_nodes) == len(nodes)) # Sanity check
    
    
    # reassign node order
    nodes = temp_nodes
    # print(nodes)
    
    
    
    # Create rectangle widths using specified node order
    widths = [loc_totals[x] / total for x in nodes]
    
    if figsize == "auto":
        figwidth = auto_resize(nodes, 12, x_label_padding)        
        fig, ax = plt.subplots(figsize=(figwidth, figwidth / 3))
    else:
        fig, ax = plt.subplots(figsize=figsize)
    
    # Lazy rectangles
    ax.bar(nodes, [-2] * len(nodes), width = widths)
    
    # Calculate arc boundaries    
    # Define L and R boundaries for each of the new nodes
    node_boundary_dict = {}
    cur_node = new_node_map[new_nodes[0]]
    cur_left = 0 - widths[0] / 2
    cur_width = widths[0]
    cur_index = 0
    
    for n in new_nodes:
        cur_arc = None
        # Find arc involving n
        for arc in new_arcs:
            if n == arc[0] or n == arc[1]:
                cur_arc = arc
                break
        if cur_arc == None:
            continue # go to next node       
        
        if cur_node != new_node_map[n]:
            cur_index += 1 
            cur_width = widths[cur_index]
            cur_node = new_node_map[n]
            cur_left = cur_index - widths[cur_index] / 2           
            
        left = cur_left
        right = cur_left + (cur_arc[2] / total)
            
        # save
        node_boundary_dict[n] = [left, right]
            
        # update
        cur_left = right
        
    # print(node_boundary_dict)
        
    # Plot arcs
    
    node_index = {}
    for i in range(len(new_nodes)):
        cur_node = new_nodes[i]
        node_index[cur_node] = i
    
    lefts = []
    rights = []
    for a in new_arcs:
        source = a[0]
        dest = a[1]
        
        if node_index[source] > node_index[dest]:
            source, dest = dest, source # swap so order is left to right
        
        # Create arc coordinates
        lefts += node_boundary_dict[source]      
        rights += node_boundary_dict[dest][::-1]
        
    
    max_radius = 0
    for i in range(len(lefts)):
        cur_radius = draw_arc(lefts[i], rights[i], ax) 
        if cur_radius > max_radius:
            max_radius = cur_radius
        
    for i in range(0, len(lefts), 2):
        shade_arc((lefts[i], rights[i]), (lefts[i+1], rights[i+1]), ax)
        
    # Final adjustments
    ax.set_ylim(-0.2, max_radius * 2)
    
    ax.set_yticklabels([])
    ax.spines[["left", "right", "top", "bottom"]].set_visible(False)
    ax.tick_params(axis = "both", length = 0)
    
    ax.set_title(title)
            
    plt.show()
        
    
def read_csv(file_name, source_col = "source", dest_col = "dest", connections_col = "connections"):
    """
    Data format:
        (Source, Destination, Weight)
        Arcs are undirected (self-arcs allowed)
        Total of each location = sum of arc weights where location is either source or dest
    
    """

    df = pd.read_csv(file_name)
    
    nodes = list(set(pd.concat([df[source_col], df[dest_col]])))
            
    arcs = []
    
    for i in range(len(df)):
        if df[connections_col].iloc[i] > 0:
            arcs.append((df[source_col].iloc[i],
                         df[dest_col].iloc[i],
                         df[connections_col].iloc[i]))
                
    return nodes, arcs
        
    


if __name__ == "__main__":
    """
    Data format:
        (Source, Destination, Weight)
        Arcs are undirected (self-arcs allowed)
        Total of each location = sum of arc weights where location is either source or dest
    
    """
    
    # Test data    
    nodes = ["A", "B", "C"]
    arcs = [("A", "B", 100),
            ("A", "C", 300),
            ("B", "C", 200)]
    
 
    # nodes, arcs = read_csv("datasets/hp_top_ten.csv", dest_col="target", connections_col = "weight")
    # nodes, arcs = read_csv("datasets/power_grid.csv")
    # nodes, arcs = read_csv("datasets/harry_potter_house_interactions.csv")
    # nodes, arcs = read_csv("datasets/myrtle_edges.csv", dest_col="target", connections_col = "weight")
    # nodes, arcs = read_csv("datasets/arXiv_final_35.csv")

    print(f"Original graph. {len(nodes)} nodes and {len(arcs)} edges")
    proportion_arc_chart(nodes, arcs, crossing_method = "LS")

    
    """
    proportion_arc_chart(nodes, arcs, crossing_method = None)
    

    for i in range(5):
        nodes, arcs = read_csv("datasets/arXiv_final_35.csv")
        proportion_arc_chart(nodes, arcs, crossing_method = "LS")
    for i in range(5):
        nodes, arcs = read_csv("datasets/arXiv_final_35.csv")
        proportion_arc_chart(nodes, arcs, crossing_method = "LA")
    """
    
    
    
