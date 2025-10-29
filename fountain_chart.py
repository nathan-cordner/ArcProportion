"""
Fountain Charts
-- Single source flow to multiple destinations
-- Arc width proportional to amount of flow
-- Flows sum up to 100%

Example use cases:
-- Showing emigration from a country
-- Showing resource allocation 

Author:  Nathan Cordner

"""

import matplotlib.pyplot as plt
from helper import auto_resize, draw_arc, shade_arc


def fountain_chart(source: str, data:  list[tuple], figsize = "auto", title: str = "", x_label_padding: float = 1.05):
    """
    Inputs:
    -- source:  text label of source node 
    -- data:  list of tuples to specify arcs
      -- Index 0:  destination label
      -- Index 1:  arc direction ("L" or "R")
      -- Index 2:  destination value (total or percentage)
      -- Index 3:  arc label (optional)

    We assume that the sum of destination values = total value at source
    
    Output: fountain chart showing resource flow from source to destinations

    """
    
    # Find total resource flow
    total = 0
    
    # Sort arcs into left and right
    left_arcs = []
    right_arcs = []
    
    for item in data:
        if item[1].lower() == "l" or item[1].lower() == "left":
            left_arcs.append(item)
        else:
            right_arcs.append(item)       
        total += item[2]       
    
    # create node label order
    node_order = [item[0] for item in left_arcs]
    node_order.append(source)
    node_order += [item[0] for item in right_arcs]
    
    # Create rectangle widths
    widths = [item[2] / total for item in left_arcs]
    widths.append(1.0) # source node
    widths += [item[2] / total for item in right_arcs]
    
    if figsize == "auto":
        figwidth = auto_resize(node_order, 12, x_label_padding)        
        fig, ax = plt.subplots(figsize=(figwidth, figwidth / 3))
    else:
        fig, ax = plt.subplots(figsize=figsize)
    
    
    
    # Lazy rectangles
    ax.bar(node_order, [-2] * len(node_order), width = widths)
    

    
    # Calculate arc boundaries
    # Work from "inside" to "outside"
    # Arcs from source (left to right) should be reverse of left_arcs, then reverse of right_arcs
    
    lefts = []
    rights = []
    arc_order = [item[0] for item in left_arcs][::-1]
    arc_order += [item[0] for item in right_arcs][::-1]
    
    cur_right = node_order.index(source) - 0.5 
    for c in arc_order:
        i = node_order.index(c) # Assumes unique node labels
     
        lefts += [i - widths[i] / 2, i + widths[i] / 2]
        rights += [cur_right + widths[i], cur_right]
        cur_right += widths[i]  
    
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
    Original data:
        
        source = "Texas"
        bussing_data = [("Los Angeles", "L", 1500),
                        ("Denver", "L", 15700),
                        ("Chicago", "R", 30800),
                        ("Washington D.C.", "R", 12500),
                        ("Philadelphia", "R", 3400),
                        ("New York City", "R", 37100)]
        
        title = "Texas Migrant Bussing Destinations"
    
    """
    
    
    source = "Texas"
    bussing_data =[("Los Angeles", "L", 1500),
                    ("Denver", "L", 15700),
                    ("Chicago", "R", 30800),
                    ("Washington D.C.", "R", 12500),
                    ("Philadelphia", "R", 3400),
                    ("New York City", "R", 37100)]
    
    title = "Texas Migrant Bussing Destinations"
    
    
    fountain_chart(source, bussing_data, title=title, x_label_padding = 1.05)