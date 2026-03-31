"""
Test and visualisation script for all stages of the basic_arc.py sprint.
Covers edge cases (Stage 5) and generates Vis 4–10.
"""
import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from basic_arc import basic_arc_plot

out_dir = "Prior visualisations"
os.makedirs(out_dir, exist_ok=True)

print("=== Stage 5: Backward Compatibility ===")

# Backward compat 1: length-2 tuples, no new params
cities = ["Los Angeles", "Denver", "Texas", "Chicago",
          "Washington D.C.", "Philadelphia", "New York City"]
arcs_simple = [
    ("Texas", "Los Angeles"),
    ("Texas", "Denver"),
    ("Texas", "Chicago"),
    ("Texas", "Washington D.C."),
    ("Texas", "Philadelphia"),
    ("Texas", "New York City")
]
fig, ax = basic_arc_plot(node_labels=cities, arcs=arcs_simple, title="Backward Compat: Cities (tuples)")
plt.close(fig)
print("  [PASS] length-2 tuples, no new params")

# Backward compat 2: DataFrame with original column names, empty color/width
df_hp = pd.read_csv("datasets/hp_character_interactions.csv").head(20)
fig, ax = basic_arc_plot(df=df_hp, title="Backward Compat: HP DataFrame")
plt.close(fig)
print("  [PASS] DataFrame with original columns (color/width NaN)")

print("\n=== Stage 5: Edge Cases ===")

# Empty arc list
fig, ax = basic_arc_plot(node_labels=["A", "B", "C"], arcs=[], title="Edge: Empty arcs")
plt.close(fig)
print("  [PASS] Empty arc list")

# Single arc
fig, ax = basic_arc_plot(node_labels=["A", "B"], arcs=[("A", "B")], title="Edge: Single arc")
plt.close(fig)
print("  [PASS] Single arc")

# Self-referencing arc
fig, ax = basic_arc_plot(node_labels=["A", "B"], arcs=[("A", "A", "red")], title="Edge: Self arc")
plt.close(fig)
print("  [PASS] Self-referencing arc")

# DataFrame with only source and dest columns (no color, no width)
df_power = pd.read_csv("datasets/power_grid.csv")
fig, ax = basic_arc_plot(df=df_power, title="Edge: Power grid (no color/width cols)",
                         source_col="source", dest_col="dest")
plt.close(fig)
print("  [PASS] DataFrame missing color/width columns entirely")

# Mixed tuple lengths in same call
mixed_arcs = [
    ("Texas", "Los Angeles"),
    ("Texas", "Denver", "blue"),
    ("Texas", "Chicago", "red", 3),
]
fig, ax = basic_arc_plot(node_labels=["Los Angeles", "Denver", "Texas", "Chicago"],
                         arcs=mixed_arcs, title="Edge: Mixed tuple lengths")
plt.close(fig)
print("  [PASS] Mixed tuple lengths (2, 3, 4)")

print("\n=== Generating Visualizations 4–10 ===")

# Vis 4: Stage 2 — tuple colors and widths
cities5 = ["Los Angeles", "Denver", "Texas", "Chicago", "New York City"]
arcs_v4 = [
    ("Texas", "Los Angeles", "red", 3),
    ("Texas", "Denver", "blue", 2),
    ("Texas", "Chicago", "green"),
    ("Texas", "New York City"),
]
fig, ax = basic_arc_plot(node_labels=cities5, arcs=arcs_v4,
                         title="Stage 2: Per-Arc Tuple Styling")
fig.savefig(os.path.join(out_dir, "vis_04_stage2_tuple_colors.png"),
            dpi=150, bbox_inches="tight")
plt.close(fig)
print("  Saved vis_04")

# Vis 5: Stage 3 — global defaults with tuple input
arcs_v5 = [
    ("Texas", "Los Angeles"),
    ("Texas", "Denver"),
    ("Texas", "Chicago"),
    ("Texas", "Washington D.C."),
    ("Texas", "Philadelphia"),
    ("Texas", "New York City", "red", 4),
]
fig, ax = basic_arc_plot(node_labels=cities, arcs=arcs_v5,
                         title="Stage 3: Steelblue Default + One Red Override",
                         default_color="steelblue", default_width=2)
fig.savefig(os.path.join(out_dir, "vis_05_stage3_global_defaults.png"),
            dpi=150, bbox_inches="tight")
plt.close(fig)
print("  Saved vis_05")

# Vis 6: Stage 3 — global defaults with DataFrame input
df_hp20 = pd.read_csv("datasets/hp_character_interactions.csv").head(20)
fig, ax = basic_arc_plot(df=df_hp20,
                         title="Stage 3: HP DataFrame — Indianred Default",
                         default_color="indianred", default_width=1.5)
fig.savefig(os.path.join(out_dir, "vis_06_stage3_df_defaults.png"),
            dpi=150, bbox_inches="tight")
plt.close(fig)
print("  Saved vis_06")

# Vis 7: Stage 4 — custom column names, myrtle dataset
df_myrtle = pd.read_csv("datasets/myrtle_edges.csv")
fig, ax = basic_arc_plot(df=df_myrtle,
                         title="Stage 4: Myrtle Warren Network (dest_col='target')",
                         source_col="source", dest_col="target",
                         default_color="darkgreen", default_width=1.5)
fig.savefig(os.path.join(out_dir, "vis_07_stage4_myrtle_custom_cols.png"),
            dpi=150, bbox_inches="tight")
plt.close(fig)
print("  Saved vis_07")

# Vis 8: Stage 4 — power grid via DataFrame
df_pg = pd.read_csv("datasets/power_grid.csv")
fig, ax = basic_arc_plot(df=df_pg,
                         title="Stage 4: EU Power Grid (no color/width cols)",
                         source_col="source", dest_col="dest",
                         default_color="darkorange", default_width=2)
fig.savefig(os.path.join(out_dir, "vis_08_stage4_powergrid_df.png"),
            dpi=150, bbox_inches="tight")
plt.close(fig)
print("  Saved vis_08")

# Vis 9: Stage 4 — arXiv dataset
df_arxiv = pd.read_csv("datasets/arXiv_final_25.csv")
fig, ax = basic_arc_plot(df=df_arxiv,
                         title="Stage 4: arXiv Co-Authors (25)",
                         source_col="source", dest_col="dest",
                         default_color="mediumpurple", default_width=1)
fig.savefig(os.path.join(out_dir, "vis_09_stage4_arxiv25.png"),
            dpi=150, bbox_inches="tight")
plt.close(fig)
print("  Saved vis_09")

# Vis 10a: Before style (all defaults)
df_hp15 = pd.read_csv("datasets/hp_character_interactions.csv").head(15)
fig, ax = basic_arc_plot(df=df_hp15, title="Before: All Defaults")
fig.savefig(os.path.join(out_dir, "vis_10a_final_before.png"),
            dpi=150, bbox_inches="tight")
plt.close(fig)
print("  Saved vis_10a")

# Vis 10b: After style (full customization)
fig, ax = basic_arc_plot(df=df_hp15, title="After: Custom Styling",
                         default_color="coral", default_width=2)
fig.savefig(os.path.join(out_dir, "vis_10b_final_after.png"),
            dpi=150, bbox_inches="tight")
plt.close(fig)
print("  Saved vis_10b")

print("\n=== ALL TESTS PASSED, ALL VISUALIZATIONS SAVED ===")
