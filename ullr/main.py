import argparse
import pandas as pd
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import os
import sys
import time

console = Console()

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
    # pathlib.Path.home() natively handles Windows (C:\Users\Name), macOS (/Users/Name), and Linux (/home/Name)
    home_dir = str(pathlib.Path.home())
    
    with console.status(f"[yellow]Scanning your computer for '{filename}'...[/]", spinner="dots"):
        for root, dirs, files in os.walk(home_dir):
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

def analyze_data(filepath):
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

    if df.empty:
        console.print("[bold red]Data is empty![/]")
        return
        
    # Filter out Ghost Data for analysis
    real_cols = [col for col in df.columns if not str(col).lower().startswith('unnamed')]
    numeric_cols = df[real_cols].select_dtypes(include=['number']).columns.tolist()
    text_cols = df[real_cols].select_dtypes(include=['object', 'category']).columns.tolist()
    date_cols = [col for col in real_cols if 'date' in col.lower() or 'time' in col.lower() or 'year' in col.lower()]

    console.print("\n[bold yellow]📊 FULL DASHBOARD BLUEPRINT[/]\n")
    
    # 1. Executive Summary
    console.print("[bold cyan]🧠 Executive Summary[/]")
    console.print(f"  - We analyzed [bold]{len(df):,}[/] rows of clean data.")
    
    if numeric_cols:
        primary_num = numeric_cols[0]
        console.print(f"  - Your total [bold cyan]{primary_num}[/] generated is [bold green]{df[primary_num].sum():,.2f}[/].")
        
    if text_cols:
        # Find a categorical column that has a few distinct groups (like Price_Tier)
        good_cats = [col for col in text_cols if 1 < df[col].nunique() <= 10]
        if good_cats:
            best_cat = good_cats[0]
            top_val = df[best_cat].value_counts().index[0]
            top_pct = (df[best_cat].value_counts().iloc[0] / len(df)) * 100
            console.print(f"  - [bold cyan]{top_val}[/] is your dominant {best_cat}, making up [bold green]{top_pct:.1f}%[/] of the entire dataset.")
    console.print("")

    # 2. Key Metrics
    if numeric_cols:
        console.print("[bold cyan]💰 Money & Numbers (Totals and Averages)[/]")
        num_table = Table(show_header=True, header_style="bold magenta")
        num_table.add_column("Data Column")
        num_table.add_column("Grand Total")
        num_table.add_column("Average (Mean)")
        num_table.add_column("Lowest Value")
        num_table.add_column("Highest Value")
        
        for col in numeric_cols:
            if "id" not in col.lower() and "zip" not in col.lower():
                total = f"{df[col].sum():,.2f}"
                avg = f"{df[col].mean():,.2f}"
                min_val = f"{df[col].min():,.2f}"
                max_val = f"{df[col].max():,.2f}"
                num_table.add_row(col, total, avg, min_val, max_val)
        console.print(num_table)
        console.print("")

    # 3. Dynamic Dashboard Layout
    from rich.prompt import Prompt
    console.print("\n[bold cyan]🛠️ Dashboard Construction[/]")
    console.print("I can provide step-by-step instructions for building this dashboard.")
    console.print("  [1] Microsoft Excel")
    console.print("  [2] Tableau")
    console.print("  [3] Power BI")
    console.print("  [4] Google Looker Studio")
    bi_choice = Prompt.ask("Select your BI Tool", choices=["1", "2", "3", "4"], default="1")
    
    bi_name = {"1": "Excel", "2": "Tableau", "3": "Power BI", "4": "Looker Studio"}[bi_choice]
    console.print(f"\n[bold yellow]🏗️ Recommended Dashboard Layout (How to build in {bi_name}):[/]")
    
    if numeric_cols:
        kpis = ", ".join([f"Total {c}" for c in numeric_cols[:2]])
        console.print(f"  [bold green]Top (KPI Cards):[/] Put large, bold text showing {kpis} at the very top of your dashboard.")
        if bi_choice == "1":
            console.print(f"      [dim]↳ Steps: Insert Shapes (Rounded Rectangles) -> Click formula bar -> Type '=' and click the Grand Total in your Pivot Table.[/dim]")
        elif bi_choice == "2":
            console.print(f"      [dim]↳ Steps: Create New Sheet -> Drag your field to the 'Text' box on the Marks card -> Format font size.[/dim]")
        elif bi_choice == "3":
            console.print(f"      [dim]↳ Steps: Visualizations Pane -> Click 'Card' visual -> Drag your numeric field into the 'Fields' bucket.[/dim]")
        elif bi_choice == "4":
            console.print(f"      [dim]↳ Steps: Click 'Add a chart' -> Select 'Scorecard' -> Drag your numeric field into the 'Metric' section.[/dim]")
        
    if date_cols and numeric_cols:
        console.print(f"  [bold cyan]Center (Line Chart):[/] Show the trend of [bold]{numeric_cols[0]}[/] over [bold]{date_cols[0]}[/] to track growth over time.")
        if bi_choice == "1":
            console.print(f"      [dim]↳ Steps: Insert PivotChart (Line) -> Drag '{date_cols[0]}' to Axis (Categories) -> Drag '{numeric_cols[0]}' to Values.[/dim]")
        elif bi_choice == "2":
            console.print(f"      [dim]↳ Steps: Columns Shelf: '{date_cols[0]}' (Continuous) -> Rows Shelf: '{numeric_cols[0]}'.[/dim]")
        elif bi_choice == "3":
            console.print(f"      [dim]↳ Steps: Visualizations Pane -> Click 'Line chart' -> X-axis: '{date_cols[0]}', Y-axis: '{numeric_cols[0]}'.[/dim]")
        elif bi_choice == "4":
            console.print(f"      [dim]↳ Steps: Click 'Add a chart' -> Select 'Time series chart' -> Dimension: '{date_cols[0]}', Metric: '{numeric_cols[0]}'.[/dim]")
    elif numeric_cols and text_cols:
        main_cats = [c for c in text_cols if df[c].nunique() <= 15]
        if main_cats:
            console.print(f"  [bold cyan]Center (Column Chart):[/] Show the highest performing [bold]{main_cats[0]}[/] categories based on [bold]{numeric_cols[0]}[/].")
            if bi_choice == "1":
                console.print(f"      [dim]↳ Steps: Insert PivotChart (Column) -> Drag '{main_cats[0]}' to Axis (Categories) -> Drag '{numeric_cols[0]}' to Values.[/dim]")
            elif bi_choice == "2":
                console.print(f"      [dim]↳ Steps: Columns Shelf: '{main_cats[0]}' -> Rows Shelf: '{numeric_cols[0]}' -> Click the Sort icon.[/dim]")
            elif bi_choice == "3":
                console.print(f"      [dim]↳ Steps: Visualizations Pane -> Click 'Clustered column chart' -> X-axis: '{main_cats[0]}', Y-axis: '{numeric_cols[0]}'.[/dim]")
            elif bi_choice == "4":
                console.print(f"      [dim]↳ Steps: Click 'Add a chart' -> Select 'Column chart' -> Dimension: '{main_cats[0]}', Metric: '{numeric_cols[0]}'.[/dim]")

    if text_cols:
        small_cats = [c for c in text_cols if 1 < df[c].nunique() <= 5]
        if small_cats:
            console.print(f"  [bold magenta]Bottom Left (Donut Chart):[/] Break down the percentage share of [bold]{small_cats[0]}[/].")
            if bi_choice == "1":
                console.print(f"      [dim]↳ Steps: Insert PivotChart (Pie/Donut) -> Drag '{small_cats[0]}' to Axis -> Drag '{small_cats[0]}' to Values (Count).[/dim]")
            elif bi_choice == "2":
                console.print(f"      [dim]↳ Steps: Marks Card: Select 'Pie' -> Drag '{small_cats[0]}' to Color -> Drag '{small_cats[0]}' (Count) to Angle.[/dim]")
            elif bi_choice == "3":
                console.print(f"      [dim]↳ Steps: Visualizations Pane -> Click 'Donut chart' -> Legend: '{small_cats[0]}', Values: '{small_cats[0]}'.[/dim]")
            elif bi_choice == "4":
                console.print(f"      [dim]↳ Steps: Click 'Add a chart' -> Select 'Donut chart' -> Dimension: '{small_cats[0]}', Metric: Record Count.[/dim]")
            
        med_cats = [c for c in text_cols if 5 < df[c].nunique() <= 15]
        if med_cats and numeric_cols:
            console.print(f"  [bold magenta]Bottom Right (Bar Chart):[/] Rank the top [bold]{med_cats[0]}[/] by [bold]{numeric_cols[0]}[/].")
            if bi_choice == "1":
                console.print(f"      [dim]↳ Steps: Insert PivotChart (Bar) -> Drag '{med_cats[0]}' to Axis -> Drag '{numeric_cols[0]}' to Values -> Right-click chart and Sort.[/dim]")
            elif bi_choice == "2":
                console.print(f"      [dim]↳ Steps: Columns Shelf: '{numeric_cols[0]}' -> Rows Shelf: '{med_cats[0]}' -> Click the Sort Descending icon.[/dim]")
            elif bi_choice == "3":
                console.print(f"      [dim]↳ Steps: Visualizations Pane -> Click 'Clustered bar chart' -> Y-axis: '{med_cats[0]}', X-axis: '{numeric_cols[0]}'.[/dim]")
            elif bi_choice == "4":
                console.print(f"      [dim]↳ Steps: Click 'Add a chart' -> Select 'Bar chart' -> Dimension: '{med_cats[0]}', Metric: '{numeric_cols[0]}'.[/dim]")
            
    if text_cols:
         valid_slicers = [f'[bold]{c}[/]' for c in text_cols if df[c].nunique() <= 20][:3]
         if valid_slicers:
             console.print(f"  [bold blue]Left Sidebar (Slicers):[/] Add clickable filters for {', '.join(valid_slicers)} so users can drill down into the data.")
             if bi_choice == "1":
                 console.print(f"      [dim]↳ Steps: Click any PivotChart -> PivotChart Analyze Ribbon -> Insert Slicer -> Check boxes for these columns.[/dim]")
             elif bi_choice == "2":
                 console.print(f"      [dim]↳ Steps: Drag your field to the Filters shelf -> Right-click the pill -> Select 'Show Filter'.[/dim]")
             elif bi_choice == "3":
                 console.print(f"      [dim]↳ Steps: Visualizations Pane -> Click 'Slicer' -> Drag your field into the Field bucket.[/dim]")
             elif bi_choice == "4":
                 console.print(f"      [dim]↳ Steps: Click 'Add a control' -> Select 'Drop-down list' -> Control field: your category.[/dim]")
    console.print("")

def clean_data(filepath):
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
        
    console.print("\n[bold yellow]🧹 INITIATING AUTO-CLEAN ENGINE...[/]")
    time.sleep(0.5)
    
    # 1. Drop Ghost / Unnamed Columns
    unnamed_cols = [col for col in df.columns if str(col).lower().startswith('unnamed')]
    if unnamed_cols:
        df = df.drop(columns=unnamed_cols)
        console.print(f"  [green]✔[/] Dropped {len(unnamed_cols)} 'Unnamed' ghost columns.")
        
    # 2. Drop Completely Empty Columns
    empty_cols = df.columns[df.isnull().all()].tolist()
    if empty_cols:
        df = df.drop(columns=empty_cols)
        console.print(f"  [green]✔[/] Dropped {len(empty_cols)} completely empty columns.")
        
    # 3. Fix Text Columns (Invisible Spaces & Text Numbers)
    text_cols = df.select_dtypes(include=['object']).columns
    space_fixed = 0
    dirty_num_fixed = 0
    
    for col in text_cols:
        # Check if column looks like a dirty number (has currency/commas and digits)
        curr_mask = df[col].notna() & df[col].astype(str).str.contains(r'[\$£€,]', regex=True) & df[col].astype(str).str.contains(r'\d', regex=True)
        if curr_mask.any():
            df[col] = df[col].astype(str).str.replace(r'[^\d.-]', '', regex=True)
            df[col] = pd.to_numeric(df[col], errors='coerce')
            dirty_num_fixed += 1
            console.print(f"  [green]✔[/] Converted '{col}' from text to pure numbers.")
            continue # Moved to numeric, skip string stripping
            
        # Strip invisible spaces for remaining text columns
        mask = df[col].notna() & df[col].astype(str).str.contains(r'^\s+|\s+$', regex=True)
        if mask.any():
            df[col] = df[col].astype(str).str.strip()
            space_fixed += 1
            console.print(f"  [green]✔[/] Stripped invisible spaces from '{col}'.")
            
    # Prompt user for output format
    from rich.prompt import Prompt
    console.print("\n[bold cyan]💾 How would you like to save the cleaned data?[/]")
    console.print("  [bold green]1.[/] Excel Workbook (.xlsx) - Best for Dashboards & formatting")
    console.print("  [bold blue]2.[/] Raw CSV (.csv) - Best for PostgreSQL Bulk Imports")
    console.print("  [bold magenta]3.[/] JSON (.json) - Best for Web Apps & APIs")
    
    save_choice = Prompt.ask("Select output format", choices=["1", "2", "3"], default="1")
    base, ext = os.path.splitext(filepath)
    
    if save_choice == "1":
        new_filepath = f"{base}_cleaned.xlsx"
        with console.status(f"[cyan]● Saving to '{os.path.basename(new_filepath)}'...[/]", spinner="bouncingBar"):
            df.to_excel(new_filepath, index=False)
            time.sleep(0.6)
    elif save_choice == "2":
        new_filepath = f"{base}_cleaned.csv"
        with console.status(f"[cyan]● Saving to '{os.path.basename(new_filepath)}'...[/]", spinner="bouncingBar"):
            df.to_csv(new_filepath, index=False)
            time.sleep(0.6)
    else:
        new_filepath = f"{base}_cleaned.json"
        with console.status(f"[cyan]● Saving to '{os.path.basename(new_filepath)}'...[/]", spinner="bouncingBar"):
            df.to_json(new_filepath, orient="records", indent=4)
            time.sleep(0.6)
            
    console.print(f"\n[bold green]🎉 SUCCESS![/] Cleaned dataset saved to:\n[cyan]{new_filepath}[/]")



def map_data(filepath):
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
        
    console.print("\n[bold yellow]🗺️ INITIATING MARKDOWN DATA DICTIONARY (ULLR MAP)...[/]")
    time.sleep(0.5)
    
    # 1. Identify Columns and Types
    schema_data = []
    primary_keys = []
    
    for col in df.columns:
        dtype = str(df[col].dtype)
        is_unique = df[col].is_unique
        is_id = 'id' in str(col).lower()
        
        # Auto-detect Primary Key
        pk_flag = ""
        if is_unique and is_id:
            pk_flag = "🔑 **PRIMARY KEY**"
            primary_keys.append(col)
        elif is_unique:
            pk_flag = "Candidate Key"
            
        # Map pandas dtypes to business logic
        business_type = dtype
        if "object" in dtype:
            business_type = "Text / Categorical"
        elif "int" in dtype:
            business_type = "Integer"
        elif "float" in dtype:
            business_type = "Decimal / Float"
        elif "datetime" in dtype:
            business_type = "Datetime"
            
        schema_data.append(f"| `{col}` | {business_type} | {pk_flag} |   |")
        
    # Generate Markdown Content
    base_name = os.path.splitext(os.path.basename(filepath))[0]
    md_content = f"# 🗃️ Data Dictionary: {base_name}\n\n"
    md_content += f"**Source File:** `{os.path.basename(filepath)}`\n"
    md_content += f"**Total Rows:** {len(df):,}\n"
    md_content += f"**Total Columns:** {len(df.columns)}\n\n"
    
    if primary_keys:
         md_content += f"**Detected Primary Key(s):** `{', '.join(primary_keys)}`\n\n"
         
    # Combined AI Stakeholder Brief Logic
    real_cols = [col for col in df.columns if not str(col).lower().startswith('unnamed')]
    numeric_cols = [c for c in df[real_cols].select_dtypes(include=['number']).columns.tolist() if 'id' not in c.lower() and 'zip' not in c.lower()]
    text_cols = df[real_cols].select_dtypes(include=['object', 'category']).columns.tolist()
    date_cols = [col for col in real_cols if 'date' in col.lower() or 'time' in col.lower() or 'year' in col.lower()]
    
    brief = "## 👔 Simulated Stakeholder Brief\n"
    brief += "> *\"Hey team, I just dropped the new dataset in the folder. Before the weekly standup, I need you to clean this up and build a dashboard for me. Specifically, I want to see:\"\n>\n"
    
    req_num = 1
    if numeric_cols:
        brief += f"> **{req_num}. High-Level KPIs**: I need the total sum and average of `{numeric_cols[0]}`.\n"
        req_num += 1
    if date_cols and numeric_cols:
        brief += f"> **{req_num}. Trend Analysis**: Build a line chart showing `{numeric_cols[0]}` tracking over time using `{date_cols[0]}`.\n"
        req_num += 1
    if text_cols and numeric_cols:
        brief += f"> **{req_num}. Category Breakdown**: I need a visual showing the top performers in `{text_cols[0]}` based on `{numeric_cols[-1]}`.\n"
        req_num += 1
    if len(text_cols) > 1:
        valid_slicers = [f'`{c}`' for c in text_cols if df[c].nunique() <= 20][:3]
        if valid_slicers:
            brief += f"> **{req_num}. Interactivity**: Make sure you include Slicers for {', '.join(valid_slicers)} so I can filter the dashboard myself.\n"
            
    brief += "> \n> **Recommended Dashboard Layout:**\n"
    
    if numeric_cols:
        kpis = " and ".join([f"`Total {c}`" for c in numeric_cols[:2]])
        brief += f"> - **Top (KPI Cards):** Put large, bold text showing {kpis} at the very top.\n"
    if date_cols and numeric_cols:
        brief += f"> - **Center (Line Chart):** Show the trend of `{numeric_cols[0]}` over `{date_cols[0]}`.\n"
    if text_cols:
        small_cats = [c for c in text_cols if 1 < df[c].nunique() <= 5]
        if small_cats:
            brief += f"> - **Bottom Left (Donut Chart):** Break down the percentage share of `{small_cats[0]}`.\n"
        med_cats = [c for c in text_cols if 5 < df[c].nunique() <= 15]
        if med_cats and numeric_cols:
            brief += f"> - **Bottom Right (Bar Chart):** Rank the top `{med_cats[0]}` by `{numeric_cols[0]}`.\n"
        valid_slicers = [f'`{c}`' for c in text_cols if df[c].nunique() <= 20][:3]
        if valid_slicers:
            brief += f"> - **Left Sidebar (Slicers):** Add clickable filters for {', '.join(valid_slicers)}.\n"
            
    brief += "> \n> *\"Let me know when the Excel file is ready for review!\"*\n\n"

    md_content += brief
    md_content += "## 📊 Schema Map\n\n"
    md_content += "| Column Name | Data Type | Key Type | Description/Notes |\n"
    md_content += "|---|---|---|---|\n"
    for row in schema_data:
        md_content += row + "\n"
        
    # Save next to the original file
    file_dir = os.path.dirname(os.path.abspath(filepath))
    out_path = os.path.join(file_dir, f"{base_name}_schema.md")
    
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(md_content)
        
    console.print(f"\n[bold green]🎉 SUCCESS![/] Markdown Data Dictionary generated and saved to:\n[cyan]{out_path}[/]")



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
    
    ind_choice = Prompt.ask("Select an option", choices=["1", "2", "3"], default="1")
    rows_choice = Prompt.ask("How many rows of dirty practice data do you need?", default="1000")
    
    try:
        rows = int(rows_choice)
    except:
        rows = 1000
        
    with console.status(f"[cyan]● Fabricating {rows:,} rows of beautifully dirty data...[/]", spinner="dots"):
        data = []
        if ind_choice == "1":
            industry = "ecommerce"
            for i in range(rows):
                data.append({
                    "Transaction_ID": fake.uuid4()[:8],
                    "Customer_Name": fake.name(),
                    "Purchase_Date": fake.date_between(start_date='-1y', end_date='today').strftime('%Y-%m-%d'),
                    "Product_Category": random.choice(["Electronics", "Clothing", "Home", "Sports"]),
                    "Quantity": random.randint(1, 10),
                    "Unit_Price": round(random.uniform(10.0, 500.0), 2)
                })
        elif ind_choice == "2":
            industry = "healthcare"
            for i in range(rows):
                data.append({
                    "Patient_ID": f"PT-{fake.random_int(min=1000, max=9999)}",
                    "Patient_Name": fake.name(),
                    "Admission_Date": fake.date_between(start_date='-2y', end_date='today').strftime('%Y-%m-%d'),
                    "Department": random.choice(["Cardiology", "Neurology", "Oncology", "Pediatrics"]),
                    "Length_of_Stay": random.randint(1, 30),
                    "Treatment_Cost": round(random.uniform(500.0, 15000.0), 2)
                })
        else:
            industry = "realestate"
            for i in range(rows):
                data.append({
                    "Property_ID": f"RE-{fake.random_int(min=100, max=999)}",
                    "Agent_Name": fake.name(),
                    "Listing_Date": fake.date_between(start_date='-6m', end_date='today').strftime('%Y-%m-%d'),
                    "Property_Type": random.choice(["House", "Condo", "Townhouse", "Commercial"]),
                    "Square_Feet": random.randint(800, 5000),
                    "Listing_Price": round(random.uniform(150000.0, 2000000.0), 2)
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
        
        out_dir = os.path.join(pathlib.Path.home(), "Projects", "eksel-praktis")
        os.makedirs(out_dir, exist_ok=True)
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


def interactive_mode():
    from rich.prompt import Prompt
    
    print_banner()
    console.print("[bold green]Welcome to the Ullr Data Engine![/]\n")
    
    while True:
        console.print("[bold cyan]What would you like to do?[/]")
        console.print("  [bold green]1.[/] Audit Data")
        console.print("  [bold blue]2.[/] Analyze Data")
        console.print("  [bold magenta]3.[/] Auto-Clean")
        console.print("  [bold bright_cyan]4.[/] Map Schema")
        console.print("  [bold yellow]5.[/] Generate Data")
        console.print("  [bold white]6.[/] Help Menu")
        console.print("  [bold red]7.[/] Exit")
        
        choice = Prompt.ask("\nSelect an option", choices=["1", "2", "3", "4", "5", "6", "7"], default="1")
        
        if choice == "7":
            console.print("[yellow]Goodbye![/]")
            break
        elif choice == "6":
            console.print("\n[bold underline]Ullr Help Menu[/]")
            console.print("[bold green]Audit Data:[/] Scans a raw CSV/Excel file for missing values, duplicates, and formatting errors without changing the file.")
            console.print("[bold blue]Analyze Data:[/] Reads a cleaned dataset and provides a blueprint/layout for building a Dashboard in BI tools.")
            console.print("[bold magenta]Auto-Clean:[/] Automatically drops empty columns, strips invisible spaces, and converts currency text back to pure numbers.")
            console.print("[bold bright_cyan]Map Schema:[/] Generates a Markdown Data Dictionary of your dataset and saves it in the same folder as your original file.")
            console.print("[bold yellow]Generate Data:[/] Creates synthetic, dirty practice datasets (e.g. E-commerce, Healthcare) with intentional errors for you to practice cleaning.")
        elif choice == "5":
            generate_data()
        elif choice == "4":
            filepath = Prompt.ask("\n[bold yellow]Enter the filename or path to map (e.g., data.csv)[/]")
            map_data(filepath.strip())
        elif choice == "1":
            filepath = Prompt.ask("\n[bold yellow]Enter the filename or path to audit (e.g., data.csv)[/]")
            audit_data(filepath.strip())
        elif choice == "2":
            filepath = Prompt.ask("\n[bold yellow]Enter the filename or path to analyze (e.g., data.csv)[/]")
            analyze_data(filepath.strip())
        elif choice == "3":
            filepath = Prompt.ask("\n[bold yellow]Enter the filename or path to clean (e.g., data.csv)[/]")
            clean_data(filepath.strip())
        
        console.print("\n" + "-"*50 + "\n")

def cli():
    parser = argparse.ArgumentParser(description="Ullr: The Offline Data Auditor")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    audit_parser = subparsers.add_parser("audit", help="Check raw data for flaws (NULLs, duplicates).")
    audit_parser.add_argument("file", help="Path to the CSV file")
    
    analyze_parser = subparsers.add_parser("analyze", help="Generate dashboard blueprints for cleaned data.")
    analyze_parser.add_argument("file", help="Path to the cleaned CSV file")
    
    clean_parser = subparsers.add_parser("clean", help="Auto-clean data (remove empty columns, strip spaces, fix text numbers).")
    clean_parser.add_argument("file", help="Path to the raw CSV file")
    
    map_parser = subparsers.add_parser("map", help="Auto-generate a Markdown Data Dictionary for Obsidian.")
    map_parser.add_argument("file", help="Path to the CSV/Excel file")
    
    generate_parser = subparsers.add_parser("generate", help="Generate synthetic dirty datasets for Excel practice.")
    
    args = parser.parse_args()
    
    if not args.command:
        interactive_mode()
        sys.exit(0)
        
    print_banner()
    if args.command == "audit":
        audit_data(args.file)
    elif args.command == "analyze":
        analyze_data(args.file)
    elif args.command == "clean":
        clean_data(args.file)
    elif args.command == "map":
        map_data(args.file)
    elif args.command == "generate":
        generate_data()

if __name__ == "__main__":
    cli()
