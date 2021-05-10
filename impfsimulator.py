from numpy.core.numeric import NaN
import pandas as pd
import matplotlib
from glob import glob
from queue import PriorityQueue

stock_files = sorted(glob("data/data_file_*.csv"))

patientenFrame = pd.read_csv("data_file_1.csv")
vacFrame = pd.read_csv("data_file_2.csv")

df = pd.concat([patientenFrame, vacFrame], axis=1, ignore_index=True)

patient_queue = PriorityQueue()
first_vacc_queue = PriorityQueue()
second_vacc_queue = PriorityQueue()

for row in df:
    patient = (df[1], df[2])
    patient_queue.put((0, patient))

for days in df[3].iteritems():
    if pd.notnull(days[1]):
    daily_capacity = df[4] + df[5] + df[6]
    # print(daily_capacity)


