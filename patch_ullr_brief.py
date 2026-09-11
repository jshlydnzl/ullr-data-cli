import os

file_path = "ullr/main.py"
with open(file_path, "r") as f:
    code = f.read()

old_brief_start = """    console.print("\\n[bold magenta]👔 STAKEHOLDER BRIEF: SYSTEM REQUIREMENTS[/]")
    console.print("[bold cyan]KPIs (The Top-Level Cards)[/]")"""

new_brief_start = """    console.print("\\n[bold magenta]👔 STAKEHOLDER BRIEF: SYSTEM REQUIREMENTS[/]")
    
    if industry == "ecommerce":
        console.print("[bold italic white]\\\"You are the Lead Data Analyst for a global retail brand. The Q4 board meeting is tomorrow. The VP of Sales just handed you this raw transaction dump. She needs to know which product categories are driving our revenue, if our discounts are actually working, and how our shipping status is impacting customer satisfaction.\\\"[/]\\n")
    elif industry == "healthcare":
        console.print("[bold italic white]\\\"You are the Operations Analyst for Metro General Hospital. The Chief Medical Officer just handed you this month's raw admission logs. She needs to know which departments are facing the most bed shortages (length of stay), what our most expensive treatments are, and the breakdown of our patient insurance providers.\\\"[/]\\n")
    else:
        console.print("[bold italic white]\\\"You are the Portfolio Analyst for a luxury real estate brokerage. The Managing Broker wants a complete breakdown of the current housing market. They need you to identify which cities are selling the most expensive properties, how HOA fees impact listing prices, and which agents are moving the most volume.\\\"[/]\\n")

    console.print("[bold cyan]KPIs (The Top-Level Cards)[/]")"""

code = code.replace(old_brief_start, new_brief_start)

with open(file_path, "w") as f:
    f.write(code)

print("Brief patched successfully!")
