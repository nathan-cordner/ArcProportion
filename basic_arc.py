"""
Basic arc plots
-- lists items along a horizontal axis, draws arcs to show relationships
-- can adjust arc color and with
-- figure size determined by x-axis text labels 

Author:  Nathan Cordner

"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd


class Arc:
    
    """
    Basic object to store arc componenets    
    """
    
    def __init__(self, source, dest, color = "lightgray", width = 1):
        self.source = source
        self.dest = dest
        self.color = color
        self.width = width

def draw_arc(arc:  Arc, ax):
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

def max_text_width(node_labels):
    """
    Helper function to determine how many pixels are used in an x-axis text label
    
    Input:  list of strings
    Output:  max pixel width 
    
    Reference:  https://stackoverflow.com/questions/5320205/matplotlib-text-dimensions

    """
    
    f = plt.figure()
    plt.xlim(0, len(node_labels))
    r = f.canvas.get_renderer()
    
    cur_max = 0
    for n in node_labels:    
        t = plt.text(len(node_labels) / 2, 0.5, n)
        bb = t.get_window_extent(renderer=r)    
        width = bb.width
        if width > cur_max:
            cur_max = width
    plt.close()
    return cur_max

    
def basic_arc_plot(df = None, node_labels = [], arcs = [], figsize="auto", title = ""):
    """
        
    Function for creating a basic arc plot
    
    Inputs:
    -- df:  Pandas data frame (columns:  source, dest, color, and width)
    
    If no dataframe provided, then required inputs are
    -- node_labels:  a list of unique strings that define node positions
    -- arcs:  a list of tuples of format (node_label_1, node_label_2)
    
    Optional inputs include
    -- figsize:  if set to "auto", figure is resized based on node label length
    -- title:  prints a title on the chart    
    
    """
    
    if not df is None:
        if not node_labels:
            # Create node labels
            source_set = set(df["source"])
            dest_set = set(df["dest"])
            # Combine
            combined = source_set.union(dest_set)
            # list and sort
            node_labels = sorted(list(combined))
        
    # Create dictionary for nodes for quick index lookup
    node_index = {}
    for i in range(len(node_labels)):
        n = node_labels[i]
        node_index[n] = i
        
    # Create arc objects for df
    if not df is None:
        arcs = []
        for i in range(len(df)):
            row = df.iloc[i]
            
            cur_arc = Arc(node_index[row["source"]], node_index[row["dest"]])
            if not pd.isna(row["color"]):
                cur_arc.color = row["color"]
            if not pd.isna(row["width"]):
                cur_arc.width = row["width"]
            arcs.append(cur_arc)
        
    if figsize == "auto":
        # Adjust figsize so that x tick labels don't overlap
        max_width = max_text_width(node_labels)
        dpi = plt.rcParams['figure.dpi']
        label_width_in_inches = max_width / dpi
        fig_width = label_width_in_inches * len(node_labels) * 1.05
        if fig_width < 6.4:
            fig_width = 6.4
        
        
        figsize = (fig_width, fig_width / 4)
    
    fig, ax = plt.subplots(figsize=figsize)
   
    # Plot nodes 
    x_vals = range(len(node_labels))
    ax.set_xticks(x_vals, node_labels)
     
    # Plot arcs
    max_height = 0
    for arc in arcs:
        if not isinstance(arc, Arc):
        
            x = node_index[arc[0]]
            y = node_index[arc[1]]
            cur_arc = Arc(x, y)
        else:
            cur_arc = arc

        radius = draw_arc(cur_arc, ax)
        if radius > max_height:
            max_height = radius
    
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