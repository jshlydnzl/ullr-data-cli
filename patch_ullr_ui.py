import os

file_path = "ullr/main.py"
with open(file_path, "r") as f:
    code = f.read()

# 1. Remove the Examples line in get_default_dir
old_prompt = """    console.print("Where should Ullr save generated practice datasets?")
    console.print("Examples: [cyan]C:\\\\Users\\\\Name\\\\Desktop[/] (Windows) or [cyan]/home/name/Desktop[/] (Mac/Linux)")
    
    while True:"""

new_prompt = """    console.print("Where should Ullr save generated practice datasets?")
    
    while True:"""

code = code.replace(old_prompt, new_prompt)

# 2. Move out_dir = get_default_dir() BEFORE the spinner
old_gen = """    try:
        rows = int(rows_choice)
    except:
        rows = 1000
        
    with console.status(f"[cyan]● Fabricating {rows:,} rows of beautifully dirty data...[/]", spinner="dots"):
        data = []"""

new_gen = """    try:
        rows = int(rows_choice)
    except:
        rows = 1000
        
    out_dir = get_default_dir()
    
    with console.status(f"[cyan]● Fabricating {rows:,} rows of beautifully dirty data...[/]", spinner="dots"):
        data = []"""

code = code.replace(old_gen, new_gen)

# Remove the old out_dir = get_default_dir() from inside the spinner
old_out_dir = """        # Save File
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{industry}_raw_{timestamp}.csv"
        
        out_dir = get_default_dir()
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, filename)"""

new_out_dir = """        # Save File
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{industry}_raw_{timestamp}.csv"
        
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, filename)"""

code = code.replace(old_out_dir, new_out_dir)

with open(file_path, "w") as f:
    f.write(code)

print("UI Fixed!")
