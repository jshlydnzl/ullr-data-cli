import os
import json

file_path = "ullr/main.py"
with open(file_path, "r") as f:
    code = f.read()

# 1. Add json import
code = code.replace("import sys\nimport time", "import sys\nimport time\nimport json")

# 2. Add config functions before print_banner
config_funcs = """
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
    console.print("\\n[bold yellow]⚠️ First Time Setup: No default directory found.[/]")
    console.print("Where should Ullr save generated practice datasets?")
    console.print("Examples: [cyan]C:\\\\Users\\\\Name\\\\Desktop[/] (Windows) or [cyan]/home/name/Desktop[/] (Mac/Linux)")
    
    while True:
        user_dir = Prompt.ask("Enter directory path").strip()
        if os.path.exists(user_dir) and os.path.isdir(user_dir):
            config["default_dir"] = user_dir
            save_config(config)
            console.print(f"[bold green]✔ Saved![/] Ullr will now save files to: {user_dir}\\n")
            return user_dir
        else:
            console.print("[bold red]❌ That directory does not exist. Please try again.[/]")

def change_default_dir():
    config = load_config()
    current = config.get("default_dir", "None")
    console.print(f"\\n[bold cyan]Current Default Directory:[/] {current}")
    
    from rich.prompt import Prompt
    user_dir = Prompt.ask("Enter NEW directory path (or press Enter to cancel)").strip()
    if not user_dir:
        return
        
    if os.path.exists(user_dir) and os.path.isdir(user_dir):
        config["default_dir"] = user_dir
        save_config(config)
        console.print(f"[bold green]✔ Directory Updated to:[/] {user_dir}\\n")
    else:
        console.print("[bold red]❌ That directory does not exist. Update canceled.[/]")

def print_banner():
"""
code = code.replace("def print_banner():", config_funcs)

# 3. Fix generate_data hardcoded path
old_path = """        out_dir = os.path.join(pathlib.Path.home(), "Projects", "eksel-praktis")
        os.makedirs(out_dir, exist_ok=True)"""
new_path = """        out_dir = get_default_dir()"""
code = code.replace(old_path, new_path)

# 4. Update interactive_mode menu
old_menu = """        console.print("  [bold yellow]5.[/] Generate Data")
        console.print("  [bold white]6.[/] Help Menu")
        console.print("  [bold red]7.[/] Exit")
        
        choice = Prompt.ask("\\nSelect an option", choices=["1", "2", "3", "4", "5", "6", "7"], default="1")"""
        
new_menu = """        console.print("  [bold yellow]5.[/] Generate Data")
        console.print("  [bold white]6.[/] Config: Set Default Directory")
        console.print("  [bold dim]7.[/] Help Menu")
        console.print("  [bold red]8.[/] Exit")
        
        choice = Prompt.ask("\\nSelect an option", choices=["1", "2", "3", "4", "5", "6", "7", "8"], default="1")"""
code = code.replace(old_menu, new_menu)

# Update interactive_mode logic
old_logic = """        if choice == "7":
            console.print("[yellow]Goodbye![/]")
            break
        elif choice == "6":
            console.print("\\n[bold underline]Ullr Help Menu[/]")"""

new_logic = """        if choice == "8":
            console.print("[yellow]Goodbye![/]")
            break
        elif choice == "7":
            console.print("\\n[bold underline]Ullr Help Menu[/]")"""
code = code.replace(old_logic, new_logic)

old_logic2 = """        elif choice == "5":
            generate_data()"""
new_logic2 = """        elif choice == "6":
            change_default_dir()
        elif choice == "5":
            generate_data()"""
code = code.replace(old_logic2, new_logic2)

# 5. Add to CLI parser
old_cli = """    generate_parser = subparsers.add_parser("generate", help="Generate synthetic dirty datasets for Excel practice.")"""
new_cli = """    generate_parser = subparsers.add_parser("generate", help="Generate synthetic dirty datasets for Excel practice.")
    
    config_parser = subparsers.add_parser("config", help="Set the default directory for saved datasets.")"""
code = code.replace(old_cli, new_cli)

old_cli2 = """    elif args.command == "generate":
        generate_data()"""
new_cli2 = """    elif args.command == "generate":
        generate_data()
    elif args.command == "config":
        change_default_dir()"""
code = code.replace(old_cli2, new_cli2)

with open(file_path, "w") as f:
    f.write(code)

print("Patch successful!")
