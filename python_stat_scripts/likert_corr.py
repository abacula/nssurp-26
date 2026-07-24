import pandas as pd
import scipy.stats as stats
import os
import sys
import tkinter as tk
from tkinter import filedialog
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

print(f"Loaded: {CSV}\n")

# load dataframe
trial = pd.read_csv(CSV)



# condition cols
trial_labels = ["control", "s_mo", "d_mo", "w_mo", "s_mls", "d_mls", "w_mls"]

# melt data to long format
trial = trial.melt(
    id_vars=["question", "participant_id"],
    value_vars=trial_labels,
    var_name="Trial",
    value_name="rating",
).dropna(subset=["rating"])

q_as_nums = []
for q in trial["question"]:
    if q == 'invasive-respectful':
        q_as_nums.append(1)
    elif q == 'unfriendly-friendly':
        q_as_nums.append(2)
    elif q == 'dangerous-safe':
        q_as_nums.append(3)
    elif q == 'ignored-seen':
        q_as_nums.append(4)

t_as_nums = []
for t in trial["Trial"]:
    if t == 'invasive-respectful':
        q_as_nums.append(1)
    elif q == 'unfriendly-friendly':
        q_as_nums.append(2)
    elif q == 'dangerous-safe':
        q_as_nums.append(3)
    elif q == 'ignored-seen':
        q_as_nums.append(4)


trial["question"] = q_as_nums
print(trial)

corrs = trial.corr()
sns.heatmap(corrs)
plt.show()
