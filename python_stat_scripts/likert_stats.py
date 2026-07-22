import pandas as pd
import scipy.stats as stats
import os
import sys
import tkinter as tk
from tkinter import filedialog

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
trial = trial.dropna(subset=["question"])

# condition cols
trial_labels = ["control", "s_mo", "d_mo", "w_mo", "s_mls", "d_mls", "w_mls"]

# melt data to long format
trial = trial.melt(
    id_vars=["question", "participant_id"],
    value_vars=trial_labels,
    var_name="Trial",
    value_name="rating",
).dropna(subset=["rating"])

# check normality
def get_normality_stats(data_list):
    normal = True
    for i in range(len(trial_labels)):
        pval = stats.normaltest(data_list[i]).pvalue
        if pval < 0.05:
            normal = False

    if normal:
        print(f'.. Data is normal')
    else:
        print(f'.. Data is not normal')

    return normal

# Mann Whitney U stats
def get_mann_whitney_u_stats(data_list):
    for i in range(len(trial_labels)):
        for j in range(i + 1, len(trial_labels)):
            results = stats.mannwhitneyu(data_list[i],data_list[j])
            if results.pvalue < 0.05:
                stars = '*'
                if results.pvalue < 0.01:
                    stars = '**'
                if results.pvalue < 0.001:
                    stars = '***'

                print(f'...... MWU p-value between group {trial_labels[i]} and {trial_labels[j]}: {results.pvalue:.4g}, {stars}')

# T-test stats
def get_ttest_stats(data_list):
    for i in range(len(trial_labels)):
        for j in range(i + 1, len(trial_labels)):
            results = stats.ttest_ind(data_list[i],data_list[j])
            if results.pvalue < 0.05:
                stars = '*'
                if results.pvalue < 0.01:
                    stars = '**'
                if results.pvalue < 0.001:
                    stars = '***'

                print(f'...... T-test p-value between group {trial_labels[i]} and {trial_labels[j]}: {results.pvalue:.4g}, {stars}')

# Normality Tests and Other Statistical Analysis
def all_stats(measure,data_list):
    print(f'Stats for {measure}')

    normal = get_normality_stats(data_list)

    if normal:
        anova = stats.f_oneway(*data_list)
        print(f'.... ANOVA Stats: {anova.statistic:.4g}, {anova.pvalue:.4g}')
        pval_anova = anova.pvalue
        if pval_anova <= 0.05:
            get_ttest_stats(data_list)

    else:
        kw = stats.kruskal(*data_list)
        print(f'.... Kruskal Wallis Stats: {kw.statistic:.4g}, {kw.pvalue:.4g}')
        pval_kw = kw.pvalue
        if pval_kw <= 0.05:
            get_mann_whitney_u_stats(data_list)

    print('\n \n')


# control, s_mo, d_mo, w_mo, s_mls, d_mls, w_mls

# Invasive_Respectful Stats
ir = [trial.loc[(trial["question"] == 'invasive-respectful') & (trial["Trial"] == t), "rating"]
      for t in trial_labels]

all_stats("Invasive/Respectful", ir)

# Unfriendly_Friendly Stats
uf = [trial.loc[(trial["question"] == 'unfriendly-friendly') & (trial["Trial"] == t), "rating"]
      for t in trial_labels]

all_stats("Unfriendly/Friendly", uf)

# Dangerous_Safe Stats
ds = [trial.loc[(trial["question"] == 'dangerous-safe') & (trial["Trial"] == t), "rating"]
      for t in trial_labels]

all_stats("Dangerous/Safe", ds)

# Ignored_Seen Stats
isn = [trial.loc[(trial["question"] == 'ignored-seen') & (trial["Trial"] == t), "rating"]
       for t in trial_labels]

all_stats("Ignored/Seen", isn)