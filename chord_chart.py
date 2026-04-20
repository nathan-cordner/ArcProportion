"""
Chord charts
-- d3-style chord diagram with weighted ribbons
-- each node gets an outer arc segment sized proportionally to its total
   incident edge weight
-- ribbons are filled shapes whose endpoint widths along each node's arc
   are proportional to the edge weight
-- optional node clustering: when groups / group_dict are provided, nodes
   in the same group are placed contiguously around the circle with an
   optional extra angular gap between groups and optional per-group colors
-- figure size determined by node label length

"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.path import Path
import pandas as pd

from helper import auto_resize
from count_crossing import count_graph_crossings, local_adjusting, cluster_local_adjusting
from arc_crossing import minimize_crossings


_DEFAULT_PALETTE = [
    "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
    "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf",
]


class Chord:

    """
    Basic object to store chord components.
    `weight` drives the ribbon's angular span at each endpoint. `color` is
    optional; when None, the ribbon takes the source node's color.

    """

    def __init__(self, source, dest, color=None, weight=1.0):
        self.source = source
        self.dest = dest
        self.color = color
        self.weight = weight


def _labels_from_df(df, source_col="source", dest_col="dest"):
    """
    Return node labels from Pandas dataframe

    """
    source_set = set(df[source_col])
    dest_set = set(df[dest_col])
    combined = source_set.union(dest_set)
    return sorted(list(combined))


def _chords_from_df(df, node_index, source_col="source", dest_col="dest",
                    color_col="color", weight_col="weight",
                    default_weight=1.0):
    """
    Create list of Chord objects from Pandas dataframe

    """
    chords = []
    for i in range(len(df)):
        row = df.iloc[i]
        weight = default_weight
        if weight_col in df.columns and not pd.isna(row[weight_col]):
            weight = float(row[weight_col])
        cur = Chord(node_index[row[source_col]], node_index[row[dest_col]],
                    weight=weight)
        if color_col in df.columns and not pd.isna(row[color_col]):
            cur.color = row[color_col]
        chords.append(cur)
    return chords


def _label_pairs(df_or_chords, source_col="source", dest_col="dest"):
    """
    Normalize chord inputs into a list of (source_label, dest_label) tuples.

    """
    if isinstance(df_or_chords, pd.DataFrame):
        return [(df_or_chords[source_col].iloc[i],
                 df_or_chords[dest_col].iloc[i])
                for i in range(len(df_or_chords))]
    return [(ch[0], ch[1]) for ch in df_or_chords]


# --- Clustering helpers (mirrors cluster_arc.py) ---

def _convert_to_cluster_arcs(groups, group_dict, label_arcs):
    cluster_arcs = []
    arc_dict = {g: set() for g in groups}
    for src, dst in label_arcs:
        g0 = group_dict[src]
        g1 = group_dict[dst]
        if g0 not in arc_dict[g1]:
            arc_dict[g0].add(g1)
            arc_dict[g1].add(g0)
            cluster_arcs.append((g0, g1))
    return cluster_arcs


def _node_cluster_order(groups, cluster_arcs):
    before_c = count_graph_crossings(groups, cluster_arcs)
    avsdf = minimize_crossings(groups, cluster_arcs)
    avsdf_c = count_graph_crossings(avsdf, cluster_arcs)
    la = local_adjusting(groups, cluster_arcs)
    la_c = count_graph_crossings(la, cluster_arcs)
    candidates = [(before_c, groups), (avsdf_c, avsdf), (la_c, la)]
    return min(candidates, key=lambda c: c[0])[1]


def _local_search_inside_cluster(start_index, cur_crossings, nodes, arcs, node_map):
    end_index = start_index
    cur_group = node_map[nodes[start_index]]
    while end_index < len(nodes) and node_map[nodes[end_index]] == cur_group:
        end_index += 1
    for i in range(start_index, end_index):
        for j in range(start_index, end_index):
            if i != j:
                nodes[i], nodes[j] = nodes[j], nodes[i]
                new_crossings = count_graph_crossings(nodes, arcs)
                if new_crossings < cur_crossings:
                    cur_crossings = new_crossings
                else:
                    nodes[i], nodes[j] = nodes[j], nodes[i]
    return end_index, cur_crossings


def _local_search_grouped(nodes, arcs, node_map):
    cur_crossings = count_graph_crossings(nodes, arcs)
    start_index = 0
    while start_index < len(nodes):
        start_index, cur_crossings = _local_search_inside_cluster(
            start_index, cur_crossings, nodes, arcs, node_map)


def _local_adjusting_grouped(nodes, arcs, node_map):
    start_index = 0
    while start_index < len(nodes):
        end_index = start_index
        cur_group = node_map[nodes[start_index]]
        while end_index < len(nodes) and node_map[nodes[end_index]] == cur_group:
            end_index += 1
        nodes[:] = cluster_local_adjusting(start_index, end_index - 1,
                                           nodes=nodes, arcs=arcs)
        start_index = end_index


def _cluster_reorder(node_labels, label_arcs, groups, group_dict, crossing_method):
    """
    Return (new_node_order, ordered_groups, group_sizes).

    """
    cluster_arcs = _convert_to_cluster_arcs(groups, group_dict, label_arcs)
    ordered_groups = _node_cluster_order(list(groups), cluster_arcs)

    new_order = []
    group_sizes = []
    for g in ordered_groups:
        members = [n for n in node_labels if group_dict[n] == g]
        new_order.extend(members)
        group_sizes.append(len(members))

    if crossing_method == "LS":
        _local_search_grouped(new_order, label_arcs, group_dict)
    elif crossing_method == "LA":
        _local_adjusting_grouped(new_order, label_arcs, group_dict)

    return new_order, ordered_groups, group_sizes


# --- Layout ---

def _compute_node_layout(node_weights, group_sizes, node_gap, group_gap):
    """
    Return (start_angle, end_angle) per node. Nodes proceed clockwise
    starting at pi/2. `node_gap` separates consecutive nodes within a
    group; `group_gap` additionally separates consecutive groups.

    """
    n = len(node_weights)
    if n == 0:
        return [], []

    if group_sizes is None:
        group_sizes = [n]

    total_weight = sum(node_weights)
    if total_weight <= 0:
        total_weight = n
        node_weights = [1.0] * n

    num_within = max(0, n - len(group_sizes))
    total_gap = num_within * node_gap + len(group_sizes) * group_gap
    available = max(0.1, 2 * np.pi - total_gap)

    per_w = available / total_weight
    start = [0.0] * n
    end = [0.0] * n
    current = np.pi / 2
    idx = 0
    for size in group_sizes:
        for j in range(size):
            span = max(node_weights[idx] * per_w, 1e-6)
            start[idx] = current
            end[idx] = current - span
            current = end[idx]
            if j < size - 1:
                current -= node_gap
            idx += 1
        current -= group_gap
    return start, end


def _compute_ribbon_endpoints(n, chords, node_start, node_end):
    """
    For each chord, allocate angular arcs on each endpoint's node segment
    proportional to the chord weight. Self-loops are skipped. Returns
    {ribbon_index: {'src': (theta_start, theta_end),
                    'dst': (theta_start, theta_end)}}.

    """
    per_node = [[] for _ in range(n)]
    for ridx, ch in enumerate(chords):
        if ch.source == ch.dest:
            continue
        per_node[ch.source].append((ridx, ch.dest, ch.weight, True))
        per_node[ch.dest].append((ridx, ch.source, ch.weight, False))

    # Consistent ordering within each node's arc
    for pn in per_node:
        pn.sort(key=lambda x: x[1])

    endpoints = {}
    for i in range(n):
        if not per_node[i]:
            continue
        seg_span = node_start[i] - node_end[i]
        total_w = sum(x[2] for x in per_node[i])
        if total_w <= 0:
            continue
        per_w = seg_span / total_w
        current = node_start[i]
        for (ridx, _other, w, is_source) in per_node[i]:
            span = w * per_w
            arc = (current, current - span)
            if ridx not in endpoints:
                endpoints[ridx] = {}
            endpoints[ridx]['src' if is_source else 'dst'] = arc
            current -= span

    return endpoints


# --- Drawing ---

def _arc_points(theta_start, theta_end, radius=1.0, steps=24):
    thetas = np.linspace(theta_start, theta_end, steps)
    return [(radius * np.cos(t), radius * np.sin(t)) for t in thetas]


def _draw_node_arc(ax, start, end, color, inner_radius=1.02, outer_radius=1.08):
    """
    Draw the outer ring segment for a single node as an annular wedge.

    """
    theta1 = np.degrees(end)
    theta2 = np.degrees(start)
    thickness = outer_radius - inner_radius
    wedge = mpatches.Wedge((0.0, 0.0), outer_radius, theta1, theta2,
                           width=thickness, facecolor=color,
                           edgecolor="white", linewidth=0.5)
    ax.add_patch(wedge)


def _draw_ribbon(ax, src_arc, dst_arc, color, alpha=0.6, arc_steps=24):
    """
    Draw a filled ribbon whose endpoints are arcs on the unit circle and
    whose sides are quadratic Bezier curves through the origin.

    """
    src_start, src_end = src_arc
    dst_start, dst_end = dst_arc

    verts = [(np.cos(src_start), np.sin(src_start))]
    codes = [Path.MOVETO]

    # Arc along circle: src_start -> src_end
    for pt in _arc_points(src_start, src_end, steps=arc_steps)[1:]:
        verts.append(pt)
        codes.append(Path.LINETO)

    # Bezier: src_end -> dst_start through origin
    verts.append((0.0, 0.0))
    codes.append(Path.CURVE3)
    verts.append((np.cos(dst_start), np.sin(dst_start)))
    codes.append(Path.CURVE3)

    # Arc along circle: dst_start -> dst_end
    for pt in _arc_points(dst_start, dst_end, steps=arc_steps)[1:]:
        verts.append(pt)
        codes.append(Path.LINETO)

    # Bezier: dst_end -> src_start through origin
    verts.append((0.0, 0.0))
    codes.append(Path.CURVE3)
    verts.append((np.cos(src_start), np.sin(src_start)))
    codes.append(Path.CURVE3)

    path = Path(verts, codes)
    patch = mpatches.PathPatch(path, facecolor=color, edgecolor="none",
                               alpha=alpha)
    ax.add_patch(patch)


def _draw_label(angle, text, ax, color="black", label_radius=1.14):
    """
    Place a node label just outside its arc segment, rotated to align
    radially. Labels on the left half of the circle flip 180 degrees so
    text stays upright.

    """
    x = label_radius * np.cos(angle)
    y = label_radius * np.sin(angle)
    angle_deg = np.degrees(angle)
    if np.cos(angle) < 0:
        rotation = angle_deg + 180
        ha = "right"
    else:
        rotation = angle_deg
        ha = "left"
    ax.text(x, y, text, rotation=rotation, rotation_mode="anchor",
            ha=ha, va="center", color=color)


# --- Main API ---

def chord_chart_plot(df=None, node_labels=[], chords=[], figsize="auto",
                     title="", default_color="lightgray", default_weight=1.0,
                     source_col="source", dest_col="dest",
                     color_col="color", weight_col="weight",
                     groups=None, group_dict=None, color_dict=None,
                     crossing_method=None, node_gap=0.005, group_gap=0.03):
    """

    Function for creating a d3-style chord chart with weighted ribbons.

    Inputs:
    -- df:  Pandas data frame (columns configurable via source_col, dest_col,
            color_col, weight_col)

    If no dataframe provided, then required inputs are
    -- node_labels:  a list of unique strings that define node positions
    -- chords:  a list of tuples: (source, dest), (source, dest, color),
                or (source, dest, color, weight)

    Optional inputs include
    -- figsize:  if set to "auto", figure is resized based on node label length
    -- title:  prints a title on the chart
    -- default_color:  fallback chord color (used only as a sentinel; ribbons
                       default to their source node's color)
    -- default_weight:  fallback ribbon weight (default 1.0)
    -- source_col / dest_col / color_col / weight_col:  DataFrame column names

    Optional clustering inputs (leave as None to disable):
    -- groups:  list of group labels defining the group order around the circle
    -- group_dict:  {node_label: group_label} mapping
    -- color_dict:  {group_label: color} used to color node arcs, labels, and
                    any ribbons without an explicit color
    -- crossing_method:  "LS" (local search) or "LA" (local adjusting) to
                         reorder nodes inside each cluster; default None only
                         reorders groups
    -- node_gap:  angular gap (radians) between consecutive nodes within a group
    -- group_gap:  additional angular gap (radians) between groups

    """

    if df is not None and not node_labels:
        node_labels = _labels_from_df(df, source_col=source_col,
                                      dest_col=dest_col)

    ordered_groups = None
    group_sizes = None

    if groups is not None and group_dict is not None:
        if df is not None:
            label_arcs = _label_pairs(df, source_col=source_col,
                                      dest_col=dest_col)
        else:
            label_arcs = _label_pairs(chords)
        node_labels, ordered_groups, group_sizes = _cluster_reorder(
            list(node_labels), label_arcs, groups, group_dict, crossing_method)

    node_index = {n: i for i, n in enumerate(node_labels)}

    if df is not None:
        chord_objs = _chords_from_df(df, node_index, source_col=source_col,
                                     dest_col=dest_col, color_col=color_col,
                                     weight_col=weight_col,
                                     default_weight=default_weight)
    else:
        chord_objs = []
        for ch in chords:
            if isinstance(ch, Chord):
                chord_objs.append(ch)
            else:
                src_i = node_index[ch[0]]
                dst_i = node_index[ch[1]]
                color = ch[2] if len(ch) >= 3 else None
                weight = ch[3] if len(ch) >= 4 else default_weight
                chord_objs.append(Chord(src_i, dst_i, color=color, weight=weight))

    n = len(node_labels)

    # Node weights = sum of incident edge weights (self-loops skipped)
    node_weights = [0.0] * n
    for ch in chord_objs:
        if ch.source == ch.dest:
            continue
        node_weights[ch.source] += ch.weight
        node_weights[ch.dest] += ch.weight
    if sum(node_weights) <= 0:
        node_weights = [1.0] * n

    node_start, node_end = _compute_node_layout(node_weights, group_sizes,
                                                 node_gap, group_gap)
    endpoints = _compute_ribbon_endpoints(n, chord_objs, node_start, node_end)

    if figsize == "auto":
        fig_width = auto_resize(node_labels)
        figsize = (fig_width, fig_width)
    fig, ax = plt.subplots(figsize=figsize)

    def node_color(i):
        if color_dict is not None and group_dict is not None:
            return color_dict.get(group_dict.get(node_labels[i]), "lightgray")
        return _DEFAULT_PALETTE[i % len(_DEFAULT_PALETTE)]

    for i in range(n):
        _draw_node_arc(ax, node_start[i], node_end[i], node_color(i))

    for ridx, ch in enumerate(chord_objs):
        if ridx not in endpoints:
            continue
        if 'src' not in endpoints[ridx] or 'dst' not in endpoints[ridx]:
            continue
        color = ch.color if ch.color is not None else node_color(ch.source)
        _draw_ribbon(ax, endpoints[ridx]['src'], endpoints[ridx]['dst'], color)

    for i in range(n):
        center = (node_start[i] + node_end[i]) / 2
        label_color = "black"
        if color_dict is not None and group_dict is not None:
            label_color = color_dict.get(group_dict.get(node_labels[i]), "black")
        _draw_label(center, node_labels[i], ax, color=label_color)

    ax.set_aspect("equal")
    ax.set_xlim(-1.55, 1.55)
    ax.set_ylim(-1.55, 1.55)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.spines[["left", "right", "top", "bottom"]].set_visible(False)
    ax.tick_params(axis="both", length=0)
    ax.set_title(title)

    return fig, ax


if __name__ == "__main__":

    cities = ["Los Angeles", "Denver", "Texas", "Chicago", "Washington D.C.",
              "Philadelphia", "New York City"]
    chords = [
        ("Texas", "Los Angeles", None, 2),
        ("Texas", "Denver", None, 3),
        ("Texas", "Chicago", None, 1),
        ("Texas", "Washington D.C.", None, 2),
        ("Texas", "Philadelphia", None, 1),
        ("Texas", "New York City", None, 4),
    ]

    chord_chart_plot(node_labels=cities, chords=chords, title="Cities")
    plt.show()
