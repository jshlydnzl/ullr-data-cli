import os

file_path = "ullr/main.py"
with open(file_path, "r") as f:
    code = f.read()

# 1. Add the prompt_for_file function right before interactive_mode()
prompt_func = """
def prompt_for_file(action_name):
    from rich.prompt import Prompt
    import glob
    
    cwd = os.getcwd()
    files = []
    for ext in ['*.csv', '*.xlsx', '*.xls']:
        files.extend(glob.glob(os.path.join(cwd, ext)))
        
    if files:
        console.print(f"\\n[bold cyan]📂 Found data files in current folder:[/]")
        for i, f in enumerate(files):
            console.print(f"  [bold green]{i+1}.[/] {os.path.basename(f)}")
        console.print("  [bold yellow]0.[/] Type a manual filename or path instead")
        
        choices = [str(i) for i in range(len(files) + 1)]
        choice = Prompt.ask(f"\\nSelect a file to {action_name}", choices=choices, default="1")
        
        if choice != "0":
            return files[int(choice)-1]
            
    return Prompt.ask(f"\\n[bold yellow]Enter the filename or path to {action_name} (e.g., data.csv)[/]").strip()

def interactive_mode():
"""
code = code.replace("def interactive_mode():", prompt_func)

# 2. Update interactive_mode to use the new function
old_interactive_1 = """        elif choice == "4":
            filepath = Prompt.ask("\\n[bold yellow]Enter the filename or path to map (e.g., data.csv)[/]")
            map_data(filepath.strip())
        elif choice == "1":
            filepath = Prompt.ask("\\n[bold yellow]Enter the filename or path to audit (e.g., data.csv)[/]")
            audit_data(filepath.strip())
        elif choice == "2":
            filepath = Prompt.ask("\\n[bold yellow]Enter the filename or path to analyze (e.g., data.csv)[/]")
            analyze_data(filepath.strip())
        elif choice == "3":
            filepath = Prompt.ask("\\n[bold yellow]Enter the filename or path to clean (e.g., data.csv)[/]")
            clean_data(filepath.strip())"""

new_interactive_1 = """        elif choice == "4":
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

code = code.replace(old_interactive_1, new_interactive_1)

with open(file_path, "w") as f:
    f.write(code)

print("UX Patch successful!")
