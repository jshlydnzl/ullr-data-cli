import os

file_path = "ullr/main.py"
with open(file_path, "r") as f:
    code = f.read()

# 1. Patch analyze_data
old_analyze = """    # 3. Dynamic Dashboard Layout
    from rich.prompt import Prompt
    console.print("\\n[bold cyan]🛠️ Dashboard Construction[/]")
    console.print("I can provide step-by-step instructions for building this dashboard.")
    console.print("  [1] Microsoft Excel")
    console.print("  [2] Tableau")
    console.print("  [3] Power BI")
    console.print("  [4] Google Looker Studio")
    bi_choice = Prompt.ask("Select your BI Tool", choices=["1", "2", "3", "4"], default="1")
    
    bi_name = {"1": "Excel", "2": "Tableau", "3": "Power BI", "4": "Looker Studio"}[bi_choice]
    console.print(f"\\n[bold yellow]🏗️ Recommended Dashboard Layout (How to build in {bi_name}):[/]")"""

new_analyze = """    # 3. Dynamic Dashboard Layout
    console.print("\\n[bold cyan]🛠️ Dashboard Construction[/]")
    
    bi_choice = "1"
    bi_name = "Excel"
    console.print(f"\\n[bold yellow]🏗️ Recommended Dashboard Layout (How to build in {bi_name}):[/]")"""

code = code.replace(old_analyze, new_analyze)

# 2. Patch clean_data
old_clean = """    # Prompt user for output format
    from rich.prompt import Prompt
    console.print("\\n[bold cyan]💾 How would you like to save the cleaned data?[/]")
    console.print("  [bold green]1.[/] Excel Workbook (.xlsx) - Best for Dashboards & formatting")
    console.print("  [bold blue]2.[/] Raw CSV (.csv) - Best for PostgreSQL Bulk Imports")
    console.print("  [bold magenta]3.[/] JSON (.json) - Best for Web Apps & APIs")
    
    save_choice = Prompt.ask("Select output format", choices=["1", "2", "3"], default="1")
    base, ext = os.path.splitext(filepath)"""

new_clean = """    # Save automatically
    base, ext = os.path.splitext(filepath)
    save_choice = "1" # Default to Excel"""

code = code.replace(old_clean, new_clean)

with open(file_path, "w") as f:
    f.write(code)

print("Prompts removed successfully!")
