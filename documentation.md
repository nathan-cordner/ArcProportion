# Overview
    This is a draft documentation of the ArcProportion project. Below is a list of modules, and an enumeration of their functions and classes.

    In this draft, "has description" means the function contains a docstring describing its utility. "has param explanation" means the function has a docstring which enumerates and explains the input parameters. These docstrings will serve as a starting point for this documentation. 

# Modules:
- arc_crossing.py
- basic_arc.py
- helper.py
- preprocessing.py
- proportion_arc.py
	
# Functions and Classes by Module

## arc_crossing.py
- dfs(dfs_stack, order, explored, adj_list)
	* has description
	* NEEDS param explanation

- minimize_crossings(node_labels = [], arcs = []):
	* has description
	* has param explanation


## basic_arc.py
- class Arc
	* has description
	* needs explanation or no? Type hints?
	
- _labels_from_df(df, source_col="source", dest_col="dest"):
	* has description
	* NEEDS param explanation
	
- _arcs_from_df(df, node_index, source_col="source", dest_col="dest",
                  color_col="color", width_col="width",
                  default_color="lightgray", default_width=1):
	* has description
	* NEEDS param explanation
	
- _draw_arc(arc:  Arc, ax):
	* has description
	* has param explanation
	
- basic_arc_plot(df=None, node_labels=[], arcs=[], figsize="auto",
                   title="", default_color="lightgray", default_width=1,
                   source_col="source", dest_col="dest",
                   color_col="color", width_col="width"):
	* has description
	* bas explanation
	
## cluster_arc.py
- convert_to_cluster_arc(nodes, groups, group_dict, arcs):
	* has description
	* NEEDS param explanation

- local_search_inside_clusters(start_index, cur_crossings, nodes, clean_arcs, node_map):
	* has description
	* NEEDS param explanation
- local_search_grouped_node_order(node_groups, nodes, arcs, node_map):
	* NEEDS description
	* has param explanation
	
- local_adjusting_grouped_node_order(node_groups, nodes, arcs, node_map):
	* NEEDS description
	* has param explanation
	
- node_cluster_order(groups, cluster_arcs)
	* has description
	* NEEDS param explanation
	
- _arcs_and_nodes_from_df(df:pd.DataFrame, source_col="source", dest_col="dest", color_col="color", width_col="width"):
	* NEEDS description
	* NEEDS param explanation
	
- grouped_arc_chart(group_dict:dict, df:pd.DataFrame=None, source_col="source", dest_col="dest", color_col="color", width_col="width", nodes=[], arcs=[], crossing_method = "LS", figsize = "auto", title: str = "", x_label_padding: float = 1.05)
	* NEEDS description
	* has param explanation
	
- read_edges(file_name, source_col = "source", dest_col = "dest"):
	* NEEDS description
	* NEEDS param explanation
	
- read_nodes(file_name, node_col = "node", group_col = "group"):
	* NEEDS description
	* NEEDS param explanation
	

## helper.py
- _max_text_width(node_labels)
	* NEEDS description
	* NEEDS param explanation
	
- auto_resize(node_labels, default_width = 6.4, padding = 1.05):
	* has description
	* NEEDS param explanation

- draw_arc(left, right, ax, color="tab:blue")
	* NEEDS description
	* NEEDS param explanation
	
- shade_arc(pair1, pair2, ax, color="tab:blue"):
	* NEEDS description
	* NEEDS param explanation

## preprocessing.py
- path_traversal(
    traversal_stack, explored, branches,
    adj_list, node_deg
)
	* NEEDS description
	* NEEDS param explanation
	
- exclude_branches(node_labels = [], arcs = []):
	* NEEDS description
	* NEEDS param explanation

proportion_arc.py
- convert_to_basic_arc(nodes, arcs, title = ""):
	* NEEDS description
	* NEEDS param explanation
	
- local_search_inside_clusters(start_index, cur_crossings, nodes, clean_arcs, node_map):
    end_index = start_index
    cur_group = node_map[nodes[start_index]]
    while end_index < len(nodes) and node_map[nodes[end_index]] == cur_group:
	* NEEDS description
	* NEEDS param explanation
	
- grouped_node_order(node_groups, nodes, arcs, node_map, method):
	* NEEDS description
	* has param explanation

- node_cluster_order(nodes, arcs):
	* has description
	* NEEDS param explanation
	
- proportion_arc_chart(nodes, arcs, crossing_method = "LS", figsize = "auto", title: str = "", x_label_padding: float = 1.05)
	* NEEDS description
	* has params
	
- read_csv(file_name, source_col = "source", dest_col = "dest", connections_col = "connections", color_col = "color", default_color = "lightgray"):
	* NEEDS description
	* NEEDS param explanation