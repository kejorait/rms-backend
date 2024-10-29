import os
import random
import time
from zoneinfo import ZoneInfo

from helper import constants
from helper.database import get_db
from models.table_session import TableSession
from models.app_setting import AppSetting

desired_timezone = ZoneInfo('Asia/Singapore')

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
            query = db.query(TableSession)
            query = query.filter(TableSession.is_delete == constants.NO)
            query = query.filter(TableSession.is_inactive == constants.NO)
            query = query.filter(TableSession.serial_sent == constants.NO)
            query = query.filter(TableSession.amount != None)
            query = query.order_by(TableSession.created_dt.asc())
            # print(query.statement.compile(compile_kwargs={"literal_binds": True}))
            res =  query.first()
            if res:
                print(res.cd)
            
    except Exception as e:
        db.rollback()  # Rollback if any error occurs
        raise
    finally:
        db.close()  # Ensure that connection is closed or returned to the pool


print("Starting queue runner...")

while True:
    random_delay = random.uniform(1, 3)  # Stagger the runner's execution (1-3 seconds)
    time.sleep(random_delay)
    print(f"Runner checking after {random_delay:.2f} seconds delay...")
    runner()
