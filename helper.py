"""
Visualization helper functions

Author:  Nathan Cordner

"""

import textwrap

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np


_DEFAULT_WRAP_WIDTH = 12


def wrap_labels(labels, width=_DEFAULT_WRAP_WIDTH):
    """
    Wrap long node labels onto multiple lines so they don't collide when
    rendered as x-tick labels. Words are preserved (no mid-word breaks).

    Input:
        labels:  iterable of strings
        width:   target max characters per line (default 12)
    Output:
        list of wrapped label strings, same length as input

    """
    return [textwrap.fill(str(label), width=width, break_long_words=False)
            for label in labels]


def _label_line_widths(labels):
    """
    Measure the rendered pixel width of each label. Multi-line labels are
    measured by their widest line (that's the line that would collide with a
    neighbor); the line count is returned separately so callers can size the
    figure height.

    Input:  list of (possibly multi-line) label strings
    Output:
        widths:      list[float] — widest-line pixel width per label
        max_lines:   int — highest line count across all labels

    Reference:  https://stackoverflow.com/questions/5320205/matplotlib-text-dimensions

    """
    fig, ax = plt.subplots()
    plt.xlim(0, max(1, len(labels)))
    fig.canvas.draw()
    r = fig.canvas.get_renderer()

    widths = []
    max_lines = 1
    for i, label in enumerate(labels):
        line_count = label.count("\n") + 1
        if line_count > max_lines:
            max_lines = line_count

        widest = 0
        for line in label.split("\n"):
            t = plt.text(i, 0, line)
            bb = t.get_window_extent(renderer=r)
            if bb.width > widest:
                widest = bb.width
        widths.append(widest)

    plt.close(fig)
    return widths, max_lines


def auto_resize(node_labels, default_width=6.4, padding=1.3,
                wrap_width=_DEFAULT_WRAP_WIDTH, return_lines=False):
    """
    Compute a figure width that accommodates each (wrapped) x-tick label
    without overlap. Sums individual label widths rather than multiplying the
    max by the node count so a single long label no longer inflates the whole
    figure.

    Input:
        node_labels:   iterable of label strings (raw, not pre-wrapped)
        default_width: lower bound on figure width in inches (default 6.4)
        padding:       multiplicative padding on the summed label width
        wrap_width:    per-line character budget used when wrapping labels
        return_lines:  when True, also return the max line count so callers
                       can bump figure height to fit 2+ line labels

    Output:
        fig_width                           when return_lines is False
        (fig_width, max_lines_per_label)    when return_lines is True

    """
    wrapped = wrap_labels(node_labels, width=wrap_width)
    widths, max_lines = _label_line_widths(wrapped)
    n = max(1, len(widths))
    widest = max(widths) if widths else 0

    dpi = plt.rcParams['figure.dpi']
    # Labels are placed at integer x-positions 0..N-1, so neighboring label
    # centers are `fig_width / (N-1)` inches apart. That interval must be
    # wider than the widest label, otherwise neighbors overlap.
    # `min_gap_px` keeps a small breathing space between long labels.
    min_gap_px = 10
    if n > 1:
        slot_inches = (widest + min_gap_px) * (n - 1) / dpi
    else:
        slot_inches = widest / dpi
    fit_inches = max(sum(widths) / dpi, slot_inches) * padding
    fig_width = max(fit_inches, default_width)

    if return_lines:
        return fig_width, max_lines
    return fig_width


# Functions for proportional arc chart
def draw_arc(left, right, ax, color="tab:blue"):
    """
    Draw a half-ellipse arc from x=left to x=right above the x-axis and
    return its horizontal radius so callers can track the tallest arc and
    size the y-axis to fit.

    Input:
        left, right: float x-coordinates of the arc's endpoints on y=0
        ax:          matplotlib Axes to draw on
        color:       edge color for the arc outline (default "tab:blue")
    Output:
        radius (float): half of |right - left|; useful for setting ylim

    """
    midpoint = (left + right) / 2
    radius = np.abs(right - midpoint)

    new_arc = mpatches.Arc(xy=(midpoint, 0), width=2 * radius, height=4 * radius,
                           theta1=0, theta2=180, color=color, lw=0.5)
    ax.add_patch(new_arc)

    return radius


def shade_arc(pair1, pair2, ax, color="tab:blue"):
    """
    Shade the region between two half-ellipse arcs to produce a proportional
    ribbon. `pair1` defines the outer arc's left/right x-endpoints and `pair2`
    defines the inner arc's endpoints; both arcs rise above the x-axis.

    Input:
        pair1:  (left, right) endpoints of the outer boundary arc
        pair2:  (left, right) endpoints of the inner boundary arc
        ax:     matplotlib Axes to draw on
        color:  fill color for the shaded ribbon (default "tab:blue",
                rendered at alpha=0.5)

    """
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
    ax.fill_between(np.concatenate([x1, x2[::-1]]), np.concatenate([y1, y2[::-1]]),
                    color=color, alpha=0.5)
