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

extra_info = ""
# condition cols
adj = input("Adjusted data based on control? y/n ")
if adj=="y":
    extra_info = "_adj"
    CONDITIONS = ["s_mo_adj", "d_mo_adj", "w_mo_adj", "s_mls_adj", "d_mls_adj", "w_mls_adj"]
else:
    avg = input("Just avg? y/n ")
    if avg=="y":
        extra_info = "_avg"
        CONDITIONS = ["control", "mo_avg", "mls_avg"]
    else:
        CONDITIONS = ["control", "s_mo", "d_mo", "w_mo", "s_mls", "d_mls", "w_mls"]


# x-axis labels
LABELS = {
    "control":  "Control",
    "s_mo":     "Slow\n(motion)",
    "d_mo":     "Dodge\n(motion)",
    "w_mo":     "Wave\n(motion)",
    "s_mls":    "Slow\n(multimodal)",
    "d_mls":    "Dodge\n(multimodal)",
    "w_mls":    "Wave\n(multimodal)",
    "s_mo_adj":     "Slow\n(motion)",
    "d_mo_adj":     "Dodge\n(motion)",
    "w_mo_adj":     "Wave\n(motion)",
    "s_mls_adj":    "Slow\n(multimodal)",
    "d_mls_adj":    "Dodge\n(multimodal)",
    "w_mls_adj":    "Wave\n(multimodal)",
    "mo_avg":   "Average (motion)",
    "mls_avg":  "Average (multimodal)",
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
    if adj=="y":
        ax.set_yticks([-4,-3,-2,-1,0,1,2,3,4])
    else:
        ax.set_yticks([1, 2, 3, 4, 5])
    if low and adj!="y":
        ax.set_yticklabels(y_tick_labels(low, high))
    ax.set_ylabel("")

    ax.set_xticks(range(len(CONDITIONS)))
    ax.set_xticklabels([LABELS[c] for c in CONDITIONS])
    ax.set_xlabel("Trial Type")

    ax.set_title(f"{q} by Trial Type")
    ax.grid(axis="y", linestyle="--", alpha=0.7)
    ax.set_axisbelow(True)

    fig.tight_layout()
  
    fig.savefig(os.path.join(OUTDIR, f"figs/plot_{q}{extra_info}.png"), dpi=400)
  

plt.show()