import datetime
import os
import random
import re
import threading
import time
import traceback

from helper import constants
from helper.database import get_db
from models.app_setting import AppSetting
from models.table import Table
from models.table_session import TableSession

gen_bucket = os.getenv("BUCKET")

BAUD_RATE = 9600
ser = None  # Initialize serial connection as None
running = True  # Control variable for main loop
db = next(get_db())
def initialize_serial_connection():
    """Mock the serial connection initialization."""
    global ser
    global db
    try:
        # Fetch COM port setting from the database
        
        query = db.query(AppSetting.cd, AppSetting.value)
        query = query.filter(AppSetting.cd == 'com_port')
        query = query.filter(AppSetting.is_inactive == constants.NO)
        query = query.filter(AppSetting.is_delete == constants.NO)
        res = query.first()
        db.close()

        if res:
            com_port = res.value
            print(f"Mock: Initialized serial connection on {com_port} at {BAUD_RATE} baud.")
    except Exception as e:
        print("Failed to initialize serial connection:")
        print(traceback.format_exc())

def runner():
    global ser
    try:
        # Attempt to (re)initialize the serial connection every loop
        initialize_serial_connection()
        
        db = next(get_db())
        query = db.query(Table)
        query = query.filter(Table.is_delete == constants.NO)
        query = query.filter(Table.is_inactive == constants.NO)
        query = query.filter(Table.is_billiard == constants.YES)
        tables = query.all()

        for mdl in tables:
            number = re.search(r'\d+', mdl.nm)
            number = int(number.group()) if number else 0

            if mdl.serial_status == 'OFF' and mdl.serial_sent == constants.YES and mdl.sent_closed == constants.YES:
                continue

            if mdl.serial_off_dt and mdl.serial_off_dt <= datetime.datetime.now() and mdl.sent_closed == constants.NO:
                print(f"Mock Command: RELAY {number} OFF")  # Mocked command
                print(f"Mock Response: OK")  # Mocked response
                time.sleep(0.5)
                
                mdl.serial_status = 'OFF'
                mdl.serial_off_dt = None
                mdl.sent_closed = constants.YES

                table_sessions = db.query(TableSession).filter(TableSession.table_cd == mdl.cd)
                for session in table_sessions:
                    session.is_closed = constants.YES
                    if session.closed_dt is None:
                        session.closed_dt = datetime.datetime.now()
                    session.closed_by = 'SYSTEM'

                db.commit()

            elif mdl.serial_status == 'ON' and mdl.serial_sent == constants.NO:
                print(f"Mock Command: RELAY {number} ON")  # Mocked command
                print(f"Mock Response: OK")  # Mocked response
                time.sleep(0.5)
                
                mdl.serial_sent = constants.YES
                db.commit()

    except Exception as e:
        if db:
            db.rollback()
        print("An error occurred during runner execution:")
        print(traceback.format_exc())
    finally:
        if db:
            db.close()

def monitor_input():
    global running, ser
    while True:
        command = input("Enter 'restart' to restart the runner or 'quit' to exit: ").strip().lower()
        if command == "restart":
            print("Restarting the runner...")
            initialize_serial_connection()
        elif command == "quit":
            print("Exiting the application...")
            running = False
            break

print("Starting queue runner...")

# Start the input monitoring in a separate thread
input_thread = threading.Thread(target=monitor_input, daemon=True)
input_thread.start()

initialize_serial_connection()  # Initialize serial connection once before the loop

while running:
    random_delay = random.uniform(2, 4)
    time.sleep(random_delay)
    print(f"Runner checking after {random_delay:.2f} seconds delay...")
    try:
        runner()
    except Exception as e:
        print("An unexpected error occurred in the runner loop:")
        print(traceback.format_exc())

print("Runner has stopped.")
