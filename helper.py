"""
Visualization helper functions

Author:  Nathan Cordner

"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np


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

# Functions for proportional arc chart
def draw_arc(left, right, ax, color="tab:blue"):
    midpoint = (left + right) / 2
    radius = np.abs(right - midpoint)
    
    new_arc = mpatches.Arc(xy = (midpoint, 0),  width = 2 * radius, height = 4 * radius, theta1 = 0, theta2 = 180, color=color, lw=0.5)
    ax.add_patch(new_arc) 
    
    return radius
    
def shade_arc(pair1, pair2, ax, color="tab:blue"):
    # Find points on ellipse using parametric coordinates
    midpoint1 = (pair1[0] + pair1[1]) / 2
    radius1 = np.abs(pair1[0] - midpoint1)    
    
    theta1 = np.radians(np.linspace(0, 180, 100))
    x1 = midpoint1 + radius1 * np.cos(theta1)
    y1 = 2 * radius1 * np.sin(theta1)
    
    midpoint2 = (pair2[0] + pair2[1]) / 2
    radius2 = np.abs(pair2[0] - midpoint2)    
    
    theta2 = np.radians(np.linspace(0, 180, 100))
    x2 = midpoint2 + radius2 * np.cos(theta2)
    y2 = 2 * radius2 * np.sin(theta2)

    # Fill the area between the arcs
    ax.fill_between(np.concatenate([x1, x2[::-1]]), np.concatenate([y1, y2[::-1]]), color=color, alpha=0.5)
