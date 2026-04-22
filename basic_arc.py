"""
Basic arc plots
-- lists items along a horizontal axis, draws arcs to show relationships
-- can adjust arc color and width
-- figure size determined by x-axis text labels 

Author:  Nathan Cordner

"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd

from helper import auto_resize, wrap_labels


class Arc:
    
    """
    Basic object to store arc componenets    
    """
    
    def __init__(self, source, dest, color = "lightgray", width = 1):
        self.source = source
        self.dest = dest
        self.color = color
        self.width = width

def _labels_from_df(df, source_col="source", dest_col="dest"):
    """
    Return node labels from Pandas dataframe

    """

    # Create node labels
    source_set = set(df[source_col])
    dest_set = set(df[dest_col])
    # Combine
    combined = source_set.union(dest_set)
    # list and sort
    return sorted(list(combined))

def _arcs_from_df(df, node_index, source_col="source", dest_col="dest",
                  color_col="color", width_col="width",
                  default_color="lightgray", default_width=1):
    """
    Create list of Arc objects from Pandas dataframe 

    """
    arcs = []
    for i in range(len(df)):
        row = df.iloc[i]
        cur_arc = Arc(node_index[row[source_col]], node_index[row[dest_col]],
                      color=default_color, width=default_width)
        if color_col in df.columns and not pd.isna(row[color_col]):
            cur_arc.color = row[color_col]
        if width_col in df.columns and not pd.isna(row[width_col]):
            cur_arc.width = row[width_col]
        arcs.append(cur_arc)
    return arcs

    
def _draw_arc(arc:  Arc, ax):
    """
    Function to visually represent an arc
    
    Inputs: 
        -- arc:  Arc object
        -- ax:  matplotlib Axes object     
    
    """
    
    left = arc.source
    right = arc.dest
    
    # assume that left has the lower coordinate value
    if left > right:
        left, right = right, left
    
    # compute semi-circle
    midpoint = (left + right) / 2
    radius = right - midpoint
    
    # draw arc with provided customizations 
    new_arc = mpatches.Arc(xy = (midpoint, 0),  width = 2 * radius, height = radius,
                           theta1 = 0, theta2 = 180, color = arc.color, lw = arc.width)
    ax.add_patch(new_arc)
    
    # return radius of arc to resize figure if necessary
    return radius  
    
  
def basic_arc_plot(df=None, node_labels=[], arcs=[], figsize="auto",
                   title="", default_color="lightgray", default_width=1,
                   source_col="source", dest_col="dest",
                   color_col="color", width_col="width"):
    """
        
    Function for creating a basic arc plot
    
    Inputs:
    -- df:  Pandas data frame (columns configurable via source_col, dest_col,
            color_col, width_col)
    
    If no dataframe provided, then required inputs are
    -- node_labels:  a list of unique strings that define node positions
    -- arcs:  a list of tuples: (source, dest), (source, dest, color),
              or (source, dest, color, width)
    
    Optional inputs include
    -- figsize:  if set to "auto", figure is resized based on node label length
    -- title:  prints a title on the chart
    -- default_color:  fallback arc color (default "lightgray")
    -- default_width:  fallback arc line width (default 1)
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
        
    # Create arc objects for df
    if not df is None:
        arcs = _arcs_from_df(df, node_index, source_col=source_col,
                             dest_col=dest_col, color_col=color_col,
                             width_col=width_col,
                             default_color=default_color,
                             default_width=default_width)
        
    # Wrap long labels so they don't overlap when rendered
    wrapped_labels = wrap_labels(node_labels)

    # resize figure
    if figsize == "auto":
        fig_width, max_lines = auto_resize(node_labels, return_lines=True)
        # Add a small amount of vertical room per extra label line
        fig_height = fig_width / 4 + 0.25 * max(0, max_lines - 1)
        figsize = (fig_width, fig_height)

    fig, ax = plt.subplots(figsize=figsize)

    # Plot nodes
    x_vals = range(len(node_labels))
    ax.set_xticks(x_vals, wrapped_labels)
     
    # Plot arcs
    max_height = 0
    for arc in arcs:
        if not isinstance(arc, Arc):
        
            x = node_index[arc[0]]
            y = node_index[arc[1]]
            color = arc[2] if len(arc) >= 3 else default_color
            width = arc[3] if len(arc) >= 4 else default_width
            cur_arc = Arc(x, y, color=color, width=width)
        else:
            cur_arc = arc

        radius = _draw_arc(cur_arc, ax)
        if radius > max_height:
            max_height = radius
    
    # final adjustments
    ax.set_ylim(0, (max_height / 2) * 1.01)  
    ax.set_xlim(0 - x_vals[-1] * 0.01, x_vals[-1] * 1.01)

    ax.set_yticklabels([])
    ax.spines[["left", "right", "top", "bottom"]].set_visible(False)
    ax.tick_params(axis = "both", length = 0)
    ax.set_title(title)
    
    return fig, ax


if __name__ == "__main__":

    # Test Run
    cities = ["Los Angeles", "Denver", "Texas", "Chicago", "Washington D.C.", "Philadelphia", "New York City"]
    arcs = [
        ("Texas", "Los Angeles"),
        ("Texas", "Denver"),
        ("Texas", "Chicago"),
        ("Texas", "Washington D.C."),
        ("Texas", "Philadelphia"),
        ("Texas", "New York City")
    ]
    
    basic_arc_plot(node_labels = cities, arcs = arcs, title="Cities")
    plt.show()