import os

import psycopg2
from dotenv import load_dotenv

# Load environment variables from .env file and override any existing ones
load_dotenv(override=True)

# Retrieve PostgreSQL connection details from environment variables
pg_user = os.getenv('PG_USER')
pg_pwd = os.getenv('PG_PWD')
pg_port = os.getenv('PG_PORT')
pg_db = os.getenv('PG_DB')
pg_host = os.getenv('PG_HOST')

# Construct the database URL
DB_URL = f"postgresql://{pg_user}:{pg_pwd}@{pg_host}:{pg_port}/{pg_db}"

print(f"Migrating to DB: {DB_URL}")

# Path to the migration folder
MIGRATION_FOLDER = 'migration'

def run_sql_file(cursor, filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        sql = file.read()
        cursor.execute(sql)

def main():
    try:
        # Establish database connection using environment variables
        connection = psycopg2.connect(
            dbname=pg_db,
            user=pg_user,
            password=pg_pwd,
            host=pg_host,
            port=pg_port
        )
        cursor = connection.cursor()

        # Execute each SQL file in the migration folder
        for filename in sorted(os.listdir(MIGRATION_FOLDER)):
            if filename.endswith('.sql'):
                filepath = os.path.join(MIGRATION_FOLDER, filename)
                print(f'Running {filename}...')
                try:
                    run_sql_file(cursor, filepath)
                    connection.commit()
                    print(f'{filename} executed successfully.')
                except Exception as e:
                    print(f'Error executing {filename}: {e}')
                    connection.rollback()  # Rollback to avoid partial commits and proceed

        # Close the cursor and connection
        cursor.close()
        connection.close()
        print('Migration completed successfully.')

    except Exception as e:
        print(f'An error occurred: {e}')
        if 'connection' in locals() and connection:
            connection.rollback()
            cursor.close()
            connection.close()

if __name__ == '__main__':
    main()
