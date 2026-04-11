"""
Chord charts
-- wraps a basic arc plot around a circle
-- nodes placed evenly around the circumference, chords drawn as
   quadratic Bezier curves through the center
-- can adjust chord color and width
-- figure size determined by node label length

"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.path import Path
import pandas as pd

from helper import auto_resize


class Chord:

    """
    Basic object to store chord components
    """

    def __init__(self, source, dest, color="lightgray", width=1):
        self.source = source
        self.dest = dest
        self.color = color
        self.width = width


def _labels_from_df(df, source_col="source", dest_col="dest"):
    """
    Return node labels from Pandas dataframe

    """

    source_set = set(df[source_col])
    dest_set = set(df[dest_col])
    combined = source_set.union(dest_set)
    return sorted(list(combined))


def _chords_from_df(df, node_index, source_col="source", dest_col="dest",
                    color_col="color", width_col="width",
                    default_color="lightgray", default_width=1):
    """
    Create list of Chord objects from Pandas dataframe

    """
    chords = []
    for i in range(len(df)):
        row = df.iloc[i]
        cur_chord = Chord(node_index[row[source_col]], node_index[row[dest_col]],
                          color=default_color, width=default_width)
        if color_col in df.columns and not pd.isna(row[color_col]):
            cur_chord.color = row[color_col]
        if width_col in df.columns and not pd.isna(row[width_col]):
            cur_chord.width = row[width_col]
        chords.append(cur_chord)
    return chords


def _node_positions(n):
    """
    Return (n, 2) array of evenly spaced points on the unit circle.
    Node 0 is placed at the top (angle pi/2) and nodes proceed clockwise.

    """
    if n == 0:
        return np.zeros((0, 2))
    thetas = np.pi / 2 - 2 * np.pi * np.arange(n) / n
    return np.column_stack((np.cos(thetas), np.sin(thetas)))


def _draw_chord(chord: Chord, positions, ax):
    """
    Function to visually represent a chord as a quadratic Bezier curve
    from source to dest with the control point at the origin.

    Inputs:
        -- chord:  Chord object (source/dest are integer indices into positions)
        -- positions:  (n, 2) array of node coordinates on the unit circle
        -- ax:  matplotlib Axes object

    """

    p_src = positions[chord.source]
    p_dst = positions[chord.dest]

    verts = [tuple(p_src), (0.0, 0.0), tuple(p_dst)]
    codes = [Path.MOVETO, Path.CURVE3, Path.CURVE3]
    path = Path(verts, codes)

    patch = mpatches.PathPatch(path, facecolor="none",
                               edgecolor=chord.color, lw=chord.width)
    ax.add_patch(patch)


def _draw_label(pos, text, ax, label_radius=1.05):
    """
    Place a node label just outside its position on the circle,
    rotated to align radially. Labels on the left half of the circle
    are flipped 180 degrees so text stays upright.

    """

    angle_rad = np.arctan2(pos[1], pos[0])
    angle_deg = np.degrees(angle_rad)

    x = label_radius * np.cos(angle_rad)
    y = label_radius * np.sin(angle_rad)

    if np.cos(angle_rad) < 0:
        rotation = angle_deg + 180
        ha = "right"
    else:
        rotation = angle_deg
        ha = "left"

    ax.text(x, y, text, rotation=rotation, rotation_mode="anchor",
            ha=ha, va="center")


def chord_chart_plot(df=None, node_labels=[], chords=[], figsize="auto",
                     title="", default_color="lightgray", default_width=1,
                     source_col="source", dest_col="dest",
                     color_col="color", width_col="width"):
    """

    Function for creating a chord chart (an arc plot wrapped around a circle)

    Inputs:
    -- df:  Pandas data frame (columns configurable via source_col, dest_col,
            color_col, width_col)

    If no dataframe provided, then required inputs are
    -- node_labels:  a list of unique strings that define node positions
    -- chords:  a list of tuples: (source, dest), (source, dest, color),
                or (source, dest, color, width)

    Optional inputs include
    -- figsize:  if set to "auto", figure is resized based on node label length
    -- title:  prints a title on the chart
    -- default_color:  fallback chord color (default "lightgray")
    -- default_width:  fallback chord line width (default 1)
    -- source_col:  name of source column in DataFrame (default "source")
    -- dest_col:  name of dest column in DataFrame (default "dest")
    -- color_col:  name of color column in DataFrame (default "color")
    -- width_col:  name of width column in DataFrame (default "width")

    """

    if not df is None:
        if not node_labels:
            node_labels = _labels_from_df(df, source_col=source_col,
                                          dest_col=dest_col)

    # Create dictionary for nodes for quick index lookup
    node_index = {}
    for i in range(len(node_labels)):
        n = node_labels[i]
        node_index[n] = i

    # Create chord objects for df
    if not df is None:
        chords = _chords_from_df(df, node_index, source_col=source_col,
                                 dest_col=dest_col, color_col=color_col,
                                 width_col=width_col,
                                 default_color=default_color,
                                 default_width=default_width)

    # resize figure
    if figsize == "auto":
        fig_width = auto_resize(node_labels)
        figsize = (fig_width, fig_width)

    fig, ax = plt.subplots(figsize=figsize)

    # Compute node positions on the unit circle
    positions = _node_positions(len(node_labels))

    # Plot chords
    for chord in chords:
        if not isinstance(chord, Chord):

            x = node_index[chord[0]]
            y = node_index[chord[1]]
            color = chord[2] if len(chord) >= 3 else default_color
            width = chord[3] if len(chord) >= 4 else default_width
            cur_chord = Chord(x, y, color=color, width=width)
        else:
            cur_chord = chord

        _draw_chord(cur_chord, positions, ax)

    # Plot node labels around the circle
    for i in range(len(node_labels)):
        _draw_label(positions[i], node_labels[i], ax)

    # final adjustments
    ax.set_aspect("equal")
    ax.set_xlim(-1.35, 1.35)
    ax.set_ylim(-1.35, 1.35)

    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.spines[["left", "right", "top", "bottom"]].set_visible(False)
    ax.tick_params(axis="both", length=0)
    ax.set_title(title)

    return fig, ax


if __name__ == "__main__":

    # Test Run
    cities = ["Los Angeles", "Denver", "Texas", "Chicago", "Washington D.C.", "Philadelphia", "New York City"]
    chords = [
        ("Texas", "Los Angeles"),
        ("Texas", "Denver"),
        ("Texas", "Chicago"),
        ("Texas", "Washington D.C."),
        ("Texas", "Philadelphia"),
        ("Texas", "New York City")
    ]

    chord_chart_plot(node_labels=cities, chords=chords, title="Cities")
    plt.show()
