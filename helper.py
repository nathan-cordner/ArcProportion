"""
Visualization helper functions

Author:  Nathan Cordner

"""

import matplotlib.pyplot as plt


def _max_text_width(node_labels):
    """
    Helper function to determine how many pixels are used in an x-axis text label
    
    Input:  list of strings
    Output:  max pixel width 
    
    Reference:  https://stackoverflow.com/questions/5320205/matplotlib-text-dimensions

    """
    
    fig, ax = plt.subplots()
    plt.xlim(0, len(node_labels))
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    
    cur_max = 0
    for i in range(len(node_labels)):    
        t = plt.text(i, 0, node_labels[i])
        bb = t.get_window_extent(renderer=r)    
        width = bb.width
        if width > cur_max:
            cur_max = width
    plt.close()
    return cur_max

def auto_resize(node_labels, default_width = 6.4, padding = 1.05):
    """
    If figsize set to "auto" in basic_arc_plot, calculate figsize param
    based on size of node labels    

    """
    
    # Adjust figsize so that x tick labels don't overlap
    max_width = _max_text_width(node_labels)
    max_width = max(1, max_width)
    
    
    dpi = plt.rcParams['figure.dpi']
    label_width_in_inches = max_width / dpi
    fig_width = label_width_in_inches * len(node_labels) * padding
    if fig_width < default_width:
        fig_width = default_width
    
    return fig_width