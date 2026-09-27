import random
import csv

total_records = 3200
cohorts = ["Group_1_Low", "Group_2_Mid", "Group_3_High", "Group_4_Control"]

with open("mock_preclinical_data.csv", mode="w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["Animal_ID", "Cohort", "Target_Dose_mg_kg", "Actual_Dose_mg_kg", "Notes"])
    writer.writeheader()
    
    for i in range(1, total_records + 1):
        animal_id = f"A{i:04d}"
        cohort = random.choice(cohorts)
        
        if cohort == "Group_1_Low":
            target = 2.0
        elif cohort == "Group_2_Mid":
            target = 5.0
        elif cohort == "Group_3_High":
            target = 10.0
        else:
            target = 1.0

        rand_val = random.random()
        if rand_val < 0.90:
            pct_diff = random.uniform(0.0, 4.9)
            notes = "Normal administration with minor handling variance."
        elif rand_val < 0.97:
            pct_diff = random.uniform(5.1, 9.9)
            notes = "Slight volume over-delivery due to syringe friction."
        else:
            pct_diff = random.uniform(10.5, 18.0)
            notes = "Compounding calculation error noted in morning batch formulation."

        actual = target * (1 + (pct_diff / 100.0) * random.choice([-1, 1]))
        actual = round(actual, 3)

        writer.writerow({
            "Animal_ID": animal_id,
            "Cohort": cohort,
            "Target_Dose_mg_kg": target,
            "Actual_Dose_mg_kg": actual,
            "Notes": notes
        })

print(f"Successfully generated {total_records} records in mock_preclinical_data.csv!")
