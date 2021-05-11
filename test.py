import pandas as pd
import matplotlib
from glob import glob
from queue import PriorityQueue
from collections import OrderedDict

"""PROCESS GIVEN DATA"""
stock_files = sorted(glob("data/data_file_*.csv"))
patFrame = pd.read_csv("data_file_1.csv")
vacFrame = pd.read_csv("data_file_2.csv")

daily_capacity = 0  # DAILY VACCINE CAPACITY

df = pd.concat([patFrame, vacFrame], axis=1, ignore_index=True)  # CONCATENATE BOTH DATAFRAMES

"""CREATE QUEUES"""
patient_queue = PriorityQueue()  # QUEUE FOR ALL PATIENTS

vacA1_queue = PriorityQueue()
vacB1_queue = PriorityQueue()  # QUEUES FOR 1ST VACCINATION
vacC1_queue = PriorityQueue()

vacA1_cache_queue = PriorityQueue()
vacB1_cache_queue = PriorityQueue()  # QUEUES TO WAIT 4 WEEKS
vacC1_cache_queue = PriorityQueue()

vacA2_queue = PriorityQueue()
vacB2_queue = PriorityQueue()  # QUEUES FOR 2ND VACCINATION
vacC2_queue = PriorityQueue()

immune_patients = []  # List of immune patients

"""SEGMENT PEOPLE INTO PRIORITIES"""
patients = OrderedDict()
for index, row in df[[0, 1, 2]].iterrows():
    patients.update(
        {index: {"Patient ID": index,  # THIS SHOULD PROBABLY BE A DICT COMP, (maybe df[0,1,2].to_dict('index'))
                 "Patient Age": row[1],
                 "Has Precondition": row[2]}})
print(patients[0])

for patient in patients:
    if patients[patient]["Patient Age"] >= 75 and patients[patient]["Has Precondition"] == 1:
        patient_queue.put((0, patient))
    elif patients[patient]["Patient Age"] >= 60 or patients[patient]["Has Precondition"] == 1:
        patient_queue.put((1, patient))
    else:
        patient_queue.put((2, patient))

"""ASSIGN DAILY CAPACITY"""
vac1_capacity = df[4].values  # VAC A CAPACITY PER DAY
vac2_capacity = df[5].values  # VAC B CAPACITY PER DAY
vac3_capacity = df[6].values  # VAC C CAPACITY PER DAY

daily_vac1_capacity = [int(x) for x in vac1_capacity if str(x) != "nan"]  # Data Cleansing
daily_vac2_capacity = [int(x) for x in vac2_capacity if str(x) != "nan"]  # Data Cleansing
daily_vac3_capacity = [int(x) for x in vac3_capacity if str(x) != "nan"]  # Data Cleansing
#(daily_vac1_capacity)

"""ASSIGN AVAILABLE VACCINES"""
"""VAC A"""
for days, vac_cap in enumerate(daily_vac1_capacity):
    if days < 14:
        for vac in range(vac_cap):
            vacA1_cache_queue.put(patient_queue.get())
    if days >= 42:
        vacA2_queue.put(vacA1_cache_queue.get())
        break
    else:
        for vac in range(vac_cap):
            vacA1_queue.put(patient_queue.get())
print("fertig mit daily vac 1")
"""VAC B"""
for days_2, vac_cap in enumerate(daily_vac2_capacity):
    if days_2 < 14:
        for vac in range(vac_cap):
            vacB1_queue.put(patient_queue.get())
    if days_2 >= 42:
        vacB2_queue.put(vacB1_cache_queue.get())
        print("test2")
        break
    else:
        for vac in range(vac_cap):
            vacB1_queue.put(patient_queue.get())
            print("test")
print("fertig mit daily vac 2")
"""VAC C"""
for days_3, vac_cap in enumerate(daily_vac3_capacity):
    if days_3 < 14:
        for vac in range(vac_cap):
            vacC1_queue.put(patient_queue.get())
    if days_3 >= 42:
        vacC2_queue.put(vacC1_cache_queue.get())
        break
    else:
        for vac in range(vac_cap):
            vacC1_queue.put(patient_queue.get())

while not vacA2_queue.empty():
    print(vacA2_queue.get())
