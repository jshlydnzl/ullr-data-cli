import os

file_path = "ullr/main.py"
with open(file_path, "r") as f:
    code = f.read()

# 1. Update Menu
old_menu = """    console.print("\\n[bold cyan]Select an Industry Context:[/]")
    console.print("  [bold green]1.[/] E-commerce (Sales, Customers, Products)")
    console.print("  [bold blue]2.[/] Healthcare (Patients, Treatments, Costs)")
    console.print("  [bold magenta]3.[/] Real Estate (Properties, Agents, Prices)")
    
    ind_choice = Prompt.ask("Select an option", choices=["1", "2", "3"], default="1")"""

new_menu = """    console.print("\\n[bold cyan]Select an Industry Context:[/]")
    console.print("  [bold green]1.[/] E-commerce (Sales, Customers, Products)")
    console.print("  [bold blue]2.[/] Healthcare (Patients, Treatments, Costs)")
    console.print("  [bold magenta]3.[/] Real Estate (Properties, Agents, Prices)")
    console.print("  [bold yellow]4.[/] Finance & Banking (Loans, Credit Scores, Defaults)")
    console.print("  [bold cyan]5.[/] Logistics & Supply Chain (Shipments, Warehouses, Delays)")
    console.print("  [bold white]6.[/] HR & Payroll (Employees, Salaries, Attrition)")
    console.print("  [bold red]7.[/] SaaS & Tech (Subscriptions, Churn, MRR)")
    
    ind_choice = Prompt.ask("Select an option", choices=["1", "2", "3", "4", "5", "6", "7"], default="1")"""

code = code.replace(old_menu, new_menu)

# 2. Add data generation logic
old_data_gen = """        else:
            industry = "realestate"
            for i in range(rows):
                data.append({
                    "Property_ID": f"RE-{fake.random_int(min=100, max=999)}",
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
                    "Listing_Price": round(random.uniform(150000.0, 2000000.0), 2)
                })"""

new_data_gen = """        elif ind_choice == "3":
            industry = "realestate"
            for i in range(rows):
                data.append({
                    "Property_ID": f"RE-{fake.random_int(min=100, max=999)}",
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
                    "Listing_Price": round(random.uniform(150000.0, 2000000.0), 2)
                })
        elif ind_choice == "4":
            industry = "finance"
            for i in range(rows):
                data.append({
                    "Loan_ID": f"LN-{fake.random_int(min=10000, max=99999)}",
                    "Customer_Name": fake.name(),
                    "Credit_Score": random.randint(300, 850),
                    "Annual_Income": round(random.uniform(30000.0, 250000.0), 2),
                    "Loan_Amount": round(random.uniform(5000.0, 100000.0), 2),
                    "Interest_Rate": round(random.uniform(2.5, 15.0), 2),
                    "Loan_Term_Months": random.choice([12, 36, 60, 72]),
                    "Employment_Status": random.choice(["Employed", "Unemployed", "Self-Employed", "Retired"]),
                    "Default_Status": random.choice(["Yes", "No", "No", "No", "No"]),
                    "Approval_Date": fake.date_between(start_date='-3y', end_date='today').strftime('%Y-%m-%d')
                })
        elif ind_choice == "5":
            industry = "logistics"
            for i in range(rows):
                data.append({
                    "Tracking_ID": f"TRK{fake.uuid4()[:8].upper()}",
                    "Warehouse_Location": fake.city(),
                    "Destination_City": fake.city(),
                    "Weight_kg": round(random.uniform(0.5, 150.0), 2),
                    "Carrier": random.choice(["FedEx", "UPS", "DHL", "USPS", "Prime"]),
                    "Shipping_Cost": round(random.uniform(5.0, 300.0), 2),
                    "Expected_Delivery": fake.date_between(start_date='-1y', end_date='today').strftime('%Y-%m-%d'),
                    "Status": random.choice(["On Time", "Delayed", "Lost", "Damaged"]),
                    "Fragile": random.choice(["Yes", "No"]),
                    "Distance_km": random.randint(10, 3000)
                })
        elif ind_choice == "6":
            industry = "hr"
            for i in range(rows):
                data.append({
                    "Employee_ID": f"EMP-{fake.random_int(min=1000, max=9999)}",
                    "Employee_Name": fake.name(),
                    "Department": random.choice(["Engineering", "Sales", "Marketing", "HR", "Finance", "Legal"]),
                    "Job_Title": fake.job(),
                    "Hire_Date": fake.date_between(start_date='-10y', end_date='today').strftime('%Y-%m-%d'),
                    "Annual_Salary": round(random.uniform(40000.0, 200000.0), 2),
                    "Performance_Score": random.randint(1, 5),
                    "Remote_Status": random.choice(["Remote", "Hybrid", "Office"]),
                    "Years_at_Company": random.randint(0, 15),
                    "Attrition": random.choice(["Active", "Resigned", "Terminated", "Active", "Active"])
                })
        else:
            industry = "saas"
            for i in range(rows):
                data.append({
                    "User_ID": f"USR-{fake.uuid4()[:6]}",
                    "Subscription_Tier": random.choice(["Free", "Pro", "Enterprise", "Pro"]),
                    "Signup_Date": fake.date_between(start_date='-4y', end_date='today').strftime('%Y-%m-%d'),
                    "Monthly_Revenue": random.choice([0.0, 29.99, 99.99, 499.99]),
                    "Last_Login_Date": fake.date_between(start_date='-1m', end_date='today').strftime('%Y-%m-%d'),
                    "Total_Logins": random.randint(1, 500),
                    "Support_Tickets": random.randint(0, 15),
                    "Churned": random.choice(["Yes", "No", "No", "No"]),
                    "Country": fake.country()
                })"""

code = code.replace(old_data_gen, new_data_gen)

# 3. Add to Stakeholder Brief
old_brief = """    elif industry == "healthcare":
        console.print("[bold italic white]\\\"You are the Operations Analyst for Metro General Hospital. The Chief Medical Officer just handed you this month's raw admission logs. She needs to know which departments are facing the most bed shortages (length of stay), what our most expensive treatments are, and the breakdown of our patient insurance providers.\\\"[/]\\n")
    else:
        console.print("[bold italic white]\\\"You are the Portfolio Analyst for a luxury real estate brokerage. The Managing Broker wants a complete breakdown of the current housing market. They need you to identify which cities are selling the most expensive properties, how HOA fees impact listing prices, and which agents are moving the most volume.\\\"[/]\\n")"""

new_brief = """    elif industry == "healthcare":
        console.print("[bold italic white]\\\"You are the Operations Analyst for Metro General Hospital. The Chief Medical Officer just handed you this month's raw admission logs. She needs to know which departments are facing the most bed shortages (length of stay), what our most expensive treatments are, and the breakdown of our patient insurance providers.\\\"[/]\\n")
    elif industry == "realestate":
        console.print("[bold italic white]\\\"You are the Portfolio Analyst for a luxury real estate brokerage. The Managing Broker wants a complete breakdown of the current housing market. They need you to identify which cities are selling the most expensive properties, how HOA fees impact listing prices, and which agents are moving the most volume.\\\"[/]\\n")
    elif industry == "finance":
        console.print("[bold italic white]\\\"You are a Risk Analyst at a global bank. The VP of Lending wants to know which demographic has the highest default rates, the average credit score of approved loans, and how interest rates correlate with employment status.\\\"[/]\\n")
    elif industry == "logistics":
        console.print("[bold italic white]\\\"You are a Supply Chain Analyst for a massive logistics network. The Director of Operations needs you to find out which warehouses are causing the most delays, which carriers are the most expensive, and the overall lost package rate.\\\"[/]\\n")
    elif industry == "hr":
        console.print("[bold italic white]\\\"You are an HR Analytics Partner. The Head of HR is worried about high turnover. They need a dashboard showing the attrition rate by department, the average salary across job titles, and if remote workers have higher performance scores.\\\"[/]\\n")
    else:
        console.print("[bold italic white]\\\"You are a Product Analyst at a fast-growing tech startup. The CEO is prepping for a VC pitch. She needs to know our exact Monthly Recurring Revenue (MRR), the churn rate broken down by subscription tier, and if users who raise support tickets are more likely to cancel.\\\"[/]\\n")"""

code = code.replace(old_brief, new_brief)

with open(file_path, "w") as f:
    f.write(code)

print("More industries added!")
