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

import matplotlib.pyplot as plt
from helper import auto_resize, draw_arc, shade_arc

def proportion_arc_chart(nodes, arcs, figsize = "auto", title: str = "", x_label_padding: float = 1.05):
    """
    Inputs:
    -- nodes:  text label of each location 
    -- arcs  list of tuples to specify arcs (undirected)
      -- Index 0:  label of node 1
      -- Index 1:  label of node 2
      -- Index 2:  arc value (total or percentage)
      
    TODO:  allow for self-arcs?
    
    Output: proportional arc chart showing flow from sources to destinations

    """
    
    # Find total resource flow
    loc_totals = {x: 0 for x in nodes}
    for a in arcs:
        loc_totals[a[0]] += a[2]
        loc_totals[a[1]] += a[2]   
    total = max(loc_totals.values())
       
    
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
    # TODO:  optimize arc placement given node order
    
    # Current implementation:  use given arc order, always work left to right
    # Also create dictionary for fast node index lookup
    
    current_lefts = {}
    node_index = {}
    for i in range(len(nodes)):
        cur_node = nodes[i]
        current_lefts[cur_node] = i - widths[i] / 2
        node_index[cur_node] = i
        
    # Plot arcs
    lefts = []
    rights = []
    for a in arcs:
        source = a[0]
        dest = a[1]
        
        if node_index[source] > node_index[dest]:
            source, dest = dest, source # swap so order is left to right
        arc_width = a[2] / total 
        
        # Create arc coordinates
        lefts += [current_lefts[source], current_lefts[source] + arc_width]        
        rights += [current_lefts[dest] + arc_width, current_lefts[dest]]
        
        # Update left values
        current_lefts[source] += arc_width
        current_lefts[dest] += arc_width
        
    
    
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


if __name__ == "__main__":
    """
    Data format:
        (Source, Destination, Weight)
        Arcs are undirected (self-arcs allowed)
        Total of each location = sum of arc weights where location is either source or dest
    
    """
    
    nodes = ["A", "B", "C"] # listed in this order, for now
    
    arcs =[("A", "B", 1000),
           ("A", "C", 500),
           ("B", "C", 2000)]
    
    proportion_arc_chart(nodes, arcs, title = "Test Graph")
