import importlib.util
import os
import sys

from dotenv import load_dotenv
from psycopg2 import connect, sql
from psycopg2.errors import DuplicateDatabase
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import sessionmaker

# Load environment variables from .env file
load_dotenv(override=True)


# Retrieve PostgreSQL connection details from environment variables
pg_user = os.getenv('PG_USER')
pg_pwd = os.getenv('PG_PWD')
pg_port = os.getenv('PG_PORT')
pg_db = os.getenv('PG_DB')
pg_host = os.getenv('PG_HOST')

# Construct the database URL
DB_URL = f"postgresql://{pg_user}:{pg_pwd}@{pg_host}:{pg_port}/{pg_db}"
DB_URL_NO_DB = f"postgresql://{pg_user}:{pg_pwd}@{pg_host}:{pg_port}/postgres"

print(f"Migrating to DB: {DB_URL}")

def create_database():
    """Creates the target database if it doesn't exist."""
    try:
        conn = connect(DB_URL_NO_DB)
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(pg_db)))
        cursor.close()
        conn.close()
        print(f"Database '{pg_db}' created successfully.")
    except DuplicateDatabase:
        print(f"Database '{pg_db}' already exists.")
    except Exception as e:
        print(f"Error creating database: {e}")
        sys.exit(1)

# Try to create the engine and connect to the database
try:
    engine = create_engine(DB_URL)
    engine.connect()
except Exception as e:
    if "does not exist" in str(e):
        print(f"Database '{pg_db}' does not exist, creating database...")
        create_database()
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

# Import all models from the models folder, excluding base.py
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
        print(f"Created table for model '{model_name}': {table_name}")
    else:
        # Get existing columns from the database
        existing_columns = {col['name'] for col in inspector.get_columns(table_name)}
        
        # Iterate over model columns and check if they exist in the table
        for column in model_class.__table__.columns:
            if column.name not in existing_columns:
                # Determine the SQL type
                column_type = str(column.type).replace("DATETIME", "TIMESTAMP")
                
                # Get the default value from the column definition
                default_value = column.default
                if default_value is not None:
                    # If default_value is a callable (e.g., func.now()), resolve it
                    if callable(default_value.arg):
                        default_value = "CURRENT_TIMESTAMP"
                    else:
                        default_value = f"'{default_value.arg}'" if isinstance(default_value.arg, str) else default_value.arg
                
                # Add column with default if specified
                with engine.begin() as conn:
                    alter_stmt = f'ALTER TABLE "{table_name}" ADD COLUMN "{column.name}" {column_type}'
                    if default_value is not None:
                        alter_stmt += f" DEFAULT {default_value}"
                    print(f"Executing: {alter_stmt}")
                    conn.execute(text(alter_stmt))
                    print(f"Added column '{column.name}' to table '{table_name}' with default {default_value}")


# Commit changes and close session
session.commit()
session.close()

print("Migration completed.")
