import datetime as dt
from uuid import uuid4

from fastapi.requests import Request

from helper import constants
from models.bill import Bill
from models.table_session import TableSession
from utils.tinylog import getLogger, setupLog


class TableSessionService:

    name = "tableSession"
    setupLog(serviceName=__file__)

    def __init__(self):
        self.log = getLogger(serviceName=__file__)
        # self.log.info(" init  TableSessionService ")
        self.content = Request.json

    # def getTableSessionByTable(self, request, db):
    def tableSessionOpen(self, request, db):
        jsonStr = {}
        
        try:

            query = db.query(TableSession.cd)
            query = query.filter(TableSession.table_cd == request.table_cd)
            query = query.filter(TableSession.is_inactive == constants.NO)
            query = query.filter(TableSession.is_delete == constants.NO)
            query = query.filter(TableSession.is_closed == constants.NO)
            data = query.first()

            if not data:
                bill_cd = request.bill_cd
                query = db.query(Bill.cd)
                query = query.filter(Bill.cd == bill_cd)
                query = query.filter(Bill.is_inactive == constants.NO)
                query = query.filter(Bill.is_delete == constants.NO)
                query = query.filter(Bill.is_closed == constants.NO)
                data = query.first()

                if not data:
                    jsonStr["data"] = "Bill not found"
                    jsonStr["isError"] = constants.YES
                    jsonStr["status"] = "Failed"
                    return jsonStr, 500
                
                else:
                    table_session = TableSession()
                    table_session.cd = uuid4().hex
                    table_session.table_cd = request.table_cd
                    table_session.created_dt = dt.datetime.now()
                    table_session.created_by = request.created_by
                    table_session.bill_cd = bill_cd
                    table_session.is_inactive = constants.NO
                    table_session.is_delete = constants.NO
                    table_session.is_open = constants.YES
                    table_session.is_closed = constants.NO
                    table_session.is_paid = constants.NO
                    table_session.serial_sent = constants.NO

                    db.add(table_session)
                    db.commit()

                    jsonStr["data"] = {"cd": table_session.cd}
                    jsonStr["isError"] = constants.NO
                    jsonStr["status"] = "Success"

            else:
                # self.log.exception(" TableSessionService")
                jsonStr["data"] = "There is ongoing table session"
                jsonStr["isError"] = constants.YES
                jsonStr["status"] = "Failed"
                return jsonStr, 500
            
        except Exception as ex:
            self.log.exception(" TableSessionService")
            jsonStr["isError"] = constants.YES
            jsonStr["status"] = "Failed"
            return jsonStr, 500
        # self.log.info("Response " + str(jsonStr))

        return jsonStr
        

    def tableSessionFixed(self, request, db):
        jsonStr = {}
        
        try:

            query = db.query(TableSession.cd)
            query = query.filter(TableSession.table_cd == request.table_cd)
            query = query.filter(TableSession.is_inactive == constants.NO)
            query = query.filter(TableSession.is_delete == constants.NO)
            query = query.filter(TableSession.is_closed == constants.NO)
            query = query.order_by(TableSession.created_dt.desc())
            data = query.first()
            

            if not data:
                bill_cd = request.bill_cd
                query = db.query(Bill.cd)
                query = query.filter(Bill.cd == bill_cd)
                query = query.filter(Bill.is_inactive == constants.NO)
                query = query.filter(Bill.is_delete == constants.NO)
                query = query.filter(Bill.is_closed == constants.NO)
                data = query.first()

                if not data:
                    jsonStr["data"] = "Bill not found"
                    jsonStr["isError"] = constants.YES
                    jsonStr["status"] = "Failed"
                    return jsonStr, 500
                
                else:
                    table_session = TableSession()
                    table_session.cd = uuid4().hex
                    table_session.table_cd = request.table_cd
                    table_session.created_dt = dt.datetime.now()
                    table_session.created_by = request.created_by
                    table_session.amount = request.amount
                    table_session.bill_cd = request.bill_cd
                    table_session.is_inactive = constants.NO
                    table_session.is_delete = constants.NO
                    table_session.is_open = constants.NO
                    table_session.is_closed = constants.NO
                    table_session.is_paid = constants.NO
                    table_session.serial_sent = constants.NO

                    db.add(table_session)
                    db.commit()

                    jsonStr["data"] = {"cd": table_session.cd}
                    jsonStr["isError"] = constants.NO
                    jsonStr["status"] = "Success"

            else:
                # self.log.exception(" TableSessionService")
                jsonStr["data"] = "There is ongoing table session"
                jsonStr["isError"] = constants.YES
                jsonStr["status"] = "Failed"
                return jsonStr, 500
            
        except Exception as ex:
            self.log.exception(" TableSessionService")
            jsonStr["isError"] = constants.YES
            jsonStr["status"] = "Failed"
            return jsonStr, 500
        # self.log.info("Response " + str(jsonStr))

        return jsonStr
        
    def tableSessionClose(self, request, db):
        jsonStr = {}
        
        try:
            latest_session = db.query(TableSession.cd).filter(TableSession.table_cd == request.table_cd)
            latest_session = latest_session.filter(TableSession.is_inactive == constants.NO)
            latest_session = latest_session.filter(TableSession.is_delete == constants.NO)
            latest_session = latest_session.filter(TableSession.is_closed == constants.NO)
            latest_session = latest_session.order_by(TableSession.created_dt.desc()).first()

            table_session = db.query(TableSession).get(latest_session)
            table_session.is_closed = constants.YES
            table_session.closed_dt = dt.datetime.now()
            table_session.closed_by = request.closed_by

            db.commit()

            jsonStr["data"] = constants.STATUS_SUCCESS
            jsonStr["isError"] = constants.NO
            jsonStr["status"] = "Success"

        except Exception as ex:
            self.log.exception(" TableSessionService")
            jsonStr["isError"] = constants.YES
            jsonStr["status"] = "Failed"
            return jsonStr, 500
        # self.log.info("Response " + str(jsonStr))

        return jsonStr