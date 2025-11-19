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

# test code
from basic_arc import basic_arc_plot

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
    # TODO:  split arcs into node pairs, then put together node groups
    
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

def convert_to_basic_arc(nodes, arcs, title = ""):
    
    node_count = {x : 1 for x in nodes}
    
    # Create new nodes and edges
    new_nodes = []
    new_arcs = []
    
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
        new_arcs += [(node1, node2, a[2])]
        
        
    new_nodes.sort()
        
    # basic_arc_plot(node_labels = new_nodes, arcs = new_arcs)
    
    # print(new_nodes)
    # print(new_arcs)
    # print(new_node_map)
    
    return new_nodes, new_arcs, new_node_map
    
    
def grouped_proportion_arc_chart(nodes, arcs, figsize = "auto", title: str = "", x_label_padding: float = 1.05):
    """
    Inputs:
    -- nodes:  input nodes (previously split)
    -- arcs  list of tuples to specify arcs (undirected)
      -- Index 0:  label of node 1
      -- Index 1:  label of node 2
      -- Index 2:  arc value (total or percentage)
    
    Output: proportional arc chart showing flow from sources to destinations

    """
    
    # Find total resource flow
    loc_totals = {x: 0 for x in nodes}
    for a in arcs:
        loc_totals[a[0]] += a[2]
        loc_totals[a[1]] += a[2]   
    total = max(loc_totals.values())
    
    # Split nodes by arcs
    new_nodes, new_arcs, new_node_map = convert_to_basic_arc(nodes, arcs)
        
    
    # TEST CASE -- hard coding for the moment `:D
    
    new_nodes[0], new_nodes[1] = new_nodes[1], new_nodes[0]
    #new_nodes[-1], new_nodes[-2] = new_nodes[-2], new_nodes[-1]
    
    # Node groups shall be preserved 
    cur_node = new_node_map[new_nodes[0]]
    temp_nodes = [cur_node]
    for n in new_nodes:
        if new_node_map[n] != cur_node:
            cur_node = new_node_map[n]
            temp_nodes += [cur_node]
    assert(len(temp_nodes) == len(nodes)) # Sanity check
    
    # reassign node order
    nodes = temp_nodes
    
    
    
    
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
    # Define L and R boundaries for each of the new nodes
    node_boundary_dict = {}
    cur_node = new_node_map[new_nodes[0]]
    cur_left = 0 - widths[0] / 2
    cur_width = widths[0]
    cur_index = 0
    
    for n in new_nodes:
        cur_arc = None
        # Find arc involving n
        for arc in new_arcs:
            if n == arc[0] or n == arc[1]:
                cur_arc = arc
                break
        if cur_arc == None:
            continue # go to next node       
        
        if cur_node != new_node_map[n]:
            cur_index += 1 
            cur_width = widths[cur_index]
            cur_node = new_node_map[n]
            cur_left = cur_index - widths[cur_index] / 2           
            
        left = cur_left
        right = cur_left + (cur_arc[2] / total)
            
        # save
        node_boundary_dict[n] = [left, right]
            
        # update
        cur_left = right
        
    print(node_boundary_dict)
        
    # Plot arcs
    
    node_index = {}
    for i in range(len(new_nodes)):
        cur_node = new_nodes[i]
        node_index[cur_node] = i
    
    lefts = []
    rights = []
    for a in new_arcs:
        source = a[0]
        dest = a[1]
        
        if node_index[source] > node_index[dest]:
            source, dest = dest, source # swap so order is left to right
        
        # Create arc coordinates
        lefts += node_boundary_dict[source]      
        rights += node_boundary_dict[dest][::-1]
        
    
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
    
    """
    nodes = ["A", "B", "C"] # listed in this order, for now
    
    arcs =[("A", "B", 1000),
           ("A", "C", 500),
           ("B", "C", 2000)]
    """
    nodes = ['Gryffindor', 'Hufflepuff', 'Other', 'Ravenclaw', 'Slytherin']
    
    arcs = [('Gryffindor', 'Gryffindor', 52913),
            ('Gryffindor', 'Hufflepuff', 711),
            ('Gryffindor', 'Other', 1501),
            ('Gryffindor', 'Ravenclaw', 1058),
            ('Gryffindor', 'Slytherin', 12721),
            ('Hufflepuff', 'Hufflepuff', 0),
            ('Hufflepuff', 'Other', 0),
            ('Hufflepuff', 'Ravenclaw', 62),
            ('Hufflepuff', 'Slytherin', 35),
            ('Other', 'Other', 15),
            ('Other', 'Ravenclaw', 11),
            ('Other', 'Slytherin', 41),
            ('Ravenclaw', 'Ravenclaw', 0),
            ('Ravenclaw', 'Slytherin', 32),
            ('Slytherin', 'Slytherin', 627)]   
    
    
    grouped_proportion_arc_chart(nodes, arcs)
    # convert_to_basic_arc(nodes, arcs)
    # proportion_arc_chart(nodes, arcs, title = "Test Graph")
