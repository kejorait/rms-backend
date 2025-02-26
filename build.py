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

    
match = re.search(r"filevers=\((\d+), (\d+), (\d+), (\d+)\)", content)
if match:
    version = '.'.join(match.groups()[:3])  # Use major.minor.patch for release tag

major, minor, patch, build = map(int, match.groups())
new_version = increment_version((major, minor, patch, build))
new_version = str(new_version)
new_version_dot = new_version.replace(",", ".").replace("(", "").replace(")", "").replace(" ", "")[:-2]

new_content = f"""
# version.txt
# UTF-8 encoding
VSVersionInfo(
    ffi=FixedFileInfo(
        filevers={new_version},
        prodvers={new_version},
        mask=0x3f,
        flags=0x0,
        OS=0x4,
        fileType=0x1,
        subtype=0x0,
        date=(0, 0)
    ),
    kids=[
        StringFileInfo(
            [
                StringTable(
                    '040904B0',
                    [
                        StringStruct('CompanyName', 'Kejora'),
                        StringStruct('FileDescription', 'RMS Backend'),
                        StringStruct('FileVersion', '{new_version_dot}'),
                        StringStruct('InternalName', 'rms-backend'),
                        StringStruct('LegalCopyright', '© Kejora'),
                        StringStruct('OriginalFilename', 'rms-backend.exe'),
                        StringStruct('ProductName', 'RMS Backend'),
                        StringStruct('ProductVersion', '{new_version_dot}')
                    ]
                )
            ]
        ),
        VarFileInfo([VarStruct('Translation', [1033, 1200])])
    ]
)
"""

with version_file.open("w", encoding="utf-8") as file:
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
