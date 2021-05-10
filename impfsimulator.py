import pandas as pd
import matplotlib
from glob import glob

stock_files = sorted(glob("data/data_file_*.csv"))

df = pd.concat((pd.read_csv(file).assign(filename=file)
           for file in stock_files), ignore_index=True)

print(df.head())
