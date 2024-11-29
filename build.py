import re
import subprocess
from pathlib import Path


# Function to increment version numbers
def increment_version(version):
    major, minor, patch, build = version
    patch += 1
    if patch == 10:
        patch = 0
        minor += 1
    if minor == 10:
        minor = 0
        major += 1
    return (major, minor, patch, build)

# Read and update version.txt
version_file = Path("version.txt")
with version_file.open("r") as file:
    content = file.read()

new_content = re.sub(
    r"filevers=\((\d+), (\d+), (\d+), (\d+)\),\n\s*prodvers=\((\d+), (\d+), (\d+), (\d+)\),",
    lambda m: f"filevers={increment_version(tuple(map(int, m.groups()[:4])))}," +
              f"\n        prodvers={increment_version(tuple(map(int, m.groups()[4:])))},",
    content
)

with version_file.open("w") as file:
    file.write(new_content)

# Run commands
commands = [
    "cmd.exe /c \"\".venv\\Scripts\\activate.bat\" && pyinstaller -F --hidden-import app --version-file .\\version.txt -n rms-backend.exe -i=NONE .\\main.py --clean\""
]

for cmd in commands:
    subprocess.run(cmd, shell=True, check=True)

# Copy the executable
subprocess.run(["xcopy", ".\\dist\\rms-backend.exe", ".\\dist\\rms-backend\\", "/Y"], shell=True, check=True)

# Extract the updated version from the version file for release
match = re.search(r"filevers=\((\d+), (\d+), (\d+), (\d+)\)", new_content)
if match:
    version = '.'.join(match.groups()[:3])  # Use major.minor.patch for release tag

# Set the folder where the release should be made
release_folder = Path("./dist/rms-backend/")

# Create a GitHub release using gh CLI inside the release folder
release_command = [
    "gh", "release", "create", f"v{version}",
    "rms-backend.exe",
    "--notes", "Automated release via script."
]

# Change to the correct git folder and run the gh release
subprocess.run(release_command, cwd=release_folder, check=True)
