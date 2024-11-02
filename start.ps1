# Activate the virtual environment
.\venv\Scripts\Activate.ps1

# Set environment variables
$env:SECRET_KEY = "topsecretkey"
$env:PG_USER = "kejora"
$env:PG_PWD = "kEjoranusantaraheba1t"
$env:PG_PORT = "7777"
$env:PG_DB = "rms-kejora"
$env:PG_HOST = "api.kejora.my.id"
$env:HOST = "https://api.kejora.my.id:5000"
$env:ENV = "DEV"
$env:MENU_PATH = "menu"
$env:USER_PATH = "user"
$env:CATEGORY_PATH = "category"
$env:UPLOADS_PATH = "uploads"
$env:PORT = "9898"

# Run the main script
python main.py
