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
### Arc
`class Arc(self, source, dest, color = "lightgray", width = 1)`

Basic object to store arc components. 

**Parameters**

| Name | Type | Default | Description |
|------|------|---------|-------------|
|source|int|None|A numerical index representing the arc's source node. The index is of the parameter node_labels[] in the function basic_arc_plot(). |
|dest|int|None|A numerical index representing the arc's destination node The index is of the parameter node_labels[] in the function basic_arc_plot().|
|color|string|"lightgray"|Sets the color of the arc. See [this link](https://matplotlib.org/stable/users/explain/colors/colors.html#colors-def) for Matplotlib color guide.|
|width|float|1|Sets the width (thickness) of the Arc|
	


### _labels_from_df 
`_labels_from_df(df, source_col="source", dest_col="dest")`

Returns node labels from Pandas DataFrame. 

**Parameters**

| Name | Type | Default | Description |
|------|------|---------|-------------|
|df|pandas.DataFrame|None|A Pandas DataFrame with named columns|
|source_col|str|"source"|Name of source column in DataFrame df|
|dest_col|str|"dest|Name of destination column in DataFrame df|

**Returns:** `list[str]` - list containing node labels



### _arcs_from_df
`_arcs_from_df(df, node_index, source_col="source", dest_col="dest",
                  color_col="color", width_col="width",
                  default_color="lightgray", default_width=1)`

Create list of Arc objects from Pandas dataframe 


**Parameters**

| Name | Type | Default | Description |
|------|------|---------|-------------|
|df|pandas.DataFrame|None|A Pandas DataFrame with named columns (columns configurable via source_col, dest_col, color_col, width_col)|
|node_index|dict|None|Node labels in a dictionary of form {"First node label": 0, "Second node label": 1, [...], "n-th node label": n}|
|source_col|str|"source"|Name of source column in DataFrame df|
|dest_col|str|"dest"|Name of destination column in DataFrame df|
|color_col|string|"color"|Sets the color of the arc. See [this link](https://matplotlib.org/stable/users/explain/colors/colors.html#colors-def) for Matplotlib color guide.|
|width_col|str|"width"|Name of width column of DataFrame|
|default_color|str|"lightgray"|Sets default arc color|
|default_width|float|1|Sets the width (thickness) of the Arc|
	
**Returns:** `list[Arc] - list of Arc objects for later visualization'



### _draw_arc
`- _draw_arc(arc:  Arc, ax)`

Visually represent an arc.

**Parameters**

| Name | Type | Default | Description |
|------|------|---------|-------------|
|arc|Arc|None|An object of type Arc|
|ax|matplotlib.axes.Axes|None|A matplotlib axes object|

**Returns:** `float: radius` - the radius of the arc


### basic_arc_plot
`basic_arc_plot(df=None, node_labels=[], arcs=[], figsize="auto",
                   title="", default_color="lightgray", default_width=1,
                   source_col="source", dest_col="dest",
                   color_col="color", width_col="width")`

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `df` | `pandas.DataFrame`, optional | `None` | Edge list as a DataFrame. Column names are configurable via `source_col`, `dest_col`, `color_col`, and `width_col`. If `None`, use `node_labels` and `arcs` instead. |
| `node_labels` | `list[str]` | `[]` | Unique strings defining node positions along the x-axis. Required when `df` is not provided; when `df` *is* provided, an explicit list overrides the auto-detected ordering. |
| `arcs` | `list[tuple \| Arc]` | `[]` | Connections between nodes. See **Arc formats** below. |
| `figsize` | `tuple \| "auto"` | `"auto"` | Figure dimensions `(width, height)`. When `"auto"`, the figure is resized based on node label length so x-tick labels don't overlap. |
| `title` | `str` | `""` | Title displayed above the chart. |
| `default_color` | `str` | `"lightgray"` | Fallback arc color used when no per-arc override is given. |
| `default_width` | `float` | `1` | Fallback arc line width used when no per-arc override is given. |
| `source_col` | `str` | `"source"` | Name of the source column in the DataFrame. |
| `dest_col` | `str` | `"dest"` | Name of the destination column in the DataFrame. |
| `color_col` | `str` | `"color"` | Name of the optional color column in the DataFrame. |
| `width_col` | `str` | `"width"` | Name of the optional width column in the DataFrame. |

**Returns:** `(fig, ax)` — a matplotlib `Figure` and `Axes` pair.

**Arc formats**

An entry in the `arcs` list can be any of the following:

- `(source, dest)` — uses `default_color` and `default_width`.
- `(source, dest, color)` — custom color, default width.
- `(source, dest, color, width)` — custom color and width.
- `Arc(source, dest, color="...", width=...)` — a fully constructed `Arc` object.

DataFrames that lack `color` or `width` columns — or rows where those cells are `NaN` — fall back to the global defaults without error.
	
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