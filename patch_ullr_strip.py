import os

file_path = "ullr/main.py"
with open(file_path, "r") as f:
    code = f.read()

# 1. Remove analyze_data, clean_data, map_data
start_idx = code.find("def analyze_data(filepath):")
end_idx = code.find("def generate_data():")

if start_idx != -1 and end_idx != -1:
    code = code[:start_idx] + code[end_idx:]

# 2. Update interactive_mode menu
old_menu = """    while True:
        console.print("[bold cyan]What would you like to do?[/]")
        console.print("  [bold green]1.[/] Audit Data")
        console.print("  [bold blue]2.[/] Analyze Data")
        console.print("  [bold magenta]3.[/] Auto-Clean")
        console.print("  [bold bright_cyan]4.[/] Map Schema")
        console.print("  [bold yellow]5.[/] Generate Data")
        console.print("  [bold white]6.[/] Config: Set Default Directory")
        console.print("  [bold dim]7.[/] Help Menu")
        console.print("  [bold red]8.[/] Exit")
        
        choice = Prompt.ask("\\nSelect an option", choices=["1", "2", "3", "4", "5", "6", "7", "8"], default="1")"""

new_menu = """    while True:
        console.print("[bold cyan]What would you like to do?[/]")
        console.print("  [bold green]1.[/] Audit Data")
        console.print("  [bold yellow]2.[/] Generate Data")
        console.print("  [bold white]3.[/] Config: Set Default Directory")
        console.print("  [bold dim]4.[/] Help Menu")
        console.print("  [bold red]5.[/] Exit")
        
        choice = Prompt.ask("\\nSelect an option", choices=["1", "2", "3", "4", "5"], default="1")"""

code = code.replace(old_menu, new_menu)

# 3. Update interactive_mode logic
old_logic = """        if choice == "8":
            console.print("[yellow]Goodbye![/]")
            break
        elif choice == "7":
            console.print("\\n[bold underline]Ullr Help Menu[/]")
            console.print("[bold green]Audit Data:[/] Scans a raw CSV/Excel file for missing values, duplicates, and formatting errors without changing the file.")
            console.print("[bold blue]Analyze Data:[/] Reads a cleaned dataset and provides a blueprint/layout for building a Dashboard in BI tools.")
            console.print("[bold magenta]Auto-Clean:[/] Automatically drops empty columns, strips invisible spaces, and converts currency text back to pure numbers.")
            console.print("[bold bright_cyan]Map Schema:[/] Generates a Markdown Data Dictionary of your dataset and saves it in the same folder as your original file.")
            console.print("[bold yellow]Generate Data:[/] Creates synthetic, dirty practice datasets (e.g. E-commerce, Healthcare) with intentional errors for you to practice cleaning.")
        elif choice == "6":
            change_default_dir()
        elif choice == "5":
            generate_data()
        elif choice == "4":
            filepath = prompt_for_file("map")
            map_data(filepath)
        elif choice == "1":
            filepath = prompt_for_file("audit")
            audit_data(filepath)
        elif choice == "2":
            filepath = prompt_for_file("analyze")
            analyze_data(filepath)
        elif choice == "3":
            filepath = prompt_for_file("clean")
            clean_data(filepath)"""

new_logic = """        if choice == "5":
            console.print("[yellow]Goodbye![/]")
            break
        elif choice == "4":
            console.print("\\n[bold underline]Ullr Help Menu[/]")
            console.print("[bold green]Audit Data:[/] Scans a raw CSV/Excel file for missing values, duplicates, and formatting errors without changing the file.")
            console.print("[bold yellow]Generate Data:[/] Creates synthetic, dirty practice datasets (e.g. E-commerce, Healthcare) with a Stakeholder Brief for you to practice cleaning.")
            console.print("[bold white]Config:[/] Change where generated files are saved.")
        elif choice == "3":
            change_default_dir()
        elif choice == "2":
            generate_data()
        elif choice == "1":
            filepath = prompt_for_file("audit")
            if filepath:
                audit_data(filepath)"""

code = code.replace(old_logic, new_logic)

# 4. Update CLI parser
old_cli = """    audit_parser = subparsers.add_parser("audit", help="Check raw data for flaws (NULLs, duplicates).")
    audit_parser.add_argument("file", help="Path to the CSV file")
    
    analyze_parser = subparsers.add_parser("analyze", help="Generate dashboard blueprints for cleaned data.")
    analyze_parser.add_argument("file", help="Path to the cleaned CSV file")
    
    clean_parser = subparsers.add_parser("clean", help="Auto-clean data (remove empty columns, strip spaces, fix text numbers).")
    clean_parser.add_argument("file", help="Path to the raw CSV file")
    
    map_parser = subparsers.add_parser("map", help="Auto-generate a Markdown Data Dictionary for Obsidian.")
    map_parser.add_argument("file", help="Path to the CSV/Excel file")
    
    generate_parser = subparsers.add_parser("generate", help="Generate synthetic dirty datasets for Excel practice.")
    
    config_parser = subparsers.add_parser("config", help="Set the default directory for saved datasets.")"""

new_cli = """    audit_parser = subparsers.add_parser("audit", help="Check raw data for flaws (NULLs, duplicates).")
    audit_parser.add_argument("file", help="Path to the CSV/Excel file")
    
    generate_parser = subparsers.add_parser("generate", help="Generate synthetic dirty datasets for Excel practice.")
    
    config_parser = subparsers.add_parser("config", help="Set the default directory for saved datasets.")"""

code = code.replace(old_cli, new_cli)

old_cli_logic = """    if args.command == "audit":
        audit_data(args.file)
    elif args.command == "analyze":
        analyze_data(args.file)
    elif args.command == "clean":
        clean_data(args.file)
    elif args.command == "map":
        map_data(args.file)
    elif args.command == "generate":
        generate_data()
    elif args.command == "config":
        change_default_dir()"""

new_cli_logic = """    if args.command == "audit":
        audit_data(args.file)
    elif args.command == "generate":
        generate_data()
    elif args.command == "config":
        change_default_dir()"""

code = code.replace(old_cli_logic, new_cli_logic)

with open(file_path, "w") as f:
    f.write(code)

print("Ullr stripped and purified!")
