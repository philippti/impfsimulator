import pandas as pd
import matplotlib
from glob import glob

stock_files = sorted(glob("data/data_file_*.csv"))

patientenFrame = pd.read_csv("data_file_1.csv")
vacFrame = pd.read_csv("data_file_2.csv")

df = pd.concat([patientenFrame, vacFrame], axis=1, ignore_index=True)

print(df.head(-1))