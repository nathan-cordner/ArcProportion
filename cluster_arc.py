"""
Cluster Arc Charts
-- Display node groups together in standard arc chart
-- Applies arc crossing reducing methods

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



def local_search_grouped_node_order(node_groups, nodes, arcs, node_map):
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

def local_adjusting_grouped_node_order(node_groups, nodes, arcs, node_map):
    """
        node_groups:  labels of node clusters
        nodes:  cluster_label followed by integer
        arcs:  shows edges and weights between individual nodes
        node_map:  maps node labels back to node cluster labels
    """
        
    # CLUSTER LOCAL ADJUSTING
    
    start_index = 0
    while start_index < len(nodes):
        end_index = start_index
        cur_group = node_map[nodes[start_index]]
        while end_index < len(nodes) and node_map[nodes[end_index]] == cur_group:
            end_index += 1
        
        nodes = cluster_local_adjusting(start_index, end_index - 1, nodes = nodes, arcs = arcs)
        start_index = end_index
    

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

    
def grouped_arc_chart(group_dict:dict, df:pd.DataFrame=None, source_col="source", dest_col="dest", color_col="color", width_col="width", nodes=[], groups=[], arcs=[], crossing_method = "LS", figsize = "auto", title: str = "", x_label_padding: float = 1.05):
    """
    Inputs:
    -- group_dict:  dictionary containing node : group pairs
    -- df:  Pandas data frame (columns configurable via source_col, dest_col,
            color_col, width_col)
    -- source_col:  name of source column in DataFrame (default "source")
    -- dest_col:  name of dest column in DataFrame (default "dest")
    -- color_col:  name of color column in DataFrame (default "color")
    -- width_col:  name of width column in DataFrame (default "width")
    -- nodes:  list of input nodes
    -- groups:  list of node groups
    -- arcs:  list of tuples to specify arcs (undirected)
      -- Index 0:  label of node 1
      -- Index 1:  label of node 2
      -- Index 2:  color of arc
      -- Index 3:  width of arc
    -- crossing_method:  LS for local search, LA for local adjusting

    
    Output: grouped arc chart showing connection from sources to destinations

    """
    pure_arcs = []
    for arc in arcs:
        pure_arcs.append((arc[0], arc[1]))

    if not df is None:
        pure_arcs = []
        arcs = []
        groups = set()
        nodes = set()
        for _, row in df.iterrows():
            source = row[source_col]
            dest = row[dest_col]
            if not dest in nodes:
                nodes.add(dest)
            if not source in nodes:
                nodes.add(source)
            arcs.append((row[source_col], row[dest_col], row[color_col], row[width_col]))
            pure_arcs.append((row[source_col], row[dest_col]))
        for node, group in group_dict.items():
            if not group in groups:
                groups.add(group)
        nodes = list(nodes)
        groups = list(groups)

    # Create cluster nodes based off of node groups and arcs 
    cluster_arcs = convert_to_cluster_arc(nodes, groups, group_dict, pure_arcs)
    
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
    if crossing_method == "LS":
        local_search_grouped_node_order(groups, nodes, pure_arcs, group_dict)
    else:
        local_adjusting_grouped_node_order(groups, nodes, pure_arcs, group_dict)

    
    # Visualize with basic arc chart
    # TODO:  deliniate groups by color
    
    print(f"Crossings grouped: {count_graph_crossings(nodes, pure_arcs)}")

    
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
        
    """
    # Example 1:  power grid groupings
    nodes, groups, group_dict = read_nodes("datasets/power_grid_groups.csv")
    arcs = read_edges("datasets/power_grid.csv") #, dest_col = "target")

    color_dict = {"Western Europe": "#D55E00",
                  "Central Europe": "#009E73",
                  "Eastern Europe": "#0072B2"}
    """

    
    # Example 2:  Myrtle Warren character interactions harry potter
    
    nodes, groups, group_dict = read_nodes("datasets/myrtle_houses.csv")
    arcs = read_edges("datasets/myrtle_edges.csv", dest_col = "target")
    
    color_dict = {"Gryffindor": "#D55E00",
                  "Slytherin": "#009E73",
                  "Hufflepuff": "#F0E442",
                  "Ravenclaw": "#0072B2",
                  "Other" : "#000000"}
    
    """
    # Example 3:  characters with high interactions
    
    nodes, groups, group_dict = read_nodes("datasets/hp_character_houses.csv")
    arcs = read_edges("datasets/hp_character_interactions.csv")

    color_dict = {"Gryffindor": "#D55E00",
                  "Slytherin": "#009E73",
                  "Hufflepuff": "#F0E442",
                  "Ravenclaw": "#0072B2",
                  "Other" : "#000000"}
    """
    
    
    print("Num nodes:", len(nodes))
    print("Num edges:", len(arcs))
    
    # BEFORE
    
    # Fill in nodes by group order
    new_node_order = []
    for g in groups:
        for n in nodes:
            if group_dict[n] == g:
                new_node_order.append(n)
    # Reassign
    nodes = new_node_order    
    
    print(f"Crossings before: {count_graph_crossings(nodes, arcs)}")
    fig, ax = basic_arc_plot(node_labels = nodes, arcs = arcs)   

    for xtick in ax.get_xticklabels():
        xtick.set_color(color_dict[group_dict[xtick.get_text()]])    
    
    plt.show()
    
    nodes, groups, group_dict = read_nodes("datasets/myrtle_houses.csv")
    arcs = read_edges("datasets/myrtle_edges.csv", dest_col = "target")
    
    start = time.time()
    # plot optimized arc plot, without grouping houses together   
    nodes = node_cluster_order(nodes, arcs)
    end = time.time()
    print(f"Crossings optimized: {count_graph_crossings(nodes, arcs)}")
    print("Running time:", end - start)
    
    fig, ax = basic_arc_plot(node_labels = nodes, arcs = arcs)   

    for xtick in ax.get_xticklabels():
        xtick.set_color(color_dict[group_dict[xtick.get_text()]])    
    
    plt.show()  
    

    # Running time tests
    for i in range(5):    
        
        nodes, groups, group_dict = read_nodes("datasets/myrtle_houses.csv")
        arcs = read_edges("datasets/myrtle_edges.csv", dest_col = "target")

        # Group houses together
        start = time.time()
        fig, ax = grouped_arc_chart(nodes, groups, group_dict, arcs)
        end = time.time()
        print("Running time:", end - start)
        
        for xtick in ax.get_xticklabels():
            xtick.set_color(color_dict[group_dict[xtick.get_text()]])
            
        plt.show()
        
    for i in range(5):    
        
        nodes, groups, group_dict = read_nodes("datasets/myrtle_houses.csv")
        arcs = read_edges("datasets/myrtle_edges.csv", dest_col = "target")
        

        # Group houses together
        start = time.time()
        fig, ax = grouped_arc_chart(nodes, groups, group_dict, arcs, crossing_method = "LA")
        end = time.time()
        print("Running time:", end - start)
        
        for xtick in ax.get_xticklabels():
            xtick.set_color(color_dict[group_dict[xtick.get_text()]])
            
        plt.show()
    
    
    
    
    
    
    
    
    

