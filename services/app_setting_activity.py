import datetime as dt
from datetime import datetime

# import cups
from fastapi.responses import JSONResponse
import win32print

from helper import constants
from models.app_setting import AppSetting
from utils.tinylog import getLogger, setupLog


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
                query = db.query(AppSetting).filter(AppSetting.cd == key)
                query = query.filter(AppSetting.is_delete == constants.NO)
                query = query.filter(AppSetting.is_inactive == constants.NO)
                query = query.first()

                if not query:
                    query = AppSetting()
                    query.cd = key
                    # query.nm = key replace _ with space, and caps lock
                    query.nm = key.replace("_", " ").upper()
                    query.created_dt = dt.datetime.now()
                    query.created_by = request.updated_by
                    query.value = value

                    db.add(query)

                else:
                    query.value = value
                    query.updated_dt = dt.datetime.now()
                    query.updated_by = request.updated_by

            db.commit()

            db.refresh(query)
            
            jsonStr["data"] = query
            jsonStr["isError"] = constants.NO
            jsonStr["status"] = constants.STATUS_SUCCESS
            return jsonStr
        
        except Exception as ex:
            # print(ex)
            self.log.error(ex)
            response = JSONResponse(status_code=500, content={"data": str(ex), "isError": constants.YES, "status": "Failed"})
            response.status_code = 500
            return response

    def getPrinters(self):
        printers = [printer[2] for printer in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)]
        return printers 
    
    # def getPrinters(self):
    #     conn = cups.Connection()
    #     # printers = [printer for printer in conn.getPrinters()]
    #     # mock printer list windows
    #     printers = ["Microsoft XPS Document Writer", "Microsoft Print to PDF", "Epson 1112"]
    #     return printers
    
    def getSerialPorts(self):
        conn = cups.Connection()
        # printers = [printer for printer in conn.getPrinters()]
        # mock printer list windows
        printers = ["COM1", "COM2", "COM3"]
        return printers