import json
from datetime import datetime
import datetime as dt
from fastapi.responses import JSONResponse
from rich.console import Console
from models.menu import Menu
from models.table import Table
from models.role import Role
from models.category import Category
from helper.jsonHelper import ExtendEncoder
from helper import constants
from utils.tinylog import getLogger, setupLog
from uuid import uuid4
from fastapi.requests import Request
from fastapi import HTTPException

class RoleService:
    
    name = "Role"
    setupLog(serviceName=__file__)
    
    def __init__(self):
        self.log = getLogger(serviceName=__file__)
        # self.log.info(" init  RoleService ")
        self.content = Request.json

    def logging(self, msg):
        self.log.info(msg)

    def getAllRole(self, request, db):
        jsonStr = {}
        try:
            # self.log.info("Response "+str(jsonStr))

          
            query = db.query(
                Role
            )
            query = query.filter(Role.is_delete == constants.NO)
            data = query.all()
            db.close()
            res = {}
            
            listData = []
            for mdl in data:
                data_list = {}
                data_list["cd"] = mdl.cd
                data_list["nm"] = mdl.nm
                data_list["created_dt"] = mdl.created_dt
                data_list["created_by"] = mdl.created_by
                data_list["updated_dt"] = mdl.created_dt
                data_list["updated_by"] = mdl.created_by
                data_list["is_delete"] = mdl.is_delete
                listData.append(data_list)

            res["data"] = listData
            res["status"] = "Success"
            res["isError"] = constants.NO
            jsonStr = res
            # self.log.info("Response " + str(jsonStr))
        except Exception as ex:
            self.log.error(ex)
            response = JSONResponse(status_code=500, content={"data": str(ex), "isError": constants.YES, "status": constants.STATUS_FAILED})
            response.status_code = 500
            return response
        return jsonStr