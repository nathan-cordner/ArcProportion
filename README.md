# ArcProportion

A new Python visualization library for arc charts


### Current Features

Basic arc chart:  list items along the x-axis and draw arcs to show relationships. Comes with
* Collision reduction:  use algorithms to minimize arc crossings in visualization 
* Pandas support:  data can be passed in as a dataframe with minimal additional customization needed
* Arc customization:  arc colors and widths can be specified


---

### Basic Arc Chart — `basic_arc_plot`

Creates a basic arc plot: items are listed along the x-axis and semicircular arcs are drawn to show relationships.

```python
basic_arc_plot(df=None, node_labels=[], arcs=[], figsize="auto", title="",
               default_color="lightgray", default_width=1,
               source_col="source", dest_col="dest",
               color_col="color", width_col="width")
```

**Args:**

- **df** (*DataFrame, optional*) — Pandas DataFrame with edge data. Column names are configurable via `source_col`, `dest_col`, `color_col`, and `width_col`. If `None`, use `node_labels` and `arcs` instead.
- **node_labels** (*list of str*) — Unique strings defining node positions along the x-axis. Required when `df` is not provided.
- **arcs** (*list of tuples*) — Connections as tuples. Supported formats:
  - `(source, dest)` — uses default color and width
  - `(source, dest, color)` — custom color, default width
  - `(source, dest, color, width)` — custom color and width
- **figsize** (*tuple or `"auto"`*) — Figure dimensions `(width, height)`. When `"auto"`, the figure is resized based on node label length.
- **title** (*str*) — Title displayed on the chart.
- **default_color** (*str*) — Fallback arc color applied when no per-arc override is given. Default `"lightgray"`.
- **default_width** (*float*) — Fallback arc line width applied when no per-arc override is given. Default `1`.
- **source_col** (*str*) — Name of the source column in the DataFrame. Default `"source"`.
- **dest_col** (*str*) — Name of the destination column in the DataFrame. Default `"dest"`.
- **color_col** (*str*) — Name of the color column in the DataFrame. Default `"color"`.
- **width_col** (*str*) — Name of the width column in the DataFrame. Default `"width"`.

**Returns:** `(fig, ax)` — a matplotlib Figure and Axes pair.

> DataFrames that lack color or width columns will not crash — all arcs use the global defaults.

---

### Future Features

"Fountain" chart:  single source, show part-to-whole relationships to destinations

Proportional arc chart:  show part to whole relationships among many sources (ins and outs must equal total value assigned to node)

**Bonus**:  chord charts (wrap arc charts in a circle)


### Requirements

Python 3.11

Pandas

Matplotlib



