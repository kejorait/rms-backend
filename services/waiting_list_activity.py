import datetime as dt
from datetime import datetime
from uuid import uuid4

from fastapi.requests import Request
from fastapi.responses import JSONResponse

from helper import constants
from models.bill import Bill
from models.table import Table
from models.waiting_list import WaitingList
from utils.tinylog import getLogger, setupLog


class WaitingListService:
    name = "waitinglist"
    setupLog(serviceName=__file__)
    
    def __init__(self):
        self.log = getLogger(serviceName=__file__)
        # self.log.info(" init  TableService ")
        self.content = Request.json

    def logging(self, msg):
        self.log.info(msg)

    # Get All Table
    def getAllWaitingList(self, request, db):
        jsonStr = {}
        # try:
        # self.log.info("Response "+str(jsonStr))

        query = db.query(
            WaitingList,
            Bill
        )
        query = query.join(Bill,
        Bill.table_cd == WaitingList.cd,
        isouter = True)
        query = query.filter(Bill.is_paid == constants.NO)
        query = query.filter(WaitingList.is_delete == constants.NO)
        query = query.order_by(WaitingList.created_dt.asc())
        # self.log.info(query.statement.compile(compile_kwargs={"literal_binds": True}))
        data = query.all()
        # print('data', data)
        db.close()
        res = {}
        
        listData = []
        x = 1
        for mdl_data in data:
            data_list = {}
            row = mdl_data.Bill
            mdl = mdl_data.WaitingList
            if row.is_paid == constants.YES:
                status = "EMPTY"
            if row.is_closed == constants.YES and row.is_paid == constants.NO:
                status = "CLOSED"
            if row.is_closed == constants.NO and row.is_paid == constants.NO:
                status = "OCCUPIED"
            data_list["number"] = x
            x=x+1
            data_list["cd"] = mdl.cd
            data_list["nm"] = mdl.nm
            data_list["created_dt"] = mdl.created_dt 
            data_list["status"] = status 
        
            listData.append(data_list)

        res["data"] = listData
        res["status"] = "Success"
        res["isError"] = constants.NO
        # jsonStr = json.dumps(res, default=str)
        jsonStr = res
            # self.log.info("Response "+str(jsonStr))
        # except Exception as ex:
        #     self.log.exception(" TableService")
        #     jsonStr["isError"] = constants.YES
        #     jsonStr["status"] = "Failed"
        #     return jsonStr, 500
        return jsonStr

 # Get All Table
    def getWaitingListDtl(self, request, db):
        jsonStr = {}
        try:
            # self.log.info("Response "+str(jsonStr))

            query = db.query(
                WaitingList,
                Bill
            )
            query = query.join(Bill,
            Bill.table_cd == WaitingList.cd,
            isouter = True)
            query = query.filter(Bill.is_paid == constants.NO)
            query = query.filter(WaitingList.is_delete == constants.NO)
            query = query.order_by(WaitingList.created_dt.asc())
            # self.log.info(query.statement.compile(compile_kwargs={"literal_binds": True}))
            data = query.all()
            # print('data', data)
            db.close()
            res = {}
            
            listData = []
            x = 1
            for mdl_data in data:
                mdl = mdl_data.WaitingList                
                data_list = {}
                data_list["number"] = x
                x=x+1
                data_list["cd"] = mdl.cd
                data_list["nm"] = mdl.nm
                data_list["created_dt"] = mdl.created_dt 
            
                listData.append(data_list)

            for x in listData:
                if x["cd"] == request.cd:
                    res["data"] = x

            query = db.query(
                Bill.table_cd
            )
            query = query.filter(Bill.is_paid == constants.NO)
            # self.log.info(query.statement.compile(compile_kwargs={"literal_binds": True}))
            data = query.all()
            # print('data', data)
            db.close()
            listFullTable = []
            for x in data:
                listFullTable.append(x.table_cd)
            # self.log.info(listFullTable)
            query = db.query(
                Table
            )
            query = query.filter(Table.cd.not_in(listFullTable))
            query = query.order_by(Table.cd.asc())
            # self.log.info(query.statement.compile(compile_kwargs={"literal_binds": True}))
            data = query.all()
            # print('data', data)
            db.close()
            listTable = []
            for mdl in data:
                data_list = {}
                data_list["table_cd"] = mdl.cd
                data_list["table_nm"] = mdl.nm
                listTable.append(data_list)
            res["table"] = listTable
            query = db.query(
                Bill.cd
            )
            query = query.filter(Bill.table_cd == request.cd)
            # self.log.info(query.statement.compile(compile_kwargs={"literal_binds": True}))
            data = query.first()
            # print('data', data)
            db.close()
            if data:
                res["bill_cd"] = data.cd
            else:
                res["bill_cd"] = ""
            # jsonStr = json.dumps(res, default=str)
            jsonStr = res
            # self.log.info("Response "+str(jsonStr))
        except Exception as ex:
            self.log.exception(" TableService")
            jsonStr["isError"] = constants.YES
            jsonStr["status"] = "Failed"
            return jsonStr, 500
        return jsonStr

    # Get Table By Id
    def getTable(self, request, db):
        jsonStr = {}
        try:
            # self.log.info("Response "+str(jsonStr))
            table_cd = request.table_cd

            query = db.query(Table.cd)
            query = query.filter(Table.cd == table_cd)
            query = query.filter(Table.is_delete == constants.NO)
            query = query.filter(Table.is_inactive == constants.NO)
            row = query.first()
            print(row)
            cd = row.cd
            # self.log.info(query.statement.compile(compile_kwargs={"literal_binds": True}))
            db.close()

            query = db.query(
                Table.cd,
                Table
            )
            query = query.filter(Table.cd == table_cd)
            data = query.all()
            print('data', data)
            db.close()
            res = {}
            
            listData = []
            for mdl in data:

                data_list = {}
                data_list["cd"] = mdl.Table.cd
                data_list["tablename"] = mdl.Table.tablename
                data_list["created_dt"] = datetime.timestamp(mdl.Table.created_dt)
                data_list["created_by"] = mdl.Table.created_by
                data_list["is_inactive"] = mdl.Table.is_inactive
                data_list["is_delete"] = mdl.Table.is_delete
                listData.append(data_list)

            res["data"] = listData
            res["status"] = "Success"
            res["isError"] = constants.NO
            # jsonStr = json.dumps(res, default=str)
            jsonStr = res
            # self.log.info("Response "+str(jsonStr))
        except Exception as ex:
            self.log.exception(" TableService")
            jsonStr["isError"] = constants.YES
            jsonStr["status"] = "Failed"
            return jsonStr, 500
        return jsonStr
    
    # Create Table
    def addWaitingList(self, request, db):
        jsonStr = {}
        
        try:
            
            query = db.query(
                WaitingList
            )
            query = query.filter(WaitingList.nm == request.nm)
            query = query.filter(WaitingList.is_delete == constants.NO)
            query = query.order_by(WaitingList.cd.asc())
            # self.log.info(query.statement.compile(compile_kwargs={"literal_binds": True}))
            data = query.all()
            if data:
                # self.log.exception(" TableService")
                ex = Exception("Data Already Exist")
                self.log.error(ex)
                response = JSONResponse(status_code=500, content={"data": str(ex), "isError": constants.YES, "status": constants.STATUS_FAILED})
                return response
            # End Input Validation

            # self.log.info("Response "+str(jsonStr))
            table = WaitingList()
            table.cd = uuid4().hex
            table.nm = request.nm
            table.created_dt = dt.datetime.now()
            table.is_delete = constants.NO

            table_obj = table
            db.add(table)
            db.commit()

            data = {
                "cd": table.cd,
                "nm": table.nm,
                "created_dt": table.created_dt,
                "is_delete": table.is_delete
            }

            jsonStr["data"] = data
            jsonStr["isError"] = constants.NO
            jsonStr["status"] = "Success"

        except Exception as ex:
            # self.log.exception(" TableService")
            self.log.error(ex)
            response = JSONResponse(status_code=500, content={"data": str(ex), "isError": constants.YES, "status": constants.STATUS_FAILED})
            return response
        
        return jsonStr
    
    # Update Table
    def updateTable(self, request, db):
        jsonStr = {}
        try:
            # self.log.info("Response "+str(jsonStr))
            cd = request.cd
            table = db.query(Table).get(cd)
            table.name = request.name
            table.tablename = request.tablename
            table.role_cd = request.role_cd
            table.updated_dt = dt.datetime.now()
            table.updated_by = request.updated_by
            table.is_delete = request.is_delete
            table.is_inactive = request.is_inactive
            table.is_resign = request.is_resign

            db.commit()

            jsonStr["data"] = constants.STATUS_SUCCESS
            jsonStr["isError"] = constants.NO
            jsonStr["status"] = "Success"

        except Exception as ex:
            self.log.exception(" MenuService")
            jsonStr["isError"] = constants.YES
            jsonStr["status"] = "Failed"
            return jsonStr, 500
        # self.log.info("Response "+str(jsonStr))
        return jsonStr
    
    # Delete Table
    def deleteWaitingList(self, request, db):
        jsonStr = {}
        try:
            # self.log.info("Response "+str(jsonStr))
            cd = request.cd
            if cd.isdigit():
                # self.log.exception(" MenuService")
                jsonStr["data"] = "is table"
                jsonStr["isError"] = constants.YES
                jsonStr["status"] = "Failed"
                return jsonStr, 500
            table = db.query(WaitingList).get(cd)
            table.is_delete = constants.YES

            db.commit()

            jsonStr["data"] = constants.STATUS_SUCCESS_DELETE
            jsonStr["isError"] = constants.NO
            jsonStr["status"] = "Success"

        except Exception as ex:
            self.log.exception(" MenuService")
            jsonStr["isError"] = constants.YES
            jsonStr["status"] = "Failed"
            return jsonStr, 500
        # self.log.info("Response "+str(jsonStr))
        return jsonStr