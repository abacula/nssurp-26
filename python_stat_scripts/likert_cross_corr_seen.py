import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import sys
import tkinter as tk
from tkinter import filedialog

target_q = 'ignored-seen'

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

print(f"Loaded: {CSV}\n")

df = pd.read_csv(CSV)
df = df.dropna(subset=['question', 'participant_id'])

# Identify condition cols
adj = input("Adjusted data based on control? y/n ")
if adj == "y":
    trial_labels = ["s_mo_adj", "d_mo_adj", "w_mo_adj", "s_mls_adj", "d_mls_adj", "w_mls_adj"]
else:
   
    trial_labels = ["control", "s_mo", "d_mo", "w_mo", "s_mls", "d_mls", "w_mls"]

# Pivot the data around participants
pivoted = df.pivot(index='participant_id', columns='question', values=trial_labels)

# Calculate the base correlation matrix across all participant rows
full_corr = pivoted.corr(method='pearson')


other_questions = [q for q in df['question'].unique() if q != target_q]

# Create a clean dense DataFrame: Rows = Conditions, Columns = Other Questions
conditioned_corr = pd.DataFrame(index=trial_labels, columns=other_questions)

for trial in trial_labels:
    for o_q in other_questions:
        target_col = (trial, target_q)
        other_col = (trial, o_q)
        
        # Verify both metric/question pairs exist in the computed matrix
        if target_col in full_corr.index and other_col in full_corr.columns:
            conditioned_corr.loc[trial, o_q] = full_corr.loc[target_col, other_col]

# Convert entries to float and drop zero-variance items that produced NaN values
conditioned_corr = conditioned_corr.astype(float).dropna(how='all', axis=0).dropna(how='all', axis=1)

print("\n" + "="*75)
print(f"MATCHING-CONDITION CORRELATION MATRIX: '{target_q.upper()}' VS OTHER QUESTIONS")
print("="*75)
print(conditioned_corr.round(2))
print("\n" + "="*75)


print(f"Strongest Inter-Question Correlations (|r| >= 0.65) [Same Condition Only]:")
has_high_corr = False

for trial in conditioned_corr.index:
    for o_q in conditioned_corr.columns:
        val = conditioned_corr.loc[trial, o_q]
        if pd.notna(val) and abs(val) >= 0.65:
            direction = "Positive" if val > 0 else "Negative"
            print(f"  • Condition '{trial}': {target_q} <---> {o_q}: {val:+.2f} ({direction})")
            has_high_corr = True
                
if not has_high_corr:
    print("  No inter-question pairings crossed the |r| >= 0.65 limit.")

print("="*75 + "\n")

get_fig = input("Get figure? y/n ")

if get_fig == "y":

    plt.figure(figsize=(10, 6))

    sns.heatmap(
        conditioned_corr, 
        annot=True, 
        cmap='coolwarm', 
        fmt=".2f", 
        vmin=-1, vmax=1, 
        linewidths=0.5,
        cbar_kws={"label": "Pearson Correlation (r)", "shrink": 0.8}
    )

    plt.title(f"Intra-Condition Correlations: '{target_q}' vs Other Questions", fontsize=13, weight='bold', pad=20)
    plt.ylabel("Trial Condition / Metric", fontsize=11, weight='bold', labelpad=10)
    plt.xlabel("Other Survey Questions", fontsize=11, weight='bold', labelpad=15)

    # Clean adjustments for horizontal X-axis text since MultiIndex strings are gone
    plt.xticks(rotation=15, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()

    if adj=="y":
        output_filename = f"figs/matching_condition_{target_q.replace('-', '_')}_adj.png"
    else:
        output_filename = f"figs/matching_condition_{target_q.replace('-', '_')}.png"
    plt.savefig(output_filename, dpi=400)
    print(f"Visual cross-heatmap saved as: '{output_filename}'")
    plt.show()