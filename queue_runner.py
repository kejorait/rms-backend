import datetime
import os
import random
import re
import time

from helper import constants
from helper.database import get_db
from models.app_setting import AppSetting
from models.table import Table

gen_bucket = os.getenv("BUCKET")

# COM_PORT = '/dev/tty10'  # Example: 'COM3'
BAUD_RATE = 9600

def runner():
    try:
        db = next(get_db())

        query = db.query(AppSetting.cd, AppSetting.value)
        query = query.filter(AppSetting.cd == 'com_port')
        query = query.filter(AppSetting.is_inactive == constants.NO)
        query = query.filter(AppSetting.is_delete == constants.NO)
        res =  query.first()

        if res:
            com_port = res.value
            print("com_port", com_port)
            query = db.query(Table)
            query = query.filter(Table.is_delete == constants.NO)
            query = query.filter(Table.is_inactive == constants.NO)
            query = query.filter(Table.is_billiard == constants.YES)
            # print(query.statement.compile(compile_kwargs={"literal_binds": True}))
            res =  query.all()
            if res:
                for mdl in res:

                    number = re.search(r'\d+', mdl.nm)
                    number = int(number.group()) if number else 0

                    if mdl.serial_off_dt:
                        if mdl.serial_off_dt <= datetime.datetime.now():
                            if mdl.sent_closed == constants.NO:

                                # ser = serial.Serial(com_port.value, '9600', timeout=1)

                                # ser.write(("RELAY " + str(number) + " OFF" + '\n').encode())  # Send command
                                # time.sleep(0.5)  # Wait for the Arduino to process the command
                                # response = ser.read_all().decode().strip()  # Read the response
                                print(f"Command: RELAY {number} OFF\n")
                                # print(f"Response: {response}\n")

                                mdl.serial_status = 'OFF'
                                mdl.serial_off_dt = None
                                mdl.sent_closed = constants.YES

                                db.commit()

                    if mdl.serial_status == 'ON' and mdl.serial_sent == constants.NO:
                        # ser = serial.Serial(com_port.value, '9600', timeout=1)

                        # ser.write(("RELAY " + str(number) + " ON" + '\n').encode())  # Send command
                        # time.sleep(0.5)  # Wait for the Arduino to process the command
                        # response = ser.read_all().decode().strip()  # Read the response
                        print(f"Command: RELAY {number} ON\n")
                        # print(f"Response: {response}\n")
                        mdl.serial_sent = constants.YES
                        db.commit()

                    
                    

                    print(number, mdl.serial_status, mdl.serial_sent, mdl.sent_closed, mdl.serial_off_dt)
            
    except Exception as e:
        db.rollback()  # Rollback if any error occurs
        raise
    finally:
        db.close()  # Ensure that connection is closed or returned to the pool


print("Starting queue runner...")

while True:
    random_delay = random.uniform(2, 4)  # Stagger the runner's execution (1-3 seconds)
    time.sleep(random_delay)
    print(f"Runner checking after {random_delay:.2f} seconds delay...")
    runner()
