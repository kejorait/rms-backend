import json
from datetime import datetime
import datetime as dt
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

          
            query = db.session.query(
                Role
            )
            query = query.filter(Role.is_delete == constants.NO)
            data = query.all()
            db.session.close()
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
            jsonStr = json.dumps(res, cls = ExtendEncoder)
            # self.log.info("Response " + str(jsonStr))
        except Exception as ex:
            self.log.exception(" RoleService")
            jsonStr["isError"] = constants.YES
            jsonStr["status"] = "Failed"
        return jsonStr