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

patientList = []  # LIST OF TUPLES OF PATIENT ID AND THEIR ASSIGNED PRIORITY
for patient in patients:
    if patients[patient]["Patient Age"] >= 75 and patients[patient]["Has Precondition"] == 1:
        patient_queue.put((0, patient))
    elif patients[patient]["Patient Age"] >= 60 or patients[patient]["Has Precondition"] == 1:
        patient_queue.put((1, patient))
    else:
        patient_queue.put((2, patient))
    patientList.append(patient_queue.get_nowait())
print(patientList)
"""ASSIGN DAILY CAPACITY"""
vac1_capacity = df[4].values  # VAC A CAPACITY PER DAY
vac2_capacity = df[5].values  # VAC B CAPACITY PER DAY
vac3_capacity = df[6].values  # VAC C CAPACITY PER DAY

daily_vac1_capacity = [int(x) for x in vac1_capacity if str(x) != "nan"]  # Data Cleansing
daily_vac2_capacity = [int(x) for x in vac2_capacity if str(x) != "nan"]  # Data Cleansing
daily_vac3_capacity = [int(x) for x in vac3_capacity if str(x) != "nan"]  # Data Cleansing
"""FIND AVAILABLE VACCINE"""
# for patient in patientList:
# hier geht es dann noch weiter
