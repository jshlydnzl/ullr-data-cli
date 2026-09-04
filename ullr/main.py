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

def find_file_globally(filename):
    home_dir = os.path.expanduser('~')
    
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

def interactive_mode():
    from rich.prompt import Prompt
    
    print_banner()
    console.print("[bold green]Welcome to the Ullr Data Engine![/]\n")
    
    while True:
        console.print("[bold cyan]What would you like to do?[/]")
        console.print("  [bold green]1.[/] Audit raw data (Data Quality Check)")
        console.print("  [bold blue]2.[/] Analyze cleaned data (Dashboard Blueprint)")
        console.print("  [bold red]3.[/] Exit")
        
        choice = Prompt.ask("\nSelect an option", choices=["1", "2", "3"], default="1")
        
        if choice == "3":
            console.print("[yellow]Goodbye![/]")
            break
        elif choice == "1":
            filepath = Prompt.ask("\n[bold yellow]Enter the filename or path to audit (e.g., data.csv)[/]")
            audit_data(filepath.strip())
        elif choice == "2":
            filepath = Prompt.ask("\n[bold yellow]Enter the filename or path to analyze (e.g., data.csv)[/]")
            analyze_data(filepath.strip())
        
        console.print("\n" + "-"*50 + "\n")

def cli():
    parser = argparse.ArgumentParser(description="Ullr: The Offline Data Auditor")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    audit_parser = subparsers.add_parser("audit", help="Check raw data for flaws (NULLs, duplicates).")
    audit_parser.add_argument("file", help="Path to the CSV file")
    
    analyze_parser = subparsers.add_parser("analyze", help="Generate dashboard blueprints for cleaned data.")
    analyze_parser.add_argument("file", help="Path to the cleaned CSV file")
    
    args = parser.parse_args()
    
    if not args.command:
        interactive_mode()
        sys.exit(0)
        
    print_banner()
    if args.command == "audit":
        audit_data(args.file)
    elif args.command == "analyze":
        analyze_data(args.file)

if __name__ == "__main__":
    cli()
