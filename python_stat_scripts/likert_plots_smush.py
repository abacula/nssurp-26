import os
import sys
import tkinter as tk
from tkinter import filedialog
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# pick csv file
root = tk.Tk()
root.withdraw()
root.update()

CSV = filedialog.askopenfilename(
    title="Select the Likert responses CSV",
    filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
)
root.destroy()

if not CSV:
    print("No file selected. Exiting.")
    sys.exit()

print(f"Loaded: {CSV}")

# save plots next to the CSV, not wherever the script was launched from
OUTDIR = os.path.dirname(os.path.abspath(CSV))

extra_info = "smush"
# condition cols
CONDITIONS = ["control", "s_all", "d_all", "w_all"]
adj = "n"

# x-axis labels
LABELS = {
    "control":  "Control",
    "s_all":     "Slow",
    "d_all":     "Dodge",
    "w_all":     "Wave",
    "s_adj":     "Slow",
    "d_adj":     "Dodge",
    "w_adj":     "Wave",
    "avg":   "Average (motion)",
}

# anchor words for each question: (low end = 1, high end = 5)
ANCHORS = {
    "invasive-respectful":  ("Invasive", "Respectful"),
    "unfriendly-friendly":  ("Unfriendly", "Friendly"),
    "dangerous-safe":       ("Dangerous", "Safe"),
    "ignored-seen":         ("Ignored", "Seen"),
}

def y_tick_labels(low, high):
    """Build the 5 worded tick labels, e.g. Very Invasive ... Very Respectful."""
    return [
        f"{low}",
        f"Slightly\n{low}",
        "Neutral",
        f"Slightly\n{high}",
        f"{high}",
    ]

# load and reshape the data
df = pd.read_csv(CSV)
df = df.dropna(subset=["question"])

# melt data: one row per (participant, question, condition, rating)
long = df.melt(
    id_vars=["question", "participant_id"],
    value_vars=CONDITIONS,
    var_name="condition",
    value_name="rating",
).dropna(subset=["rating"])

# plots
for q in df["question"].unique():
    sub = long[long["question"] == q]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.tick_params(axis='both', which='major', labelsize=20, length=8, width=2)
    sns.boxplot(
        x="condition", y="rating", data=sub,
        order=CONDITIONS, hue="condition", legend=False,
        palette="GnBu",
        medianprops={"color": "red", "linewidth": 2},
        flierprops={"marker": "o", "markerfacecolor": "none",
                    "markeredgecolor": "gray", "markersize": 5},
        ax=ax,
    )

    # worded y-axis, number fallback
    low, high = ANCHORS.get(q, (None, None))
    ax.set_ylim(0.5, 5.5)
    sns.despine(top=True, right=True, left=True, bottom=True)
    if adj=="y":
        ax.set_yticks([-4,-3,-2,-1,0,1,2,3,4])
    else:
        ax.set_yticks([1, 2, 3, 4, 5])
    if low and adj!="y":
        ax.set_yticklabels(y_tick_labels(low, high))
    ax.set_ylabel("")

    ax.set_xticks(range(len(CONDITIONS)))
    ax.set_xticklabels([LABELS[c] for c in CONDITIONS])
    ax.set_xlabel("Trial")

    #ax.set_title(f"{q} by Trial Type")
    ax.grid(axis="y", linestyle="--", alpha=0.7)
    ax.set_axisbelow(True)

    fig.tight_layout()
  
    fig.savefig(os.path.join(OUTDIR, f"figs/plot_{q}{extra_info}.png"), dpi=400)
  

plt.show()