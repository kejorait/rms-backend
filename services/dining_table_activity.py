import datetime as dt
import json
import re
from datetime import datetime
from uuid import uuid4

from fastapi.requests import Request
from fastapi.responses import JSONResponse
from sqlalchemy import func
from sqlalchemy.orm import aliased
from sqlalchemy.sql.expression import and_

from helper import constants
from helper.jsonHelper import ExtendEncoder
from models.bill import Bill
from models.table import Table
from models.table_session import TableSession
from utils.tinylog import getLogger, setupLog


class DiningTableService:
    name = "dining_table"
    setupLog(serviceName=__file__)
    
    def __init__(self):
        self.log = getLogger(serviceName=__file__)
        # self.log.info(" init  TableService ")
        self.content = Request.json

    def logging(self, msg):
        self.log.info(msg)

    # Get All Table
    def getAllDiningTable(self, request, db):
        jsonStr = {}
        try:
            # print("yes")
            # Define subquery to get the row number for each table.cd ordered by created_dt
            subquery = db.query(
                    Table.cd,
                    Table.nm,
                    Table.desc,
                    Table.is_billiard,
                    Bill.user_nm,
                    Bill.created_by,
                    Bill.is_closed,
                    Bill.is_paid,
                    Bill.created_dt.label('bill_created_dt'),
                    TableSession.created_dt.label('session_created_dt'),
                    TableSession.amount.label('session_amount'),
                    TableSession.is_open.label('session_is_open'),
                    TableSession.is_closed.label('session_is_closed'),
                    func.row_number().over(
                        partition_by=Table.cd,
                        order_by=[
                            Bill.created_dt.desc(),
                            TableSession.created_dt.desc()
                        ]
                    ).label('row_num')
                    )

            subquery = subquery.outerjoin(Bill, and_(
                        Bill.table_cd == Table.cd,
                        Bill.is_inactive == constants.NO,
                        Bill.is_delete == constants.NO,
                        Bill.is_paid == constants.NO
                    ))
            subquery = subquery.outerjoin(TableSession, and_(
                        Bill.cd == TableSession.bill_cd,
                        TableSession.is_inactive == constants.NO,
                        TableSession.is_delete == constants.NO,
                        TableSession.is_closed == constants.NO
                    ))
            
            subquery = subquery.filter(Table.is_inactive == constants.NO)
            subquery = subquery.filter(Table.is_delete == constants.NO)
            subquery = subquery.filter(Table.is_billiard == constants.NO)

            subquery = subquery.subquery()

            # Alias the subquery
            subquery_alias = aliased(subquery)

            # Query to select only the first row for each table.cd
            query = db.query(
                subquery_alias.c.cd,
                subquery_alias.c.nm,
                subquery_alias.c.desc,
                subquery_alias.c.is_billiard,
                subquery_alias.c.user_nm,
                subquery_alias.c.created_by,
                subquery_alias.c.is_closed,
                subquery_alias.c.is_paid,
                subquery_alias.c.session_created_dt,
                subquery_alias.c.session_amount,
                subquery_alias.c.session_is_open,
                subquery_alias.c.session_is_closed
            ).filter(subquery_alias.c.row_num == 1)

            # Order by cast table.cd as integer
            # query = query.order_by(cast(subquery_alias.c.cd, Integer).asc())

            # self.log.info(query.statement.compile(compile_kwargs={"literal_binds": True}))
            data = query.all()
            
            db.close()
            res = {}
            
            listData = []
            for mdl in data:
                data_list = {}
                data_list["cd"] = mdl.cd
                data_list["nm"] = mdl.nm
                number = re.search(r'\d+', mdl.nm)
                number = int(number.group()) if number else 0
                data_list["no"] = number
                data_list["desc"] = mdl.desc
                data_list["is_billiard"] = mdl.is_billiard

                session_status = ""

                if mdl.session_is_open == constants.YES:
                    session_status = "OPEN"
                elif mdl.session_is_open == constants.NO:
                    session_status = "FIXED"
                else:
                    session_status = "CLOSED"  # In case no conditions match

                data_list["session_status"] = session_status

                session_amount = 0
                if mdl.session_amount:
                    session_amount = mdl.session_amount

                data_list["session_amount"] = session_amount

                data_list["session_created_dt"] = mdl.session_created_dt
                
                if mdl.user_nm:
                    data_list["user_nm"] = mdl.user_nm
                    data_list["created_by"] = mdl.created_by
                    if mdl.is_paid == constants.YES:
                        status = "EMPTY"
                    elif mdl.is_closed == constants.YES and mdl.is_paid == constants.NO:
                        status = "CLOSED"
                    elif mdl.is_closed == constants.NO and mdl.is_paid == constants.NO:
                        status = "OCCUPIED"
                    else:
                        status = "UNKNOWN"  # In case no conditions match
                else:
                    status = "EMPTY"
                    data_list["created_by"] = ""
                    data_list["user_nm"] = ""
                
                data_list["status"] = status
                listData.append(data_list)

            listData = sorted(listData, key=lambda k: k['no'])
            res["data"] = listData
            res["status"] = "Success"
            res["isError"] = constants.NO
            jsonStr = res
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
    def createTable(self, request, db):
        jsonStr = {}
        
        try:
            table = Table()
            table.cd = uuid4().hex
            table.nm = request.nm
            table.desc = request.desc
            table.is_billiard = request.is_billiard
            table.created_dt = dt.datetime.now()
            table.created_by = request.created_by
            table.is_delete = constants.NO
            table.is_inactive = constants.NO

            db.add(table)
            db.commit()
            
            jsonStr["data"] = {"cd": table.cd}
            jsonStr["isError"] = constants.NO
            jsonStr["status"] = constants.STATUS_SUCCESS

        except Exception as ex:
            self.log.exception(" TableService")
            jsonStr["isError"] = constants.YES
            jsonStr["status"] = "Failed"
            response = JSONResponse(content=jsonStr)
            response.status_code = 500
            return response

        return jsonStr
    
    # Update Table
    def updateTable(self, request, db):
        jsonStr = {}
        try:
            # self.log.info("Response "+str(jsonStr))
            cd = request.cd
            table = db.query(Table).get(cd)
            table.nm = request.nm
            table.desc = request.desc
            table.is_billiard = request.is_billiard
            table.updated_dt = dt.datetime.now()
            table.updated_by = request.updated_by

            table_obj = table
            table_obj = json.loads(json.dumps(table_obj, cls=ExtendEncoder))
            db.commit()

            jsonStr["data"] = table_obj
            jsonStr["isError"] = constants.NO
            jsonStr["status"] = constants.STATUS_SUCCESS

        except Exception as ex:
            self.log.exception(" MenuService")
            jsonStr["data"] = str(ex)
            jsonStr["isError"] = constants.YES
            jsonStr["status"] = "Failed"
            response = JSONResponse(content=jsonStr)
            response.status_code = 500
            return response
        return jsonStr
    
    # Delete Table
    def deleteTable(self, request, db):
        jsonStr = {}
        try:
            # self.log.info("Response "+str(jsonStr))
            cd = request.cd
            table = db.query(Table).get(cd)
            table.is_delete = constants.YES
            table.updated_dt = dt.datetime.now()
            table.updated_by = request.deleted_by

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
    
    def deleteTableBulk(self, request, db):
        jsonStr = {"data": [], "isError": constants.NO, "status": "Success"}
        try:
            # Check if cd is a list
            cds = request.cd if isinstance(request.cd, list) else [request.cd]
            
            for cd in cds:
                table = db.query(Table).get(cd)
                if table:
                    table.is_delete = constants.YES
                    table.updated_dt = dt.datetime.now()
                    table.updated_by = request.deleted_by
                    jsonStr["data"].append({"cd": cd, "status": constants.STATUS_SUCCESS_DELETE})
                else:
                    jsonStr["data"].append({"cd": cd, "status": "Not Found"})
            
            db.commit()
        except Exception as ex:
            self.log.exception(" MenuService")
            jsonStr = {
                "isError": constants.YES,
                "status": "Failed",
                "data": str(ex)
            }
            return jsonStr, 500
        # self.log.info("Response "+str(jsonStr))
        return jsonStr
