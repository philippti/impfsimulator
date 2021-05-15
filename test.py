import pandas as pd
from matplotlib import pyplot as plt
from glob import glob
import random
from collections import Counter, defaultdict

"""PROCESS GIVEN DATA"""
stock_files = sorted(glob("data/data_file_*.csv"))
patFrame = pd.read_csv("data_file_1.csv")
vacFrame = pd.read_csv("data_file_2.csv")

df = pd.concat([patFrame, vacFrame], axis=1, ignore_index=True)  # Concatenate both dataframes

"""CREATE QUEUES"""
patient_queue = []  # List for all patients

"""SEGMENT PEOPLE INTO PRIORITIES"""
patients = []
for index, row in df[[0, 1, 2]].iterrows():
    patients.append({"Patient ID": index,
                     "Patient Age": row[1],
                     "Has Precondition": row[2],
                     "first_vaccination_date": None,
                     "second_vaccination_date": None,
                     "vaccine_provider": None})

def setPriority(b=True): #True= mit Prio, False= ohne Prio
    if b == True:
        prio0, prio1, prio2 = 0,1,2
    elif b == False:
        prio0, prio1, prio2 = 0,0,0

    for patient in patients:
        if patient["Patient Age"] >= 75 and patient["Has Precondition"] == 1:
            patient_queue.append((prio0, patient))
        elif patient["Patient Age"] >= 60 or patient["Has Precondition"] == 1:
            patient_queue.append((prio1, patient))
        else:
            patient_queue.append((prio2, patient))

def setCapacity(x=1): #1= default, 2= B ab Tag 100 nicht verfügbar, 3= B Tag 100-120 nicht verfügbar
    """ASSIGN DAILY CAPACITY"""
    vac1_capacity = df[4].values  # Vac A Capacity per day
    vac2_capacity = df[5].values  # Vac B Capacity per day
    vac3_capacity = df[6].values  # Vac C Capacity per day

    daily_vac1_capacity = [int(x) for x in vac1_capacity if str(x) != "nan"]  # Data Cleansing
    daily_vac2_capacity = [int(x) for x in vac2_capacity if str(x) != "nan"]  # Data Cleansing
    daily_vac3_capacity = [int(x) for x in vac3_capacity if str(x) != "nan"]  # Data Cleansing
    if x == 2:
        daily_vac2_capacity[99:] = [0 for i in range(len(daily_vac2_capacity[99:]))]
    elif x == 3:
        daily_vac2_capacity[99:120] = [0 for i in range(len(daily_vac2_capacity[99:120]))]
    else:
        pass

    total_capacity_dict = [{"A": a, "B": b, "C": c} for (a, b, c) in
                        zip(daily_vac1_capacity, daily_vac2_capacity, daily_vac3_capacity)]
    return total_capacity_dict

"""ADDITIONAL DECLARATIONS"""
first_vac_counter = {i:0 for i in range(305)}
sec_vac_counter = {i:0 for i in range(305)}


def prioritize_eligible(patients, day):
    '''
    Yields a random eligible patient, starting with the highest priority patients and going down.
    Only hands back patients who are eligible for their first vaccine or who have waited long enough to be eligble for their second vaccine.
    '''
    patients = sorted(patients, key=lambda p: p[0])
    for patient_priority, patient in patients:
        if patient["first_vaccination_date"] is not None and patient["second_vaccination_date"] is not None:
            continue
        if patient["first_vaccination_date"] is not None and day - patient["first_vaccination_date"] < 28:
            continue
        yield patient



def run_vaccinations(days, patient_queue):
    total_vac_capacity = Counter({"A": 0, "B": 0, "C": 0})
    for day in range(min(days, len(total_capacity_dict))):
        vaccine_capacities = Counter(total_capacity_dict[day])
        total_vac_capacity += vaccine_capacities
        for patient in prioritize_eligible(patient_queue, day):
            if not any(total_vac_capacity.values()):
                continue  # Only update vaccination dates if there are vaccines remaining.

            if not patient["first_vaccination_date"]:
                # Choose a provider/vaccine for the patient.
                provider = random.choice([k for (k, v) in total_vac_capacity.items() if
                                          v > 0])  # Choose a random provider/vaccine if it has capacity.
                patient["vaccine_provider"] = provider
                # Administer the vaccine.
                total_vac_capacity[provider] -= 1
                patient["first_vaccination_date"] = day
                first_vac_counter[day] += 1
            elif not patient["second_vaccination_date"] and total_vac_capacity[patient["vaccine_provider"]] > 0:
                # Administer the vaccine a second time.
                total_vac_capacity[patient["vaccine_provider"]] -= 1
                patient["second_vaccination_date"] = day
                sec_vac_counter[day] += 1

    return patient_queue, total_vac_capacity  # A deep copy of whatever data we want, I'd recommend the day, the patients list, and the vaccine capacities list.


def main(patient_queue):
    report, capacity = run_vaccinations(305, patient_queue)
    low_priority_patients = [(p["Patient ID"], p["first_vaccination_date"], p["second_vaccination_date"]) for pi, p in report if p["first_vaccination_date"] == 100]
    print(capacity)
    import pprint  # Can be removed if needed
    pprint.pprint(low_priority_patients)

    # Every day's relevant data is available in that report.
    # You can also call list on run_vaccinations and get the reports for every day so you can run analyses on them @Shara
    # Converting this to be more efficient using pandas/dataframes is an option, but only if Shara wants to :)


#main(patient_queue)
setPriority(False)
total_capacity_dict = setCapacity()
run_vaccinations(305, patient_queue)
plt.plot(range(305),first_vac_counter.values())
plt.plot(range(305),sec_vac_counter.values())
print("All patients have received their 2nd vacc on day", list(sec_vac_counter.values()).index(0))
#for patient in patient_queue
#plt.plot(range)

def szenarioA():
    # Szenario A: 

print("Simulationsbedingung: es gibt keine Priorisierung der Patienten nach Risikogruppen und entsprechend nur eine Warteliste\n")

print("a) Nach wie vielen Tagen sind alle Patienten geimpft?\n")
print("Am Tag", list(first_vac_counter.values()).index(0), "haben alle ihre erste Impfung erhalten.\n")

print("b) Welche Patienten werden innerhalb der ersten 5 Tage geimpft?\n")

c) wann erhält Patient 17.909 die Zweitimpfung?
