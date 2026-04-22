# ArcProportion

A Python visualization library for arc charts and chord diagrams, built on top of `matplotlib` and `pandas`.

ArcProportion makes it easy to visualize relationships between entities as semicircular arcs along a horizontal axis or as chords wrapped around a circle. Data can be passed in as a `pandas.DataFrame` edge list or as plain Python lists and tuples, and every arc or chord can be styled individually with custom colors and line widths.

### Current Features

Basic arc chart:  list items along the x-axis and draw arcs to show relationships. Comes with
* Collision reduction:  use algorithms to minimize arc crossings in visualization
* Pandas support:  data can be passed in as a dataframe with minimal additional customization needed
* Arc customization:  arc colors and widths can be specified
* Long-label friendly:  multi-word x-tick labels are auto-wrapped onto multiple lines so they don't overlap

Grouped arc chart:  basic arc chart that keeps members of the same group contiguous along the x-axis. Comes with
* Cluster-aware crossing reduction:  reorders groups globally and runs local search / local adjusting inside each cluster
* Per-group label coloring:  pass `group_coloring_map={group: color}` to color x-tick labels by group
* Pandas support:  edge list as a DataFrame, plus a `group_dict` mapping each node to its group

Proportional arc chart:  multi-source / multi-destination flow chart where each node is a rectangle whose width is proportional to its total incident weight, and each arc's footprint at each endpoint is proportional to the edge weight. Comes with
* Weighted ribbons:  ribbons are filled half-ellipse shapes, sized end-to-end by the edge value
* Crossing reduction:  same global + cluster-local algorithms as the grouped chart
* Compact layout:  width-aware x-positions pack narrow nodes close together so there's no wasted whitespace between small rectangles

Chord chart (d3-style):  items placed around a circle, with weighted ribbons showing part-to-whole relationships. Comes with
* Weighted ribbons:  each node's outer arc is sized by its total incident edge weight, and each ribbon's endpoint width is proportional to the edge's weight — connection strength reads at a glance
* Optional clustering:  group nodes by an arbitrary category (house, region, etc.) so members of the same group sit contiguously around the circle, with optional crossing-reduction inside each cluster and optional per-group colors for the outer arcs and labels
* Pandas support and chord customization:  same DataFrame / tuple / object inputs as the arc charts


---

## API Reference

### Basic Arc Chart — `basic_arc_plot`

Creates a basic arc plot: items are listed along the x-axis and semicircular arcs are drawn above the axis to show relationships between them.

```python
from basic_arc import basic_arc_plot, Arc

basic_arc_plot(df=None, node_labels=[], arcs=[], figsize="auto", title="",
               default_color="lightgray", default_width=1,
               source_col="source", dest_col="dest",
               color_col="color", width_col="width")
```

**Parameters**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `df` | `pandas.DataFrame`, optional | `None` | Edge list as a DataFrame. Column names are configurable via `source_col`, `dest_col`, `color_col`, and `width_col`. If `None`, use `node_labels` and `arcs` instead. |
| `node_labels` | `list[str]` | `[]` | Unique strings defining node positions along the x-axis. Required when `df` is not provided; when `df` *is* provided, an explicit list overrides the auto-detected ordering. |
| `arcs` | `list[tuple \| Arc]` | `[]` | Connections between nodes. See **Arc formats** below. |
| `figsize` | `tuple \| "auto"` | `"auto"` | Figure dimensions `(width, height)`. When `"auto"`, the figure is resized based on node label length so x-tick labels don't overlap. |
| `title` | `str` | `""` | Title displayed above the chart. |
| `default_color` | `str` | `"lightgray"` | Fallback arc color used when no per-arc override is given. |
| `default_width` | `float` | `1` | Fallback arc line width used when no per-arc override is given. |
| `source_col` | `str` | `"source"` | Name of the source column in the DataFrame. |
| `dest_col` | `str` | `"dest"` | Name of the destination column in the DataFrame. |
| `color_col` | `str` | `"color"` | Name of the optional color column in the DataFrame. |
| `width_col` | `str` | `"width"` | Name of the optional width column in the DataFrame. |

**Returns:** `(fig, ax)` — a matplotlib `Figure` and `Axes` pair.

**Arc formats**

An entry in the `arcs` list can be any of the following:

- `(source, dest)` — uses `default_color` and `default_width`.
- `(source, dest, color)` — custom color, default width.
- `(source, dest, color, width)` — custom color and width.
- `Arc(source, dest, color="...", width=...)` — a fully constructed `Arc` object.

DataFrames that lack `color` or `width` columns — or rows where those cells are `NaN` — fall back to the global defaults without error.

---

### Chord Chart — `chord_chart_plot`

Creates a d3-style chord diagram: each node gets an outer arc segment whose angular size is proportional to its total incident edge weight, and each edge is drawn as a filled ribbon whose endpoint widths along those arcs are proportional to the edge's weight. Ribbon sides are quadratic Bézier curves through the center of the circle. Nodes can optionally be clustered by group so members of the same group sit contiguously around the circumference.

```python
from chord_chart import chord_chart_plot, Chord

chord_chart_plot(df=None, node_labels=[], chords=[], figsize="auto", title="",
                 default_color="lightgray", default_weight=1.0,
                 source_col="source", dest_col="dest",
                 color_col="color", weight_col="weight",
                 groups=None, group_dict=None, color_dict=None,
                 crossing_method=None, node_gap=0.005, group_gap=0.03)
```

**Parameters**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `df` | `pandas.DataFrame`, optional | `None` | Edge list as a DataFrame. Column names are configurable via `source_col`, `dest_col`, `color_col`, and `weight_col`. If `None`, use `node_labels` and `chords` instead. |
| `node_labels` | `list[str]` | `[]` | Unique strings defining node positions around the circle. Nodes are placed clockwise starting from the top of the circle. Required when `df` is not provided. |
| `chords` | `list[tuple \| Chord]` | `[]` | Connections between nodes. See **Chord formats** below. |
| `figsize` | `tuple \| "auto"` | `"auto"` | Figure dimensions `(width, height)`. When `"auto"`, a square figure is sized based on node label length so labels around the circle stay readable. |
| `title` | `str` | `""` | Title displayed above the chart. |
| `default_color` | `str` | `"lightgray"` | Sentinel color used only internally; ribbons without an explicit color fall back to their source node's color. |
| `default_weight` | `float` | `1.0` | Fallback ribbon weight used when no per-chord override is given. |
| `source_col` | `str` | `"source"` | Name of the source column in the DataFrame. |
| `dest_col` | `str` | `"dest"` | Name of the destination column in the DataFrame. |
| `color_col` | `str` | `"color"` | Name of the optional color column in the DataFrame. |
| `weight_col` | `str` | `"weight"` | Name of the optional weight column in the DataFrame. |
| `groups` | `list[str]`, optional | `None` | Group labels defining the group order around the circle. Enables clustering when combined with `group_dict`. |
| `group_dict` | `dict[str, str]`, optional | `None` | Mapping from node label to its group label. |
| `color_dict` | `dict[str, str]`, optional | `None` | Mapping from group label to color; colors the outer node arcs, labels, and any ribbons without an explicit color. Without this mapping, a default palette is used for node arcs. |
| `crossing_method` | `"LS" \| "LA" \| None` | `None` | If set, additionally reorders nodes inside each cluster via local search (`"LS"`) or local adjusting (`"LA"`) to reduce crossings. |
| `node_gap` | `float` | `0.005` | Angular gap (radians) between consecutive nodes within a group. |
| `group_gap` | `float` | `0.03` | Additional angular gap (radians) inserted between groups so clusters read as distinct wedges. |

**Returns:** `(fig, ax)` — a matplotlib `Figure` and `Axes` pair.

**Chord formats**

An entry in the `chords` list can be any of the following:

- `(source, dest)` — uses the source node's color and `default_weight`.
- `(source, dest, color)` — custom color, default weight.
- `(source, dest, color, weight)` — custom color and weight.
- `Chord(source, dest, color="...", weight=...)` — a fully constructed `Chord` object.

DataFrames missing `color`/`weight` columns or with `NaN` cells fall back to the defaults. Node labels around the circle are automatically rotated radially, with labels on the left half of the circle flipped 180° so that text always reads left-to-right. Self-loops are sized into each endpoint node's weight but not drawn.

---

### Grouped Arc Chart — `grouped_arc_chart`

Creates a basic arc chart whose nodes are kept contiguous by group along the x-axis. Group order and intra-group order are both reordered to reduce crossings; x-tick labels can be colored per group via `group_coloring_map`.

```python
from cluster_arc import grouped_arc_chart

grouped_arc_chart(group_dict, df=None,
                  source_col="source", dest_col="dest",
                  color_col="color", width_col="width",
                  nodes=[], arcs=[],
                  crossing_method="LS", figsize="auto",
                  title="", x_label_padding=1.05,
                  group_coloring_map=None)
```

**Parameters**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `group_dict` | `dict[str, str]` | — | Required. Mapping from node label to its group label. Group labels drive the on-axis clustering. |
| `df` | `pandas.DataFrame`, optional | `None` | Edge list as a DataFrame. When provided, `nodes` and `arcs` are derived from it. Column names are configurable via `source_col`, `dest_col`, `color_col`, `width_col`. |
| `source_col` | `str` | `"source"` | Name of the source column in the DataFrame. |
| `dest_col` | `str` | `"dest"` | Name of the destination column in the DataFrame. |
| `color_col` | `str` | `"color"` | Name of the optional color column in the DataFrame. |
| `width_col` | `str` | `"width"` | Name of the optional width column in the DataFrame. |
| `nodes` | `list[str]` | `[]` | Node labels. Required when `df` is not provided. |
| `arcs` | `list[tuple]` | `[]` | Connections between nodes as `(source, dest)`, `(source, dest, color)`, or `(source, dest, color, width)`. Required when `df` is not provided. |
| `crossing_method` | `"LS" \| "LA"` | `"LS"` | Intra-cluster crossing-reduction method — local search (`"LS"`) or local adjusting (`"LA"`). |
| `figsize` | `tuple \| "auto"` | `"auto"` | Figure dimensions `(width, height)`. When `"auto"`, sized based on (wrapped) label widths. |
| `title` | `str` | `""` | Title displayed above the chart. |
| `x_label_padding` | `float` | `1.05` | Horizontal padding multiplier applied to the auto-computed figure width. |
| `group_coloring_map` | `dict[str, str]`, optional | `None` | Mapping from group label to color. When given, each x-tick label is colored by its group. |

**Returns:** `(fig, ax)` — a matplotlib `Figure` and `Axes` pair.

Long node labels are auto-wrapped onto multiple lines (same behavior as `basic_arc_plot`). The DataFrame `color`/`width` columns currently flow through to the underlying basic-arc render; if a column is missing use the `nodes`/`arcs` form.

---

### Proportional Arc Chart — `proportion_arc_chart`

Creates a proportional flow chart: each node is rendered as a rectangle whose width is proportional to its total incident weight, and each edge is drawn as a filled half-ellipse ribbon whose footprint at each endpoint is proportional to the edge's value.

```python
from proportion_arc import proportion_arc_chart

proportion_arc_chart(nodes, arcs,
                     crossing_method="LS", figsize="auto",
                     title="", x_label_padding=1.05, gap=0.15)
```

**Parameters**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `nodes` | `list[str]` | — | Required. Node labels in desired display order (reordered during crossing reduction). |
| `arcs` | `list[tuple]` | — | Required. Connections as `(source, dest, value)` or `(source, dest, value, color)`. `value` is the edge weight; the sum of incident values defines each node's rectangle width. |
| `crossing_method` | `"LS" \| "LA" \| None` | `"LS"` | Intra-cluster crossing-reduction method — local search (`"LS"`), local adjusting (`"LA"`), or `None` to skip reduction. |
| `figsize` | `tuple \| "auto"` | `"auto"` | Figure dimensions `(width, height)`. When `"auto"`, figure width is sized from (wrapped) label widths and scaled up when narrow rectangles would push labels to overlap (capped at 2× the label-based width). |
| `title` | `str` | `""` | Title displayed above the chart. |
| `x_label_padding` | `float` | `1.05` | Horizontal padding multiplier on the auto-computed figure width. |
| `gap` | `float` | `0.15` | Spacing (in the same units as rectangle widths, i.e. fractions of the largest node total) inserted between consecutive node rectangles. Smaller values minimize whitespace; bump it up when a dataset mixes very narrow rectangles with long labels. |

**Returns:** the chart is rendered with `plt.show()`; the `Figure` and `Axes` are accessible via `plt.gcf()` / `plt.gca()`.

**Arc formats**

An entry in the `arcs` list can be:

- `(source, dest, value)` — ribbon drawn in default gray.
- `(source, dest, value, color)` — ribbon drawn in the given color.

Use `read_csv(file_name, source_col=..., dest_col=..., connections_col=..., color_col=...)` from `proportion_arc.py` to build `nodes` / `arcs` from a CSV edge list.

---

### Quick Start

```python
# Basic arc chart
from basic_arc import basic_arc_plot
import matplotlib.pyplot as plt

cities = ["Los Angeles", "Denver", "Texas", "Chicago", "New York City"]
arcs = [("Texas", c) for c in cities if c != "Texas"]
basic_arc_plot(node_labels=cities, arcs=arcs, title="Cities")
plt.show()
```

```python
# Grouped arc chart
from cluster_arc import grouped_arc_chart, read_edges, read_nodes
import matplotlib.pyplot as plt

nodes, _, group_dict = read_nodes("datasets/myrtle_houses.csv")
arcs = read_edges("datasets/myrtle_edges.csv", dest_col="target")
color_map = {"Gryffindor": "#D55E00", "Slytherin": "#009E73",
             "Hufflepuff": "#F0E442", "Ravenclaw": "#0072B2", "Other": "#000000"}
grouped_arc_chart(group_dict, nodes=nodes, arcs=arcs,
                  group_coloring_map=color_map, title="Myrtle — grouped")
plt.show()
```

```python
# Proportional arc chart
from proportion_arc import proportion_arc_chart

nodes = ["A", "B", "C"]
arcs = [("A", "B", 100, "red"),
        ("A", "C", 300, "blue"),
        ("B", "C", 200, "purple")]
proportion_arc_chart(nodes, arcs, title="ABC")
```

---

### Future Features

"Fountain" chart:  single source, show part-to-whole relationships to destinations


### Requirements

Python 3.11

Pandas

Matplotlib

NumPy



