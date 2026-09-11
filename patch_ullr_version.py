import os

file_path = "setup.py"
with open(file_path, "r") as f:
    code = f.read()

# Update version
code = code.replace("version='1.0.0'", "version='2.0.0'")

# Update description
old_desc = "description='An offline, AI-free Data Analytics and Dashboard Auditing CLI',"
new_desc = "description='A purely native Practice Engine for aspiring Data Analysts to generate and audit datasets',"
code = code.replace(old_desc, new_desc)

with open(file_path, "w") as f:
    f.write(code)

print("Version bumped to 2.0.0 and description updated!")
