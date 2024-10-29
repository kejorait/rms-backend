import json
from datetime import datetime
import datetime as dt

from fastapi.responses import JSONResponse
from models.table import Table
from models.bill import Bill
from models.app_setting import AppSetting
from helper.jsonHelper import ExtendEncoder
from helper import constants
from utils.tinylog import getLogger, setupLog
from uuid import uuid4
from sqlalchemy import func,Integer
from sqlalchemy.sql.expression import cast, and_
import sqlalchemy
from sqlalchemy.orm import aliased
from fastapi import HTTPException

import win32print

class AppSettingService:
    name = "app_setting"
    setupLog(serviceName=__file__)
    
    def __init__(self):
        self.log = getLogger(serviceName=__file__)

    def logging(self, msg):
        self.log.info(msg)

    # Get All Table
    def getAllAppSetting(self, request, db):
        jsonStr = {}
        try:
            # Define subquery to get the row number for each table.cd ordered by created_dt
            query = db.query(AppSetting)
            query = query.filter(AppSetting.is_delete == constants.NO)
            query = query.filter(AppSetting.is_inactive == constants.NO)
            data = query.all()
            db.close()
            res = {}
            
            listData = []
            for mdl in data:

                data_list = {}
                data_list["cd"] = mdl.cd
                data_list["nm"] = mdl.nm
                data_list["desc"] = mdl.desc
                data_list["value"] = mdl.value
                if mdl.created_dt:
                    data_list["created_dt"] = datetime.timestamp(mdl.created_dt)
                else:
                    data_list["created_dt"] = ""
                data_list["created_by"] = mdl.created_by
                data_list["is_inactive"] = mdl.is_inactive
                data_list["is_delete"] = mdl.is_delete
                listData.append(data_list)

            jsonStr["data"] = listData
            jsonStr["isError"] = constants.NO
            jsonStr["status"] = constants.STATUS_SUCCESS
            return jsonStr
        
        except Exception as ex:
            # print(ex)
            self.log.error(ex)
            response = JSONResponse(status_code=500, content={"data": str(ex), "isError": constants.YES, "status": "Failed"})
            response.status_code = 500
            return response


    # Get Table By Id
    def updateAppSetting(self, request, db):
        jsonStr = {}
        try:
            # print(self.content)
            for key, value in request.data.items():
                # print(key, value)
                query = db.query(AppSetting).get(key)
                query.value = value
                query.updated_dt = dt.datetime.now()
                query.updated_by = request.updated_by

            db.commit()
            
            jsonStr["data"] = request.data
            jsonStr["isError"] = constants.NO
            jsonStr["status"] = constants.STATUS_SUCCESS
            return jsonStr
        
        except Exception as ex:
            # print(ex)
            self.log.error(ex)
            response = JSONResponse(status_code=500, content={"data": str(ex), "isError": constants.YES, "status": "Failed"})
            response.status_code = 500
            return response

    def getPrinters():
        printers = [printer[2] for printer in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)]
        return printers 