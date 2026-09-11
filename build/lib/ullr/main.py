import argparse
import pandas as pd
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import os
import sys
import time
import json
import pathlib

console = Console()


CONFIG_FILE = os.path.join(pathlib.Path.home(), ".ullr_config.json")

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

def get_default_dir():
    config = load_config()
    if "default_dir" in config and os.path.exists(config["default_dir"]):
        return config["default_dir"]
    
    from rich.prompt import Prompt
    console.print("\n[bold yellow]⚠️ First Time Setup: No default directory found.[/]")
    console.print("Where should Ullr save generated practice datasets?")
    
    while True:
        user_dir = Prompt.ask("Enter directory path").strip()
        if os.path.exists(user_dir) and os.path.isdir(user_dir):
            config["default_dir"] = user_dir
            save_config(config)
            console.print(f"[bold green]✔ Saved![/] Ullr will now save files to: {user_dir}\n")
            return user_dir
        else:
            console.print("[bold red]❌ That directory does not exist. Please try again.[/]")

def change_default_dir():
    config = load_config()
    current = config.get("default_dir", "None")
    console.print(f"\n[bold cyan]Current Default Directory:[/] {current}")
    
    from rich.prompt import Prompt
    user_dir = Prompt.ask("Enter NEW directory path (or press Enter to cancel)").strip()
    if not user_dir:
        return
        
    if os.path.exists(user_dir) and os.path.isdir(user_dir):
        config["default_dir"] = user_dir
        save_config(config)
        console.print(f"[bold green]✔ Directory Updated to:[/] {user_dir}\n")
    else:
        console.print("[bold red]❌ That directory does not exist. Update canceled.[/]")

def print_banner():

    banner = """
 ██╗   ██╗██╗     ██╗     ██████╗ 
 ██║   ██║██║     ██║     ██╔══██╗
 ██║   ██║██║     ██║     ██████╔╝
 ██║   ██║██║     ██║     ██╔══██╗
 ╚██████╔╝███████╗███████╗██║  ██║
  ╚═════╝ ╚══════╝╚══════╝╚═╝  ╚═╝
 The Offline Data Auditor
    """
    console.print(banner, style="bold cyan")

import pathlib

def find_file_globally(filename):
    if not filename or filename.strip() == "":
        return None
        
    home_dir = str(pathlib.Path.home())
    search_dirs = [
        os.path.join(home_dir, "Downloads"),
        os.path.join(home_dir, "Documents"),
        os.path.join(home_dir, "Desktop")
    ]
    
    with console.status(f"[yellow]Scanning Downloads, Documents, and Desktop for '{filename}'...[/]", spinner="dots"):
        for base_dir in search_dirs:
            if not os.path.exists(base_dir):
                continue
            for root, dirs, files in os.walk(base_dir):
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                if filename in files:
                    full_path = os.path.join(root, filename)
                    console.print(f"[bold green]Found it at:[/] {full_path}\n")
                    return full_path
            
    return None

def load_dataframe(filepath):
    """Smart loader that handles CSVs and multi-tab Excel files."""
    try:
        if filepath.lower().endswith('.csv'):
            with console.status(f"[cyan]● Loading '{os.path.basename(filepath)}'...[/]", spinner="bouncingBar"):
                time.sleep(0.6)
                return pd.read_csv(filepath)
        elif filepath.lower().endswith(('.xlsx', '.xls')):
            xls = pd.ExcelFile(filepath)
            sheet_names = xls.sheet_names
            
            if len(sheet_names) == 1:
                with console.status(f"[cyan]● Loading '{os.path.basename(filepath)}'...[/]", spinner="bouncingBar"):
                    time.sleep(0.6)
                    return pd.read_excel(xls, sheet_name=sheet_names[0])
                
            from rich.prompt import Prompt
            console.print(f"\n[bold cyan]📂 Multiple tabs detected in this Excel file![/]")
            for i, sheet in enumerate(sheet_names):
                console.print(f"  [bold green]{i+1}.[/] {sheet}")
                
            choices = [str(i+1) for i in range(len(sheet_names))]
            choice = Prompt.ask("\nWhich tab would you like to load?", choices=choices, default="1")
            selected_sheet = sheet_names[int(choice)-1]
            
            with console.status(f"[cyan]● Loading tab: '{selected_sheet}'...[/]", spinner="bouncingBar"):
                time.sleep(0.6)
                return pd.read_excel(xls, sheet_name=selected_sheet)
        else:
            console.print(f"[bold red]Error:[/] Unsupported file format. Please provide a .csv or .xlsx file.")
            return None
    except Exception as e:
        console.print(f"[bold red]Error reading file:[/] {e}")
        return None

def audit_data(filepath):
    if not os.path.exists(filepath):
        found_path = find_file_globally(os.path.basename(filepath))
        if found_path:
            filepath = found_path
        else:
            console.print(f"[bold red]Error:[/] Could not find '{os.path.basename(filepath)}' anywhere on your computer.")
            return 
        
    df = load_dataframe(filepath)
    if df is None:
        return
        
    rows, cols = df.shape
    console.print(f"\n[bold green]✅ Successfully loaded![/] {rows:,} rows, {cols} columns.\n")
    
    # Separate real data columns from 'Unnamed' ghost columns
    real_cols = [col for col in df.columns if not str(col).lower().startswith('unnamed')]
    unnamed_cols = [col for col in df.columns if str(col).lower().startswith('unnamed')]
    
    # 1. Check Missing Values (Only on real columns!)
    missing = df[real_cols].isnull().sum()
    actual_missing_cols = missing[missing > 0]
    
    # 2. Check Duplicates
    duplicates = df.duplicated().sum()
    
    # 3. Check for Invisible Spaces (Messy Text)
    text_cols = df[real_cols].select_dtypes(include=['object']).columns
    space_issues = {}
    dirty_numbers = {}
    
    for col in text_cols:
        # Find leading/trailing spaces
        mask = df[col].notna() & df[col].astype(str).str.contains(r'^\s+|\s+$', regex=True)
        spaces = mask.sum()
        if spaces > 0:
            space_issues[col] = spaces
            
        # Find numbers trapped as text (like $1,000)
        curr_mask = df[col].notna() & df[col].astype(str).str.contains(r'[\$£€,]', regex=True) & df[col].astype(str).str.contains(r'\d', regex=True)
        dirty_num = curr_mask.sum()
        if dirty_num > 0:
            dirty_numbers[col] = dirty_num
    
    # Build Output Panel
    console.print("[bold yellow]🩺 DATA HEALTH CHECK REPORT[/]")
    console.print("Here is what needs to be cleaned up before you can use this data:\n")
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("What we checked")
    table.add_column("What we found")
    table.add_column("Next Steps")
    
    if duplicates > 0:
        table.add_row("Copy-Paste Errors (Duplicates)", f"{duplicates:,} exact duplicate rows", "[bold red]Delete duplicates in Excel[/]")
    else:
        table.add_row("Copy-Paste Errors (Duplicates)", "0 duplicate rows", "[bold green]Looks Good![/]")
        
    if not actual_missing_cols.empty:
        table.add_row("Blank Cells (Missing Data)", f"Found in {len(actual_missing_cols)} columns", "[bold red]Fill in or remove blanks[/]")
    else:
        table.add_row("Blank Cells (Missing Data)", "0 blank cells", "[bold green]Looks Good![/]")
        
    if space_issues:
        table.add_row("Invisible Spaces (Messy Text)", f"Found in {len(space_issues)} columns", "[bold red]Use TRIM() in Excel[/]")
    else:
        table.add_row("Invisible Spaces (Messy Text)", "0 messy text cells", "[bold green]Looks Good![/]")
        
    if dirty_numbers:
        table.add_row("Numbers Trapped as Text", f"Found in {len(dirty_numbers)} columns", "[bold red]Remove $ or commas[/]")
    else:
        table.add_row("Numbers Trapped as Text", "0 trapped numbers", "[bold green]Looks Good![/]")
        
    console.print(table)
    
    if not actual_missing_cols.empty:
        console.print("\n[bold red]⚠️ Where to find the Blank Cells:[/]")
        for col, count in actual_missing_cols.items():
            console.print(f"  - Column [cyan]{col}[/]: {count:,} empty cells")
            
    if space_issues:
        console.print("\n[bold red]⚠️ Where to find Invisible Spaces:[/]")
        for col, count in space_issues.items():
            console.print(f"  - Column [cyan]{col}[/]: {count:,} cells have hidden spaces.")
            
    if dirty_numbers:
        console.print("\n[bold red]⚠️ Where to find Trapped Numbers:[/]")
        for col, count in dirty_numbers.items():
            console.print(f"  - Column [cyan]{col}[/]: {count:,} cells have $ or commas making them text.")
            
    if unnamed_cols:
        console.print(f"\n[bold yellow]👻 Note: We ignored {len(unnamed_cols)} 'Unnamed' columns.[/]")
        console.print("Excel sometimes creates invisible columns if you have a floating summary table off to the right side of your data. We filtered them out to keep this report clean!")
            
    if actual_missing_cols.empty and duplicates == 0 and not space_issues and not dirty_numbers:
        console.print("\n[bold green]🎉 AMAZING! Your actual data is 100% clean and ready for analysis![/]")

def generate_data():
    from rich.prompt import Prompt
    try:
        from faker import Faker
    except ImportError:
        console.print("[bold red]Faker library not installed. Run 'pip install faker' first.[/]")
        return
        
    import random
    from datetime import datetime
    import numpy as np
    
    fake = Faker()
    
    console.print("\n[bold yellow]🏭 INITIATING PRACTICE DATA ENGINE (ULLR GENERATE)...[/]")
    time.sleep(0.5)
    
    console.print("\n[bold cyan]Select an Industry Context:[/]")
    console.print("  [bold green]1.[/] E-commerce (Sales, Customers, Products)")
    console.print("  [bold blue]2.[/] Healthcare (Patients, Treatments, Costs)")
    console.print("  [bold magenta]3.[/] Real Estate (Properties, Agents, Prices)")
    console.print("  [bold yellow]4.[/] Finance & Banking (Loans, Credit Scores, Defaults)")
    console.print("  [bold cyan]5.[/] Logistics & Supply Chain (Shipments, Warehouses, Delays)")
    console.print("  [bold white]6.[/] HR & Payroll (Employees, Salaries, Attrition)")
    console.print("  [bold red]7.[/] SaaS & Tech (Subscriptions, Churn, MRR)")
    
    ind_choice = Prompt.ask("Select an option", choices=["1", "2", "3", "4", "5", "6", "7"], default="1")
    rows_choice = Prompt.ask("How many rows of dirty practice data do you need?", default="1000")
    
    try:
        rows = int(rows_choice)
    except:
        rows = 1000
        
    out_dir = get_default_dir()
    
    with console.status(f"[cyan]● Fabricating {rows:,} rows of beautifully dirty data...[/]", spinner="dots"):
        data = []
        if ind_choice == "1":
            industry = "ecommerce"
            for i in range(rows):
                data.append({
                    "Transaction_ID": fake.uuid4()[:8],
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
                    "Customer_Rating": random.randint(1, 5)
                })
        elif ind_choice == "2":
            industry = "healthcare"
            for i in range(rows):
                data.append({
                    "Patient_ID": f"PT-{fake.random_int(min=1000, max=9999)}",
                    "Patient_Name": fake.name(),
                    "Gender": random.choice(["M", "F", "Other"]),
                    "Blood_Type": random.choice(["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]),
                    "Admission_Date": fake.date_between(start_date='-2y', end_date='today').strftime('%Y-%m-%d'),
                    "Admission_Type": random.choice(["Emergency", "Elective", "Transfer", "Maternity"]),
                    "Department": random.choice(["Cardiology", "Neurology", "Oncology", "Pediatrics", "Orthopedics", "ER"]),
                    "Insurance_Provider": random.choice(["BlueCross", "Aetna", "Cigna", "Medicare", "None"]),
                    "Length_of_Stay": random.randint(1, 30),
                    "Treatment_Cost": round(random.uniform(500.0, 15000.0), 2),
                    "Discharge_Status": random.choice(["Home", "Transferred", "Rehab", "Deceased"])
                })
        elif ind_choice == "3":
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
                })
                
        df = pd.DataFrame(data)
        
        # --- INJECT DIRTY DATA ---
        cols = list(df.columns)
        
        # 1. Nulls (Missing Values)
        for col in cols:
            mask = np.random.rand(len(df)) < 0.05  # 5% missing
            df.loc[mask, col] = np.nan
            
        # 2. Invisible Spaces (Messy Text)
        text_cols = [c for c in cols if 'Name' in c or 'Category' in c or 'Type' in c or 'Department' in c]
        for col in text_cols:
            mask = np.random.rand(len(df)) < 0.15 # 15% messy text
            def add_spaces(x):
                if pd.isna(x): return x
                return ("   " + str(x)) if random.random() > 0.5 else (str(x) + "   ")
            
            df.loc[mask, col] = df.loc[mask, col].apply(add_spaces)
            
        # 3. Numbers Trapped as Text
        num_cols = [c for c in cols if 'Price' in c or 'Cost' in c]
        for col in num_cols:
            df[col] = df[col].astype('object')
            mask = np.random.rand(len(df)) < 0.20 # 20% trapped numbers
            def add_currency(x):
                if pd.isna(x): return x
                return f"${x:,.2f}" if random.random() > 0.5 else f"£{x:,.2f}"
                
            df.loc[mask, col] = df.loc[mask, col].apply(add_currency)
            
        # 4. Ghost Column
        df["Unnamed: 4"] = np.nan
        
        # Save File
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{industry}_raw_{timestamp}.csv"
        
        out_dir = get_default_dir()
        out_path = os.path.join(out_dir, filename)
        
        df.to_csv(out_path, index=False)
        time.sleep(1)
        
    console.print(f"\n[bold green]🎉 SUCCESS![/] {rows:,} rows of beautifully broken {industry} data generated.")
    console.print(f"[cyan]Saved to: {out_path}[/]")
    
    # --- DYNAMIC STAKEHOLDER BRIEF ---
    real_cols = [col for col in df.columns if not str(col).lower().startswith('unnamed')]
    numeric_cols = [c for c in df[real_cols].select_dtypes(include=['number', 'float64', 'int64']).columns.tolist() if 'id' not in c.lower() and 'zip' not in c.lower()]
    # Text cols excluding specific names that usually act as unique IDs (like Patient_Name)
    text_cols = [c for c in df[real_cols].select_dtypes(include=['object', 'string']).columns.tolist() if 'name' not in c.lower() and 'id' not in c.lower()]
    date_cols = [col for col in real_cols if 'date' in col.lower() or 'time' in col.lower() or 'year' in col.lower()]

    console.print("\n[bold magenta]👔 STAKEHOLDER BRIEF: SYSTEM REQUIREMENTS[/]")
    
    if industry == "ecommerce":
        console.print("[bold italic white]\"You are the Lead Data Analyst for a global retail brand. The Q4 board meeting is tomorrow. The VP of Sales just handed you this raw transaction dump. She needs to know which product categories are driving our revenue, if our discounts are actually working, and how our shipping status is impacting customer satisfaction.\"[/]\n")
    elif industry == "healthcare":
        console.print("[bold italic white]\"You are the Operations Analyst for Metro General Hospital. The Chief Medical Officer just handed you this month's raw admission logs. She needs to know which departments are facing the most bed shortages (length of stay), what our most expensive treatments are, and the breakdown of our patient insurance providers.\"[/]\n")
    elif industry == "realestate":
        console.print("[bold italic white]\"You are the Portfolio Analyst for a luxury real estate brokerage. The Managing Broker wants a complete breakdown of the current housing market. They need you to identify which cities are selling the most expensive properties, how HOA fees impact listing prices, and which agents are moving the most volume.\"[/]\n")
    elif industry == "finance":
        console.print("[bold italic white]\"You are a Risk Analyst at a global bank. The VP of Lending wants to know which demographic has the highest default rates, the average credit score of approved loans, and how interest rates correlate with employment status.\"[/]\n")
    elif industry == "logistics":
        console.print("[bold italic white]\"You are a Supply Chain Analyst for a massive logistics network. The Director of Operations needs you to find out which warehouses are causing the most delays, which carriers are the most expensive, and the overall lost package rate.\"[/]\n")
    elif industry == "hr":
        console.print("[bold italic white]\"You are an HR Analytics Partner. The Head of HR is worried about high turnover. They need a dashboard showing the attrition rate by department, the average salary across job titles, and if remote workers have higher performance scores.\"[/]\n")
    else:
        console.print("[bold italic white]\"You are a Product Analyst at a fast-growing tech startup. The CEO is prepping for a VC pitch. She needs to know our exact Monthly Recurring Revenue (MRR), the churn rate broken down by subscription tier, and if users who raise support tickets are more likely to cancel.\"[/]\n")

    console.print("[bold cyan]KPIs (The Top-Level Cards)[/]")
    if numeric_cols:
        for num_col in numeric_cols[:2]:
            console.print(f"  * Total {num_col.replace('_', ' ')}")
            console.print(f"  * Avg. {num_col.replace('_', ' ')}")
    else:
        console.print("  * Total Records")

    console.print("\n[bold cyan]Business Questions (The Charts & Visuals)[/]")
    if date_cols and numeric_cols:
        console.print(f"  * Time-Series Trend: How is {numeric_cols[0].replace('_', ' ')} trending based on {date_cols[0].replace('_', ' ')}? (Line Chart)")
    if text_cols and numeric_cols:
        console.print(f"  * Financial/Metric Breakdown: Which {text_cols[0].replace('_', ' ')} drives the highest {numeric_cols[0].replace('_', ' ')}? (Bar Chart)")
    if text_cols:
        console.print(f"  * Volume Breakdown: What is the distribution of total volume by {text_cols[0].replace('_', ' ')}? (Donut Chart)")
    if len(text_cols) > 1 and numeric_cols:
        console.print(f"  * Secondary Ranking: Compare {text_cols[1].replace('_', ' ')} by {numeric_cols[-1].replace('_', ' ')}? (Bar Chart)")

    console.print("\n[bold yellow]Your training mission is ready. Clean the data and build the Engine to answer these exact questions![/]")



def prompt_for_file(action_name):
    from rich.prompt import Prompt
    import glob
    
    cwd = os.getcwd()
    files = []
    for ext in ['*.csv', '*.xlsx', '*.xls']:
        files.extend(glob.glob(os.path.join(cwd, ext)))
        
    if files:
        console.print(f"\n[bold cyan]📂 Found data files in current folder:[/]")
        for i, f in enumerate(files):
            console.print(f"  [bold green]{i+1}.[/] {os.path.basename(f)}")
        console.print("  [bold yellow]0.[/] Type a manual filename or path instead")
        
        choices = [str(i) for i in range(len(files) + 1)]
        choice = Prompt.ask(f"\nSelect a file to {action_name}", choices=choices, default="1")
        
        if choice != "0":
            return files[int(choice)-1]
            
    return Prompt.ask(f"\n[bold yellow]Enter the filename or path to {action_name} (e.g., data.csv)[/]").strip()

def interactive_mode():

    from rich.prompt import Prompt
    
    print_banner()
    console.print("[bold green]Welcome to the Ullr Data Engine![/]\n")
    
    while True:
        console.print("[bold cyan]What would you like to do?[/]")
        console.print("  [bold green]1.[/] Audit Data")
        console.print("  [bold yellow]2.[/] Generate Data")
        console.print("  [bold dim]3.[/] Help Menu")
        console.print("  [bold red]4.[/] Exit")
        
        choice = Prompt.ask("\nSelect an option", choices=["1", "2", "3", "4"], default="1")
        
        if choice == "4":
            console.print("[yellow]Goodbye![/]")
            break
        elif choice == "3":
            console.print("\n[bold underline]Ullr Help Menu[/]")
            console.print("[bold green]Audit Data:[/] Scans a raw CSV/Excel file for missing values, duplicates, and formatting errors without changing the file.")
            console.print("[bold yellow]Generate Data:[/] Creates synthetic, dirty practice datasets with a Stakeholder Brief for you to practice cleaning.")
        elif choice == "2":
            generate_data()
        elif choice == "1":
            filepath = prompt_for_file("audit")
            if filepath:
                audit_data(filepath)
        
        console.print("\n" + "-"*50 + "\n")

def cli():
    parser = argparse.ArgumentParser(description="Ullr: The Offline Data Auditor")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    audit_parser = subparsers.add_parser("audit", help="Check raw data for flaws (NULLs, duplicates).")
    audit_parser.add_argument("file", help="Path to the CSV/Excel file")
    
    generate_parser = subparsers.add_parser("generate", help="Generate synthetic dirty datasets for Excel practice.")
    
    args = parser.parse_args()
    
    if not args.command:
        interactive_mode()
        sys.exit(0)
        
    print_banner()
    if args.command == "audit":
        audit_data(args.file)
    elif args.command == "generate":
        generate_data()

if __name__ == "__main__":
    cli()
