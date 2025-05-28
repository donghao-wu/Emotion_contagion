import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# from ace_tools import display_dataframe_to_user

# Load the batch run results
df = pd.read_csv('batch_run_results.csv')

# Display a sample of the raw data
print("Batch Run Results Sample")
print(df.head())

# Identify numeric outcome columns (excluding input parameters)
param_cols = ['width', 'height', 'density', 'seed', 'green_ratio', 'stress_ratio', 'run_number']
numeric_cols = [c for c in df.select_dtypes(include=[np.number]).columns if c not in param_cols]

# For each outcome variable, plot its mean across green_ratio for each stress_ratio
for outcome in numeric_cols:
    plt.figure()
    for sr, group in df.groupby('stress_ratio'):
        pivot = group.groupby('green_ratio')[outcome].mean().reset_index()
        plt.plot(pivot['green_ratio'], pivot[outcome], marker='o', label=f'stress_ratio={sr}')
    plt.xlabel('Green Ratio')
    plt.ylabel(outcome)
    plt.title(f'{outcome} vs Green Ratio (averaged over runs)')
    plt.legend()
    plt.tight_layout()
    plt.show()
