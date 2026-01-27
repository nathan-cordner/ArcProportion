"""
Cluster Arc Charts
-- Display node groups together in standard arc chart
-- Applies arc crossing reducing methods

Author:  Nathan Cordner

"""

import pandas as pd
import matplotlib.pyplot as plt
from helper import auto_resize, draw_arc, shade_arc

from count_crossing import count_graph_crossings, local_adjusting
from arc_crossing import minimize_crossings

# test code
from basic_arc import basic_arc_plot


def convert_to_cluster_arc(nodes, groups, group_dict, arcs):
    """
    Iterate through list of arcs
    Place edge between node groups if there is an edge between representative nodes    
    """
    
    cluster_arcs = []
    
    # initialize empty adjacency list
    arc_dict = {}
    for g in groups:
        arc_dict[g] = set()
    
    
    for i in range(len(arcs)):
        cur_arc = arcs[i]
        node_group_0 = group_dict[cur_arc[0]]
        node_group_1 = group_dict[cur_arc[1]]
        
        # check if arc already exists

        if not node_group_0 in arc_dict[node_group_1]:
            # Add new relationship
            arc_dict[node_group_0].add(node_group_1)
            arc_dict[node_group_1].add(node_group_0)
            
            cluster_arcs.append((node_group_0, node_group_1))   
    
    return cluster_arcs
    
        
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



def grouped_node_order(node_groups, nodes, arcs, node_map):
    """
        node_groups:  labels of node clusters
        nodes:  cluster_label followed by integer
        arcs:  shows edges and weights between individual nodes
        node_map:  maps node labels back to node cluster labels
    """
        
    
    cur_crossings = count_graph_crossings(nodes, arcs)
    # print(cur_crossings)
    
    # just swap order inside clusters
    start_index = 0
    while start_index < len(nodes):
        start_index, cur_crossings = local_search_inside_clusters(start_index, cur_crossings, nodes, arcs, node_map)
       
    
    # print(count_graph_crossings(nodes, clean_arcs))
    

def node_cluster_order(groups, cluster_arcs):
    """
        Compute best of AVSDF, Local Adjusting 
        
        Edit node group order accordingly    
    
    """

    before_crossings = count_graph_crossings(groups, cluster_arcs)
        
    # AVSDF
    avsdf_order = minimize_crossings(groups, cluster_arcs)
    avsdf_crossings = count_graph_crossings(avsdf_order, cluster_arcs)
           
    # Local Adjusting    
    local_order = local_adjusting(groups, cluster_arcs)
    local_crossings = count_graph_crossings(local_order, cluster_arcs)
        
    # Find best
    candidates = [(before_crossings, groups),
                  (avsdf_crossings, avsdf_order),
                  (local_crossings, local_order)]
    
    # print(before_crossings, avsdf_crossings, local_crossings)
    
    # return node order of smallest number of crossings
    return min(candidates)[1]

    
def grouped_arc_chart(nodes, groups, group_dict, arcs, figsize = "auto", title: str = "", x_label_padding: float = 1.05):
    """
    Inputs:
    -- nodes:  list of input nodes
    -- groups:  list of node groups
    -- group_dict:  dictionary containing node : group pairs
    -- arcs  list of tuples to specify arcs (undirected)
      -- Index 0:  label of node 1
      -- Index 1:  label of node 2
    
    Output: grouped arc chart showing connection from sources to destinations

    """
    
    # Create cluster nodes based off of node groups and arcs 
    cluster_arcs = convert_to_cluster_arc(nodes, groups, group_dict, arcs)
    
    # compute node group order
    groups = node_cluster_order(groups, cluster_arcs)
    
    # Fill in nodes by group order
    new_node_order = []
    for g in groups:
        for n in nodes:
            if group_dict[n] == g:
                new_node_order.append(n)
    # Reassign
    nodes = new_node_order
    
    #  print(groups)
    # print(nodes)
    
    
    # Redo node order
    grouped_node_order(groups, nodes, arcs, group_dict)
    
    
    # Visualize with basic arc chart
    # TODO:  deliniate groups by color
    
    print(f"Crossings grouped: {count_graph_crossings(nodes, arcs)}")

    
    return basic_arc_plot(node_labels = nodes, arcs = arcs)

        
    
def read_edges(file_name, source_col = "source", dest_col = "dest"):
    """
    Data format:
        (Source, Destination, Weight)
        Arcs are undirected (self-arcs allowed)
        Total of each location = sum of arc weights where location is either source or dest
    
    """

    df = pd.read_csv(file_name)
                
    arcs = []
    
    for i in range(len(df)):
        arcs.append((df[source_col].iloc[i],
                     df[dest_col].iloc[i]))
                
    return arcs
        

def read_nodes(file_name, node_col = "node", group_col = "group"):
    df = pd.read_csv(file_name)
    nodes = list(df[node_col])
    
    groups = list(set(df[group_col]))
    
    group_dict = {}
    for i in range(len(df)):
        cur_node = df[node_col].iloc[i]
        cur_group = df[group_col].iloc[i]
        group_dict[cur_node] = cur_group
    
    
    return nodes, groups, group_dict
    
    
    


if __name__ == "__main__":
    """
    Data format:
        (Source, Destination, Weight)
        Arcs are undirected (self-arcs allowed)
        Total of each location = sum of arc weights where location is either source or dest
    
    """
    nodes, groups, group_dict = read_nodes("datasets/myrtle_houses.csv")
        
    arcs = read_edges("datasets/myrtle_edges.csv", dest_col = "target")
 
    color_dict = {"Gryffindor": "#D55E00",
                  "Slytherin": "#009E73",
                  "Hufflepuff": "#F0E442",
                  "Ravenclaw": "#0072B2",
                  "Other" : "#000000"}
    
    # BEFORE
    print(f"Crossings before: {count_graph_crossings(nodes, arcs)}")
    fig, ax = basic_arc_plot(node_labels = nodes, arcs = arcs)   

    for xtick in ax.get_xticklabels():
        xtick.set_color(color_dict[group_dict[xtick.get_text()]])    
    
    plt.show()
    
    # plot optimized arc plot, without grouping houses together   
    nodes = node_cluster_order(nodes, arcs)
    print(f"Crossings optimized: {count_graph_crossings(nodes, arcs)}")

    
    fig, ax = basic_arc_plot(node_labels = nodes, arcs = arcs)   

    for xtick in ax.get_xticklabels():
        xtick.set_color(color_dict[group_dict[xtick.get_text()]])    
    
    plt.show()  
 
    # Group houses together
    fig, ax = grouped_arc_chart(nodes, groups, group_dict, arcs)
    
    
    for xtick in ax.get_xticklabels():
        xtick.set_color(color_dict[group_dict[xtick.get_text()]])
        
    plt.show()
    
    
    
    
    
    
    
    

