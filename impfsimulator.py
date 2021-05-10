import pandas as pd
import matplotlib
from glob import glob
from queue import PriorityQueue

stock_files = sorted(glob("data/data_file_*.csv"))
patFrame = pd.read_csv("data_file_1.csv")
vacFrame = pd.read_csv("data_file_2.csv")

daily_capacity = 0  # Tägliche Impstoffkapazität

df = pd.concat([patFrame, vacFrame], axis=1, ignore_index=True)  # Kombiniere beide Frames

patient_queue = PriorityQueue()  # Erstelle Queue für alle Patienten
print(df.head())
patients = list(zip(df[1].values, df[2].values))

patient_queue.put((0, patients))
print(patient_queue.get_nowait())
for days in df[3].iteritems():  # Berechne Tägliche Kapazität
    if pd.notnull(days[1]):
        daily_capacity = df[4].values + df[5].values + df[6].values

daily_capacity = [int(x) for x in daily_capacity if str(x) != "nan"]  # Data Cleansing


def numberlist(nums, limit):
    i = 0
    while sum(nums[:i]) < limit:
        i += 1
    return i

def totalVacCap(day):
    hi = 0
    week1 = 0
    for i in daily_capacity:
        if hi <= day:
            hi += 1
            week1 += i
    print(week1)
print(f"Alle Patienten sind nach {numberlist(daily_capacity, len(patients) * 2)} Tagen geimpft.")

vac5 = 0
counter = 0
for element in daily_capacity:
    counter += 1
    if counter <= 5:
        vac5 += element
print(f"Nach fünf Tagen sind die Patienten 0 bis {vac5 - 1} geimpft.")
