import pandas as pd
from matplotlib import pyplot as plt
from glob import glob
import random
from collections import Counter

"""PROCESS GIVEN DATA"""
stock_files = sorted(glob("data/data_file_*.csv"))
pat_frame = pd.read_csv("data_file_1.csv")
vac_frame = pd.read_csv("data_file_2.csv")

df = pd.concat([pat_frame, vac_frame], axis=1, ignore_index=True)  # Concatenate both dataframes

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


def set_priority(b=bool):  # True = w/ prio, False = w/o prio
    if b:
        for patient in patients:
            if patient["Patient Age"] >= 75 and patient["Has Precondition"] == 1:
                patient_queue.append((0, patient))
            elif patient["Patient Age"] >= 60 or patient["Has Precondition"] == 1:
                patient_queue.append((1, patient))
            else:
                patient_queue.append((2, patient))
    elif not b:
        for patient in patients:
            patient_queue.append((0, patient))


def set_capacity(x):  # 2 = B not available starting on day 100, 3 = B not available for days 100-120.
    """ASSIGN DAILY CAPACITY"""
    vac1_capacity = df[4].values  # Vac A Capacity per day
    vac2_capacity = df[5].values  # Vac B Capacity per day
    vac3_capacity = df[6].values  # Vac C Capacity per day

    daily_vac1_capacity = [int(x) for x in vac1_capacity if str(x) != "nan"]  # Data Cleansing
    daily_vac2_capacity = [int(x) for x in vac2_capacity if str(x) != "nan"]  # Data Cleansing
    daily_vac3_capacity = [int(x) for x in vac3_capacity if str(x) != "nan"]  # Data Cleansing
    if x == 2:
        daily_vac2_capacity[98:] = [0 for i in range(len(daily_vac2_capacity[98:]))]
    elif x == 3:
        daily_vac2_capacity[98:119] = [0 for i in range(len(daily_vac2_capacity[98:119]))]
    else:
        pass

    total_capacity_dict = [{"A": a, "B": b, "C": c} for (a, b, c) in
                           zip(daily_vac1_capacity, daily_vac2_capacity, daily_vac3_capacity)]
    return total_capacity_dict


def prioritize_eligible(patients, day):
    '''
    Yields a random eligible patient, starting with the highest priority patients and going down.
    Only hands back patients who are eligible for their first vaccine or who have waited long enough to be eligble for their second vaccine.
    '''
    patients = sorted(patients, key=lambda p: p[0])  # Sorts patients according to given priority.
    for patient_priority, patient in patients:
        if patient["first_vaccination_date"] is not None and patient["second_vaccination_date"] is not None:
            continue
        if patient["first_vaccination_date"] is not None and day - patient["first_vaccination_date"] < 28:
            continue
        yield patient


def run_vaccinations(days, patient_queue, total_capacity_dict, first_vac_counter, sec_vac_counter):
    '''
    Main simulator, iterates over patient_queue and assigns vaccination dates and providers.
    '''
    total_vac_capacity = Counter({"A": 0, "B": 0, "C": 0})
    for element in patients:  # Reset values for successive execution of simulations.
        element['first_vaccination_date'] = None
        element['second_vaccination_date'] = None
        element['vaccine_provider'] = None
    for day in range(min(days, len(total_capacity_dict))):
        vaccine_capacities = Counter(total_capacity_dict[day])
        total_vac_capacity += vaccine_capacities
        for patient in prioritize_eligible(patient_queue, day):
            if not any(total_vac_capacity.values()):
                continue  # Only update vaccination dates if there are vaccines remaining.

            if patient["first_vaccination_date"] == None:
                # Choose a provider/vaccine for the patient.
                provider = random.choice([k for (k, v) in total_vac_capacity.items() if
                                          v > 0])  # Choose a random provider/vaccine if it has capacity.
                patient["vaccine_provider"] = provider
                # Administer the vaccine.
                total_vac_capacity[provider] -= 1
                patient["first_vaccination_date"] = day
                first_vac_counter[day] += 1
            elif patient["second_vaccination_date"] == None and total_vac_capacity[patient["vaccine_provider"]] > 0:
                # Administer the vaccine a second time.
                total_vac_capacity[patient["vaccine_provider"]] -= 1
                patient["second_vaccination_date"] = day
                sec_vac_counter[day] += 1

    return patient_queue, total_vac_capacity  # A deep copy of whatever data we want, I'd recommend the day, the patients list, and the vaccine capacities list.


def visualization():
    labels = 'Risikogruppe 1', 'Risikogruppe 2', 'Riskiogruppe 3'
    patients_zero_prio = [x["Patient ID"] for prio, x in patient_queue if prio == 0]
    patients_one_prio = [x["Patient ID"] for prio, x in patient_queue if prio == 1]
    patients_two_prio = [x["Patient ID"] for prio, x in patient_queue if prio == 2]
    sizes = [len(patients_zero_prio), len(patients_one_prio), len(patients_two_prio)]

    fig, ax1 = plt.subplots()
    ax1.pie(sizes, labels=labels, autopct='%1.2f%%',
            shadow=True)

    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.title("Wie viel Prozent der Bev??lkerung sind in den \n jeweiligen Risikogruppen\n")
    plt.show()


def szenario_A():
    # Szenario A: No priorization

    """ADDITIONAL DECLARATIONS"""
    first_vac_counter = {i: 0 for i in range(487)}
    sec_vac_counter = {i: 0 for i in range(487)}

    set_priority(False)
    total_capacity_dict = set_capacity(1)
    run_vaccinations(487, patient_queue, total_capacity_dict, first_vac_counter, sec_vac_counter)

    print(
        "\nSimulationsbedingung: es gibt keine Priorisierung der Patienten nach Risikogruppen und entsprechend nur eine Warteliste")

    print("\na) Nach wie vielen Tagen sind alle Patienten geimpft?")
    print("\nAn Tag", list(first_vac_counter.values()).index(0), "haben alle ihre erste Impfung erhalten.")
    print("\nAlle Patienten haben ihre Zweitimpfung an Tag:",
          max(patient["second_vaccination_date"] for patient in patients if patient["second_vaccination_date"]))

    print("\nb) Welche Patienten werden innerhalb der ersten 5 Tage geimpft?")
    patients_first_five_days = [x["Patient ID"] for prio, x in patient_queue if x["first_vaccination_date"] <= 4]
    print('\nNach f??nf Tagen wurden Patienten:', patients_first_five_days, "geimpft")
    print("\nc) wann erh??lt Patient 17.909 die Zweitimpfung?")

    print('\nPatient Nr', patients[17909]["Patient ID"], 'erh??lt an Tag', patients[17909]["second_vaccination_date"],
          'seine zweite Impfung')


def szenario_B():
    # Szenario B: Prioritizing according to risk groups 1 and 2

    """ADDITIONAL DECLARATIONS"""
    first_vac_counter = {i: 0 for i in range(487)}
    sec_vac_counter = {i: 0 for i in range(487)}

    set_priority(True)
    total_capacity_dict = set_capacity(1)

    run_vaccinations(487, patient_queue, total_capacity_dict, first_vac_counter, sec_vac_counter)

    print(
        "\n a) Erstellen Sie eine geeignete Visualisierung der Bev??lkerungsanteile in den verschiedenen Risikogruppen (aus den Datensets)")
    visualization()

    print("\n b) Nach wie vielen Tagen sind alle Patienten geimpft?")
    print("\n An Tag", list(first_vac_counter.values()).index(0), "haben alle ihre erste Impfung erhalten.")
    print("\n Alle Patienten haben ihre Zweitimpfung an Tag:",
          max(patient["second_vaccination_date"] for patient in patients if patient["second_vaccination_date"]))

    print("\n c) Welche Patienten werden innerhalb der ersten 5 Tage geimpft?")
    patients_first_five_days = [x["Patient ID"] for prio, x in patient_queue if x["first_vaccination_date"] <= 4]
    print('\n Nach f??nf Tagen wurden Patienten:', patients_first_five_days, "geimpft")

    print("\n d) Wann erh??lt Patient 17.909 die Zweitimpfung?")

    print('\n Patient Nr', patients[17909]["Patient ID"], 'erh??lt an Tag', patients[17909]["second_vaccination_date"],
          'seine zweite Impfung')

    print('\n e) Wann erhalten jeweils alle Patienten aus Risikogruppe 1 und 2 ihre Erstimpfung?')

    print('\n Aus Risikogruppe 1 wurden alle nach Tag',
          max(patient['first_vaccination_date'] for prio, patient in patient_queue if prio == 0), 'geimpft')
    print('\n Aus Risikogruppe 2 wurden alle nach Tag',
          max(patient['first_vaccination_date'] for prio, patient in patient_queue if prio == 1), 'geimpft')

    print('\n f) Wie sehen diese Zahlen von b-d im Vergleich zu a-c aus Szenario A aus?')
    print('''\n 
    Die Zeit, bis alle ihre erste Impfung erhalten haben ist in Szenario B gleich wie in Szenario A. Ebenso die Zweitimpfung. Es wurde nur die Reihenfolge\n
    entsprechend der Priorit??t ge??ndert. Die Patienten, die in den ersten f??nf Tagen geimpft werden, sind entsprechend die Patienten aus den Risikogruppen in Szenario B.\n
    In Szenario A geht es einfach der Reihenfolge nach von Patient 0 aus los.\n
    F??r Patient 17909 verschiebt sich die Zweitimpfung von Tag 161 auf Tag 239.''')


def szenario_Ca():
    """ADDITIONAL DECLARATIONS"""
    first_vac_counter = {i: 0 for i in range(487)}
    sec_vac_counter = {i: 0 for i in range(487)}

    set_priority(True)
    total_capacity_dict = set_capacity(2)
    run_vaccinations(487, patient_queue, total_capacity_dict, first_vac_counter, sec_vac_counter)

    print('\n a) Nach wie vielen Tagen sind alle Patienten geimpft?')
    print("\n An Tag", list(first_vac_counter.values()).index(0), "haben alle ihre erste Impfung erhalten.")


def szenario_Cb():
    """ADDITIONAL DECLARATIONS"""
    first_vac_counter = {i: 0 for i in range(487)}
    sec_vac_counter = {i: 0 for i in range(487)}

    set_priority(True)
    total_capacity_dict = set_capacity(3)
    run_vaccinations(487, patient_queue, total_capacity_dict, first_vac_counter, sec_vac_counter)

    print('\n b) Wie ver??ndert sich a), wenn die Zulassung f??r Anbieter B an Tag 120 wieder erteilt wird?')
    print("\n An Tag", list(first_vac_counter.values()).index(0), "haben alle ihre erste Impfung erhalten.")


# ATTENTION! Please run each scenario seperately to avoid data collision.
# szenario_A()
szenario_B()
# szenario_Ca()
# szenario_Cb()
