import os

file_path = "ullr/main.py"
with open(file_path, "r") as f:
    code = f.read()

# 1. Update Menu to remove Config
old_menu = """    while True:
        console.print("[bold cyan]What would you like to do?[/]")
        console.print("  [bold green]1.[/] Audit Data")
        console.print("  [bold yellow]2.[/] Generate Data")
        console.print("  [bold white]3.[/] Config: Set Default Directory")
        console.print("  [bold dim]4.[/] Help Menu")
        console.print("  [bold red]5.[/] Exit")
        
        choice = Prompt.ask("\\nSelect an option", choices=["1", "2", "3", "4", "5"], default="1")"""

new_menu = """    while True:
        console.print("[bold cyan]What would you like to do?[/]")
        console.print("  [bold green]1.[/] Audit Data")
        console.print("  [bold yellow]2.[/] Generate Data")
        console.print("  [bold dim]3.[/] Help Menu")
        console.print("  [bold red]4.[/] Exit")
        
        choice = Prompt.ask("\\nSelect an option", choices=["1", "2", "3", "4"], default="1")"""

code = code.replace(old_menu, new_menu)

# 2. Update logic
old_logic = """        if choice == "5":
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

new_logic = """        if choice == "4":
            console.print("[yellow]Goodbye![/]")
            break
        elif choice == "3":
            console.print("\\n[bold underline]Ullr Help Menu[/]")
            console.print("[bold green]Audit Data:[/] Scans a raw CSV/Excel file for missing values, duplicates, and formatting errors without changing the file.")
            console.print("[bold yellow]Generate Data:[/] Creates synthetic, dirty practice datasets with a Stakeholder Brief for you to practice cleaning.")
        elif choice == "2":
            generate_data()
        elif choice == "1":
            filepath = prompt_for_file("audit")
            if filepath:
                audit_data(filepath)"""

code = code.replace(old_logic, new_logic)

# 3. Update CLI logic
old_cli = """    generate_parser = subparsers.add_parser("generate", help="Generate synthetic dirty datasets for Excel practice.")
    
    config_parser = subparsers.add_parser("config", help="Set the default directory for saved datasets.")"""

new_cli = """    generate_parser = subparsers.add_parser("generate", help="Generate synthetic dirty datasets for Excel practice.")"""
code = code.replace(old_cli, new_cli)

old_cli_logic = """    elif args.command == "generate":
        generate_data()
    elif args.command == "config":
        change_default_dir()"""

new_cli_logic = """    elif args.command == "generate":
        generate_data()"""
code = code.replace(old_cli_logic, new_cli_logic)

with open(file_path, "w") as f:
    f.write(code)

print("Menu simplified!")
