import os

file_path = "ullr/main.py"
with open(file_path, "r") as f:
    code = f.read()

# 1. Patch E-commerce
old_ecommerce = """                    "Transaction_ID": fake.uuid4()[:8],
                    "Customer_Name": fake.name(),
                    "Purchase_Date": fake.date_between(start_date='-1y', end_date='today').strftime('%Y-%m-%d'),
                    "Product_Category": random.choice(["Electronics", "Clothing", "Home", "Sports"]),
                    "Quantity": random.randint(1, 10),
                    "Unit_Price": round(random.uniform(10.0, 500.0), 2)"""

new_ecommerce = """                    "Transaction_ID": fake.uuid4()[:8],
                    "Customer_Name": fake.name(),
                    "Customer_Age": random.randint(18, 75),
                    "Customer_Country": fake.country(),
                    "Purchase_Date": fake.date_between(start_date='-1y', end_date='today').strftime('%Y-%m-%d'),
                    "Product_Category": random.choice(["Electronics", "Clothing", "Home", "Sports", "Beauty", "Toys"]),
                    "Quantity": random.randint(1, 10),
                    "Unit_Price": round(random.uniform(10.0, 500.0), 2),
                    "Discount_Applied": random.choice([0.0, 5.0, 10.0, 25.0]),
                    "Payment_Method": random.choice(["Credit Card", "PayPal", "Debit Card", "Crypto"]),
                    "Shipping_Status": random.choice(["Delivered", "Shipped", "Processing", "Cancelled"]),
                    "Customer_Rating": random.randint(1, 5)"""

code = code.replace(old_ecommerce, new_ecommerce)

# 2. Patch Healthcare
old_healthcare = """                    "Patient_ID": f"PT-{fake.random_int(min=1000, max=9999)}",
                    "Patient_Name": fake.name(),
                    "Admission_Date": fake.date_between(start_date='-2y', end_date='today').strftime('%Y-%m-%d'),
                    "Department": random.choice(["Cardiology", "Neurology", "Oncology", "Pediatrics"]),
                    "Length_of_Stay": random.randint(1, 30),
                    "Treatment_Cost": round(random.uniform(500.0, 15000.0), 2)"""

new_healthcare = """                    "Patient_ID": f"PT-{fake.random_int(min=1000, max=9999)}",
                    "Patient_Name": fake.name(),
                    "Gender": random.choice(["M", "F", "Other"]),
                    "Blood_Type": random.choice(["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]),
                    "Admission_Date": fake.date_between(start_date='-2y', end_date='today').strftime('%Y-%m-%d'),
                    "Admission_Type": random.choice(["Emergency", "Elective", "Transfer", "Maternity"]),
                    "Department": random.choice(["Cardiology", "Neurology", "Oncology", "Pediatrics", "Orthopedics", "ER"]),
                    "Insurance_Provider": random.choice(["BlueCross", "Aetna", "Cigna", "Medicare", "None"]),
                    "Length_of_Stay": random.randint(1, 30),
                    "Treatment_Cost": round(random.uniform(500.0, 15000.0), 2),
                    "Discharge_Status": random.choice(["Home", "Transferred", "Rehab", "Deceased"])"""

code = code.replace(old_healthcare, new_healthcare)

# 3. Patch Real Estate
old_realestate = """                    "Property_ID": f"RE-{fake.random_int(min=100, max=999)}",
                    "Agent_Name": fake.name(),
                    "Listing_Date": fake.date_between(start_date='-6m', end_date='today').strftime('%Y-%m-%d'),
                    "Property_Type": random.choice(["House", "Condo", "Townhouse", "Commercial"]),
                    "Square_Feet": random.randint(800, 5000),
                    "Listing_Price": round(random.uniform(150000.0, 2000000.0), 2)"""

new_realestate = """                    "Property_ID": f"RE-{fake.random_int(min=100, max=999)}",
                    "Agent_Name": fake.name(),
                    "City": fake.city(),
                    "Zip_Code": fake.zipcode(),
                    "Listing_Date": fake.date_between(start_date='-6m', end_date='today').strftime('%Y-%m-%d'),
                    "Property_Type": random.choice(["House", "Condo", "Townhouse", "Commercial", "Multi-Family"]),
                    "Year_Built": random.randint(1950, 2023),
                    "Bedrooms": random.randint(1, 6),
                    "Bathrooms": random.randint(1, 5),
                    "Square_Feet": random.randint(800, 5000),
                    "Has_Pool": random.choice(["Yes", "No"]),
                    "HOA_Fees": round(random.uniform(0.0, 500.0), 2),
                    "Listing_Price": round(random.uniform(150000.0, 2000000.0), 2)"""

code = code.replace(old_realestate, new_realestate)

with open(file_path, "w") as f:
    f.write(code)

print("Columns added successfully!")
