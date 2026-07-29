import pandas as pd
import scipy.stats as stats
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
trial = trial.dropna(subset=["question"])

extra_info = ""

# condition cols
adj = input("Adjusted data based on control? y/n ")
if adj=="y":
    extra_info = "_adj"
    trial_labels = ["s_mo_adj", "d_mo_adj", "w_mo_adj", "s_mls_adj", "d_mls_adj", "w_mls_adj"]
else:
    avg = input("Just avg? y/n ")
    if avg=="y":
        extra_info = "_avg"
        trial_labels = ["control", "mo_avg", "mls_avg"]
    else:
        trial_labels = ["control", "s_mo", "d_mo", "w_mo", "s_mls", "d_mls", "w_mls"]

rating_cols = trial_labels

trial["gender"] = trial["gender"].astype('category').cat.codes
trial["age"] = trial["age"].astype('category').cat.codes

demographic_cols = ["age","gender","see_robots","interact_robots","robot_attitude","tech_comfort"]


print(f"Ratings Columns: {rating_cols}")
print(f"Demographics Columns: {demographic_cols}\n")
print("~" * 70)
print("~" * 70)

unique_questions = trial["question"].unique()

for q in unique_questions:
    print(f"CORRELATION FOR {q}")
    

    q_trial = trial[trial['question'] == q]

    ratings = [r for r in rating_cols]
    demographics = [d for d in demographic_cols]

    all_corr = q_trial[ratings + demographics].corr(method='pearson')

    cross_corr = all_corr.loc[ratings, demographics]

    print("Key Demographic Influences (|r| >= 0.50):")
    has_impact = False
    
    
    for rating_var in cross_corr.index:
        for demo_var in cross_corr.columns:
            val = cross_corr.loc[rating_var, demo_var]
            if abs(val) >= 0.50:
                direction = "higher ratings" if val > 0 else "lower ratings"
                print(f" As {demo_var} increases, {rating_var} tends to have {direction} (r = {val:+.2f})")
                has_impact = True
    
    if not has_impact:
        print("  No demographic traits crossed the |r| >= 0.50 threshold for this question.")

    print("~" * 70)

    get_fig = input("Get figures? y/n ")

    if get_fig=="y":
        plt.figure(figsize=(10, 6))
            
        sns.heatmap(
            cross_corr, 
            annot=True, 
            cmap='coolwarm', 
            fmt=".2f", 
            vmin=-1, vmax=1, 
            linewidths=0.8,
            cbar_kws={"label": "Correlation Coefficient (r)"}
        )
            
        plt.title(f'Correlation between Demographics and Ratings\n[Question: {q}]', fontsize=12, weight='bold', pad=15)
        plt.xlabel('Demographic Variables', fontsize=10, weight='bold', labelpad=10)
        plt.ylabel('Question Rating Variables', fontsize=10, weight='bold', labelpad=10)
        plt.tight_layout()
        
        # Save independent plot image file
        clean_filename = "".join([c if c.isalnum() else "_" for c in q])
        output_image = f'figs/demo_corr_{clean_filename}{extra_info}.png'
        plt.savefig(output_image, dpi=400)
        plt.close()
            
        