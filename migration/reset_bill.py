import os
import sys
from urllib.parse import quote_plus  # Import URL encoding function

from dotenv import load_dotenv
from psycopg2 import connect, sql
from psycopg2.errors import DuplicateDatabase
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Load environment variables from .env file
load_dotenv(override=True)

# Retrieve PostgreSQL connection details from environment variables
pg_user = os.getenv('PG_USER')
pg_pwd = os.getenv('PG_PWD')  # Password might contain special characters like '@'
pg_port = os.getenv('PG_PORT')
pg_db = os.getenv('PG_DB')
pg_host = os.getenv('PG_HOST')

# URL-encode the password to handle special characters
pg_pwd_encoded = quote_plus(pg_pwd)  # This encodes the password properly

# Construct the database URL
DB_URL = f"postgresql://{pg_user}:{pg_pwd_encoded}@{pg_host}:{pg_port}/{pg_db}"
DB_URL_NO_DB = f"postgresql://{pg_user}:{pg_pwd_encoded}@{pg_host}:{pg_port}/postgres"

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
db = Session()

# bill = db.query(Bill).all()
# delete all
db.execute(text('DELETE FROM bill'))
db.execute(text('DELETE FROM bill_dtl'))
db.execute(text('DELETE FROM table_session'))

# Commit changes and close session
db.commit()
db.close()

print("bill reset completed.")
