import os

file_path = "ullr/main.py"
with open(file_path, "r") as f:
    code = f.read()

old_func = """def find_file_globally(filename):
    # pathlib.Path.home() natively handles Windows (C:\\Users\\Name), macOS (/Users/Name), and Linux (/home/Name)
    home_dir = str(pathlib.Path.home())
    
    with console.status(f"[yellow]Scanning your computer for '{filename}'...[/]", spinner="dots"):
        for root, dirs, files in os.walk(home_dir):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            if filename in files:
                full_path = os.path.join(root, filename)
                console.print(f"[bold green]Found it at:[/] {full_path}\\n")
                return full_path
            
    return None"""

new_func = """def find_file_globally(filename):
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
                    console.print(f"[bold green]Found it at:[/] {full_path}\\n")
                    return full_path
            
    return None"""

code = code.replace(old_func, new_func)

with open(file_path, "w") as f:
    f.write(code)

print("Search Patch successful!")
