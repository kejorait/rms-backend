import os

# List all Python files in the 'models' folder
models_folder = "models"
model_files = [
    os.path.splitext(f)[0]  # Remove the '.py' extension
    for f in os.listdir(models_folder)
    if f.endswith(".py") and f not in ["__init__.py", "base.py"]
]

# Print all the models for PyInstaller's --hidden-import
for model in model_files:
    print(f"--hidden-import=models.{model}")
