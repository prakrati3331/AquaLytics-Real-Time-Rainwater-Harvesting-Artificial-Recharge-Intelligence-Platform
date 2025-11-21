import pandas as pd
import glob

# path to your csv files
files = sorted(glob.glob("databases/groundwater*.csv"))

dfs = [pd.read_csv(f) for f in files]
combined = pd.concat(dfs, ignore_index=True)

# save combined file
combined.to_csv("databases/groundwater_combined.csv", index=False)

print("Combined CSV created:", "databases/groundwaterCombined.csv")