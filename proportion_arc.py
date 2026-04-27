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
from helper import auto_resize, draw_arc, shade_arc, wrap_labels

from count_crossing import count_graph_crossings, local_adjusting, cluster_local_adjusting
from arc_crossing import minimize_crossings

# test code
from basic_arc import basic_arc_plot
import time


def convert_to_basic_arc(nodes, arcs, title = ""):
    """
    Split each node into one copy per incident arc so the proportional chart
    can treat each (split) endpoint as a distinct basic-arc node. The i-th
    occurrence of a node ``X`` becomes the label ``X<i>``, and every input
    arc becomes one arc between the corresponding split-labels.

    Inputs:
        nodes:  list of node labels in desired display order
        arcs:   list of ``(source, dest, value [, color])`` tuples
        title:  unused; preserved for backwards compatibility

    Output:
        tmp_new_nodes:  list of split node labels, reordered so each run of
                        labels coming from the same original node appears
                        together, in the order ``nodes`` was given
        new_arcs:       list of ``(split_source, split_dest, value)`` tuples
                        whose endpoints are labels in ``tmp_new_nodes``
        new_node_map:   dict mapping each split label back to its original
                        node label

    """

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

        if len(a) >= 4 and pd.notna(a[3]):
            new_arcs += [(node1, node2, a[2], a[3])]
        else:
            new_arcs += [(node1, node2, a[2], "lightgray")]

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
    """
    Reduce crossings within a single cluster of split nodes by trying every
    pair swap inside it and keeping those that strictly lower the global
    crossing count. The cluster is the maximal run of consecutive entries in
    ``nodes`` sharing a value under ``node_map``, starting at ``start_index``.

    Inputs:
        start_index:    index into ``nodes`` where this cluster starts
        cur_crossings:  crossing count for the current ordering of ``nodes``
        nodes:          list of split node labels (reordered in place)
        clean_arcs:     list of (source, dest) tuples over split labels
        node_map:       dict mapping split label back to original node

    Output:
        (end_index, cur_crossings)
            end_index:     first index after this cluster, so callers can
                           resume at the next cluster
            cur_crossings: updated crossing count after any improving swaps

    Side effect:  swaps inside ``nodes`` mutate the list in place.

    """
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

def _arcs_and_nodes_from_df(df:pd.DataFrame, source_col="source", dest_col="dest", color_col="color", value_col="value"):
        arcs = []
        nodes = set()
        for _, row in df.iterrows():
            source = row[source_col]
            dest = row[dest_col]
            if not dest in nodes:
                nodes.add(dest)
            if not source in nodes:
                nodes.add(source)
            arcs.append((row[source_col], row[dest_col], row[value_col], row[color_col]))
        nodes = list(nodes)
        return arcs, nodes

def proportion_arc_chart( df:pd.DataFrame=None, source_col="source", dest_col="dest", color_col="color", value_col="value", nodes=[], arcs=[], crossing_method = "LS", figsize = "auto", title: str = "", x_label_padding: float = 1.05, group_dict=None, color_dict=None, gap: float = 0.15):
    """
    Inputs:
    -- nodes:  input nodes (previously split)
    -- arcs  list of tuples to specify arcs (undirected)
      -- Index 0:  label of node 1
      -- Index 1:  label of node 2
      -- Index 2:  arc value (total or percentage)
      -- Index 3:  arc color (optional, default lightgray)
    -- crossing_method:  LS for local search, LA for local adjusting, None for neither
    -- gap:  spacing (in the same units as rectangle widths, i.e. fractions
             of `total`) inserted between neighboring node rectangles. With
             variable widths this controls how tightly nodes sit next to one
             another; smaller values minimize whitespace.

    Output: proportional arc chart showing flow from sources to destinations

    """

    if not df is None:
        arcs, nodes = _arcs_and_nodes_from_df(df, source_col, dest_col, color_col, value_col)

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

    wrapped_nodes = wrap_labels(nodes)

    if figsize == "auto":
        figwidth, max_lines = auto_resize(nodes, 12, x_label_padding,
                                          return_lines=True)
        fig_height = figwidth / 3 + 0.25 * max(0, max_lines - 1)
    else:
        figwidth = figsize[0]
        fig_height = figsize[1]

    # Auto-grow `gap` (in data units) so every adjacent label pair has
    # enough inches between x-positions to render without overlap. Use the
    # widest adjacent *pair* (half-sum of neighbor label widths) — with a
    # single-widest proxy, two equally-wide neighbors only get ~5% breathing
    # room and visually touch. The relationship is self-referential (data
    # span depends on `gap`), so iterate until it converges.
    from helper import _label_line_widths
    label_widths_px, _ = _label_line_widths(wrapped_nodes)
    dpi = plt.rcParams['figure.dpi']
    sum_w = sum(widths)
    n = len(nodes)
    half_pair_mins = [(widths[i] + widths[i + 1]) / 2 for i in range(n - 1)]
    min_half_pair = min(half_pair_mins) if half_pair_mins else 0
    if n > 1 and label_widths_px:
        widest_pair_px = max((label_widths_px[i] + label_widths_px[i + 1]) / 2
                             for i in range(n - 1))
    else:
        widest_pair_px = max(label_widths_px) if label_widths_px else 0
    widest_in = widest_pair_px / dpi
    # Effective plotting inches: the axes occupies ~78% of fig_width after
    # matplotlib's default margins, so use that for label-fit calculations.
    # The x-limits also pad data_span by `gap` on each side (set below).
    AX_FRAC = 0.78
    if n > 1 and widest_in > 0:
        for _ in range(8):
            data_span = sum_w + (n + 1) * gap
            eff_inches = figwidth * AX_FRAC
            widest_data = widest_in * x_label_padding * data_span / eff_inches
            needed_gap = widest_data - min_half_pair
            if needed_gap <= gap:
                break
            denom = eff_inches - widest_in * x_label_padding * (n + 1)
            if denom <= 0:
                figwidth *= 1.5
                fig_height = figwidth / 3 + 0.25 * max(0, max_lines - 1)
                continue
            gap = (widest_in * x_label_padding * sum_w - min_half_pair * eff_inches) / denom
            gap = max(gap, 0)

    # Width-aware x-positions: each node's center sits one (half-width +
    # gap + half-width) step from the previous center, so narrow nodes no
    # longer leave awkward whitespace and wide nodes don't get crowded.
    x_positions = [widths[0] / 2]
    for i in range(1, len(nodes)):
        x_positions.append(
            x_positions[-1] + widths[i - 1] / 2 + gap + widths[i] / 2
        )
    node_center = dict(zip(nodes, x_positions))

    fig, ax = plt.subplots(figsize=(figwidth, fig_height))
    
    # node_color
    bar_colors = []

    for node in nodes:
        cur_color = "lightgray"   # default

        if group_dict is not None and color_dict is not None:
            if node in group_dict:
                cur_group = group_dict[node]
                if cur_group in color_dict:
                    cur_color = color_dict[cur_group]

        bar_colors.append(cur_color)
        
    # Rectangles beneath each node label at their width-aware positions
    ax.bar(x_positions, [-2] * len(nodes), width=widths, color=bar_colors)
    ax.set_xticks(x_positions)
    ax.set_xticklabels(wrapped_nodes)
    
    # Calculate arc boundaries
    # Define L and R boundaries for each of the new nodes, anchored to the
    # width-aware x-position of the original (pre-split) node.
    node_boundary_dict = {}
    cur_group = new_node_map[new_nodes[0]]
    cur_left = node_center[cur_group] - widths[0] / 2

    for n in new_nodes:
        cur_arc = None
        # Find arc involving n
        for arc in new_arcs:
            if n == arc[0] or n == arc[1]:
                cur_arc = arc
                break
        if cur_arc is None:
            continue  # go to next node

        if cur_group != new_node_map[n]:
            cur_group = new_node_map[n]
            idx = nodes.index(cur_group)
            cur_left = node_center[cur_group] - widths[idx] / 2

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
    arc_colors = []
    for a in new_arcs:
        source = a[0]
        dest = a[1]
        color = a[3] if len(a) >= 4 and pd.notna(a[3]) else "lightgray"

        if node_index[source] > node_index[dest]:
            source, dest = dest, source # swap so order is left to right
        
        # Create arc coordinates
        lefts += node_boundary_dict[source]      
        rights += node_boundary_dict[dest][::-1]
        arc_colors.append(color)
    
    max_radius = 0

    # draw the two boundary arcs for each proportional arc
    for i in range(0, len(lefts), 2):
        color = arc_colors[i // 2]

        cur_radius = draw_arc(lefts[i], rights[i], ax, color)
        if cur_radius > max_radius:
            max_radius = cur_radius

        cur_radius = draw_arc(lefts[i+1], rights[i+1], ax, color)
        if cur_radius > max_radius:
            max_radius = cur_radius

    # shade the area between the two boundaries
    for i in range(0, len(lefts), 2):
        color = arc_colors[i // 2]
        shade_arc((lefts[i], rights[i]), (lefts[i+1], rights[i+1]), ax, color)
        
    # Final adjustments
    ax.set_ylim(-0.2, max_radius * 2)
    # Tight x-limits around the node rectangles so there's no dead space
    ax.set_xlim(-widths[0] / 2 - gap, x_positions[-1] + widths[-1] / 2 + gap)

    ax.set_yticklabels([])
    ax.spines[["left", "right", "top", "bottom"]].set_visible(False)
    ax.tick_params(axis = "both", length = 0)
    
    ax.set_title(title)
            
    plt.show()
        
    
def read_csv(file_name, source_col = "source", dest_col = "dest", connections_col = "connections", color_col = "color", default_color = "lightgray"):
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
            color = default_color
            if color_col in df.columns and pd.notna(df[color_col].iloc[i]):
                color = df[color_col].iloc[i]

            arcs.append((df[source_col].iloc[i],
                        df[dest_col].iloc[i],
                        df[connections_col].iloc[i],
                        color))
                
    return nodes, arcs
        
    


if __name__ == "__main__":
    """
    Data format:
        (Source, Destination, Weight)
        Arcs are undirected (self-arcs allowed)
        Total of each location = sum of arc weights where location is either source or dest
    
    """
    """
    # Test data    
    nodes = ["A", "B", "C"]
    arcs = [("A", "B", 100, "red"),
            ("A", "C", 300, "blue"),
            ("B", "C", 200, "purple")]
    
    
    # nodes, arcs = read_csv("datasets/hp_top_ten.csv", dest_col="target", connections_col = "weight")
    # nodes, arcs = read_csv("datasets/power_grid.csv")
    # nodes, arcs = read_csv("datasets/harry_potter_house_interactions.csv")
    # nodes, arcs = read_csv("datasets/myrtle_edges.csv", dest_col="target", connections_col = "weight")
    # nodes, arcs = read_csv("datasets/arXiv_final_35.csv")

    print(f"Original graph. {len(nodes)} nodes and {len(arcs)} edges")
    proportion_arc_chart(nodes, arcs, crossing_method = "LS")

    
    #
    proportion_arc_chart(nodes, arcs, crossing_method = None)
    

    for i in range(5):
        nodes, arcs = read_csv("datasets/arXiv_final_35.csv")
        proportion_arc_chart(nodes, arcs, crossing_method = "LS")
    for i in range(5):
        nodes, arcs = read_csv("datasets/arXiv_final_35.csv")
        proportion_arc_chart(nodes, arcs, crossing_method = "LA")
    """
    
    
    nodes = ["A", "B", "C", "D"]

    # Arc format:
    # (source, dest, weight, arc_color)
    arcs = [
        ("A", "B", 100, "red"),
        ("A", "C", 180, "blue"),
        ("B", "D", 120, "purple"),
        ("C", "D", 80, "green")
    ]

    # group_dict says which group each node belongs to
    group_dict = {
        "A": "Group1",
        "B": "Group2",
        "C": "Group4",
        "D": "Group3"
    }

    # color_dict gives the NODE colors by group
    color_dict = {
        "Group1": "orange",
        "Group2": "gold",
        "Group3": "black"
    }

    print(f"Original graph. {len(nodes)} nodes and {len(arcs)} edges")

    proportion_arc_chart(
        nodes,
        arcs,
        group_dict=group_dict,
        color_dict=color_dict,
        crossing_method="LS",
        title="Test: Arc Colors Different from Node Colors"
    )
