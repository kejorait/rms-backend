import os
import sys
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import DeclarativeMeta
import importlib.util
from psycopg2 import connect, sql
from psycopg2.errors import InvalidCatalogName, DuplicateDatabase
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve PostgreSQL connection details from environment variables
pg_user = os.getenv('PG_USER')
pg_pwd = os.getenv('PG_PWD')
pg_port = os.getenv('PG_PORT')
pg_db = os.getenv('PG_DB')
pg_host = os.getenv('PG_HOST')

# Construct the database URL
DB_URL = f"postgresql://{pg_user}:{pg_pwd}@{pg_host}:{pg_port}/{pg_db}"
DB_URL_NO_DB = f"postgresql://{pg_user}:{pg_pwd}@{pg_host}:{pg_port}/postgres"

def create_database():
    try:
        # Connect to the default 'postgres' database to create the target database
        conn = connect(DB_URL_NO_DB)
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(pg_db)))
        cursor.close()
        conn.close()
        print(f"Database {pg_db} created successfully.")
    except DuplicateDatabase:
        print(f"Database {pg_db} already exists.")
    except Exception as e:
        print(f"Error creating database: {e}")
        sys.exit(1)

# Try to create the engine and connect to the database
try:
    engine = create_engine(DB_URL)
    engine.connect()
except Exception as e:
    if "does not exist" in str(e):
        print(f"Database {pg_db} does not exist, creating database...")
        create_database()
        # Retry creating the engine and connecting
        try:
            engine = create_engine(DB_URL)
            engine.connect()
        except Exception as e:
            print(f"Error connecting to the database after creation: {e}")
            sys.exit(1)
    else:
        print(f"Error connecting to the database: {e}")
        sys.exit(1)

# Create a sessionmaker to interact with the database
Session = sessionmaker(bind=engine)
session = Session()

# Import all models from the models folder excluding base.py
models_folder = "models"  # Replace with your actual models folder path
models = {}

for filename in os.listdir(models_folder):
    if filename.endswith(".py") and filename not in ["__init__.py", "base.py"]:
        module_name = filename[:-3]
        file_path = os.path.join(models_folder, filename)
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        models_in_module = {
            name: cls
            for name, cls in module.__dict__.items()
            if isinstance(cls, type) and isinstance(cls, DeclarativeMeta)
        }
        models.update(models_in_module)

# Initialize the inspector
inspector = inspect(engine)

# Iterate over each model and create its corresponding table if it does not exist
for model_name, model_class in models.items():
    if model_name == "DeclarativeOrigin":
        continue
    table_name = model_class.__tablename__
    if not inspector.has_table(table_name):
        model_class.__table__.create(engine)
        print(f"Created table for model {model_name}: {table_name}")

# Commit changes and close session
session.commit()
session.close()

print("Migration completed.")
