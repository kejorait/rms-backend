import json
import os
import datetime
from fastapi.responses import JSONResponse
from rich.console import Console
from models.menu import Menu
from models.table import Table
from models.bill import Bill
from models.category import Category
from helper.jsonHelper import ExtendEncoder
from helper import constants
from utils.tinylog import getLogger, setupLog
from uuid import uuid4
from models.waiting_list import WaitingList
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import dotenv
from fastapi.requests import Request
from fastapi import HTTPException

load_dotenv()


class MenuService:

    name = "Menu"
    setupLog(serviceName=__file__)

    ALLOWED_EXTENSIONS = set(["png", "jpg", "jpeg"])
    MENU_PATH = os.getenv("MENU_PATH")
    MENU_FOLDER = "./" + MENU_PATH
    MENU_URL = os.getenv("HOST") + "/" + MENU_PATH + "/"

    def __init__(self):
        self.log = getLogger(serviceName=__file__)
        # self.log.info(" init  MenuService ")

    def allowed_file(self, filename):
        return (
            "." in filename
            and filename.rsplit(".", 1)[1].lower() in self.ALLOWED_EXTENSIONS
        )

    def addMenu(self, request, db):
        jsonStr = {}
        try:
            reqdata = request.form
            # self.log.info("Response "+str(jsonStr))
            menu = Menu()
            menu.cd = uuid4().hex
            menu.nm = reqdata["nm"]
            menu.desc = reqdata["desc"]
            menu.price = reqdata["price"]
            menu.category_cd = reqdata["category_cd"]
            menu.created_dt = datetime.datetime.now()
            menu.created_by = reqdata["created_by"]
            menu.is_delete = constants.NO
            menu.is_inactive = constants.NO

            if "file" not in Request.files:
                jsonStr["data"] = "No file"
                jsonStr["isError"] = constants.NO
                jsonStr["status"] = "Success"
            else:
                file = Request.files["file"]
                # if user does not select file, browser also
                # submit a empty part without filename
                if file.filename == "":
                    jsonStr["data"] = "No selected file"
                    jsonStr["isError"] = constants.NO
                    jsonStr["status"] = "Success"
                if file and self.allowed_file(file.filename):
                    filename = str(file.filename)
                    filename_data = filename[:-4]
                    filename_ext = filename[-4:]
                    timenow = str(datetime.datetime.now())
                    datenow = timenow[:-16]
                    timenow = timenow[11:]
                    filename = (
                        filename_data
                        + "-"
                        + datenow
                        + "-"
                        + timenow
                        + "."
                        + filename_ext
                    )
                    filename = secure_filename(filename)
                    self.log.info(filename)
                    file.save(os.path.join(self.MENU_FOLDER, filename))
                    jsonStr["data"] = "Success"
                    jsonStr["isError"] = constants.NO
                    jsonStr["status"] = "Success"
                    menu.img = filename

            db.add(menu)
            db.commit()

        except Exception as ex:
            self.log.error(ex)
            response = JSONResponse(status_code=500, content={"data": str(ex), "isError": constants.YES, "status": "Failed"})
            response.status_code = 500
            return response
        return jsonStr

    def updateMenu(self, request, db):
        jsonStr = {}
        try:
            reqdata = Request.form
            # self.log.info("Response "+str(jsonStr))
            cd = reqdata["cd"]
            menu = db.query(Menu).get(cd)
            menu.nm = reqdata["nm"]
            menu.desc = reqdata["desc"]
            menu.price = reqdata["price"]
            menu.category_cd = reqdata["category_cd"]
            menu.updated_dt = datetime.datetime.now()
            menu.updated_by = reqdata["updated_by"]

            if "file" not in Request.files:
                jsonStr["data"] = "No file"
                jsonStr["isError"] = constants.NO
                jsonStr["status"] = "Success"
            else:
                file = Request.files["file"]
                # if user does not select file, browser also
                # submit a empty part without filename
                if file.filename == "":
                    jsonStr["data"] = "No selected file"
                    jsonStr["isError"] = constants.NO
                    jsonStr["status"] = "Success"
                if file and self.allowed_file(file.filename):
                    filename = str(file.filename)
                    filename_data = filename[:-4]
                    filename_ext = filename[-4:]
                    timenow = str(datetime.datetime.now())
                    datenow = timenow[:-16]
                    timenow = timenow[11:]
                    filename = (
                        filename_data
                        + "-"
                        + datenow
                        + "-"
                        + timenow
                        + "."
                        + filename_ext
                    )
                    filename = secure_filename(filename)
                    self.log.info(filename)
                    file.save(os.path.join(self.MENU_FOLDER, filename))
                    jsonStr["data"] = "Success"
                    jsonStr["isError"] = constants.NO
                    jsonStr["status"] = "Success"
                    menu.img = filename

            db.commit()

        except Exception as ex:
            self.log.error(ex)
            response = JSONResponse(status_code=500, content={"data": str(ex), "isError": constants.YES, "status": "Failed"})
            response.status_code = 500
            return response
        # self.log.info("Response "+str(jsonStr))
        return jsonStr

    def deleteMenu(self, request, db):
        jsonStr = {}
        try:
            # self.log.info("Request "+str(Request.json))
            cd = Request.json["cd"]
            menu = db.query(Menu).get(cd)
            menu.updated_dt = datetime.datetime.now()
            menu.updated_by = Request.json["updated_by"]
            menu.is_delete = constants.YES

            db.commit()

            jsonStr["isError"] = constants.NO
            jsonStr["status"] = "Success"
        except Exception as ex:
            self.log.exception(" MenuService")
            jsonStr["isError"] = constants.YES
            jsonStr["status"] = "Failed"
            return jsonStr, 500
        # self.log.info("Response "+str(jsonStr))
        return jsonStr

    def getMenu(self, request, db):
        jsonStr = {}
        try:
            # self.log.info("Request "+str(Request.json))
            if "bill_cd" in Request.json:
                bill_cd = Request.json["bill_cd"]
            else:
                # self.log.exception(" MenuService")
                jsonStr["isError"] = constants.YES
                jsonStr["status"] = "Failed"
                return jsonStr, 500

            query = db.query(Bill.cd)
            query = query.filter(Bill.cd == bill_cd)
            query = query.filter(Bill.is_closed == constants.NO)
            query = query.filter(Bill.is_delete == constants.NO)
            query = query.filter(Bill.is_inactive == constants.NO)
            query = query.filter(Bill.is_paid == constants.NO)
            query = query.order_by(Bill.created_dt.desc())
            row = query.first()
            # self.log.info(query.statement.compile(compile_kwargs={"literal_binds": True}))
            db.close()
            query = db.query(WaitingList)
            query = query.join(Bill, Bill.table_cd == WaitingList.cd)
            # query = query.filter(Bill.cd == bill_cd)
            wl_data = query.first()
            # self.log.info(query.statement.compile(compile_kwargs={"literal_binds": True}))
            db.close()
            query = db.query(Table)
            query = query.join(Bill, Bill.table_cd == Table.cd)
            # query = query.filter(Bill.cd == bill_cd)
            table_data = query.first()
            # self.log.info(query.statement.compile(compile_kwargs={"literal_binds": True}))
            db.close()
            # self.log.info(row)
            if row:
                query = db.query(
                    Menu,
                    Category.nm.label("category_nm"),
                )
                query = query.join(Category, Category.cd == Menu.category_cd)
                query = query.filter(Menu.is_delete == constants.NO)
                query = query.filter(Menu.is_inactive == constants.NO)
                query = query.order_by(Menu.created_dt.asc())
                data = query.all()
                # self.log.info(query.statement.compile(compile_kwargs={"literal_binds": True}))
                db.close()
                res = {}

                listData = []
                listCategory = []
                for mdl in data:
                    listCategory.append(mdl.category_nm)

                for mdl in set(listCategory):
                    data_list = {}
                    data_list["name"] = mdl
                    if table_data:
                        data_list["table_nm"] = table_data.nm
                    else:
                        data_list["table_nm"] = "Waiting List - " + wl_data.nm
                    menu_list = []
                    for mdl2 in data:
                        # self.log.info(mdl2.Menu.nm)
                        if mdl == mdl2.category_nm:
                            menu_list_data = {}
                            menu_list_data["cd"] = mdl2.Menu.cd
                            menu_list_data["nm"] = mdl2.Menu.nm
                            if mdl2.Menu.img:
                                menu_list_data["img"] = self.MENU_URL + mdl2.Menu.img
                            else:
                                menu_list_data["img"] = ""
                            menu_list_data["desc"] = mdl2.Menu.desc
                            menu_list_data["price"] = mdl2.Menu.price
                            menu_list_data["category_cd"] = mdl2.Menu.category_cd
                            menu_list_data["created_dt"] = mdl2.Menu.created_dt
                            menu_list_data["created_by"] = mdl2.Menu.created_by
                            menu_list_data["is_inactive"] = mdl2.Menu.is_inactive
                            menu_list_data["is_delete"] = mdl2.Menu.is_delete
                            menu_list_data["updated_dt"] = mdl2.Menu.updated_dt
                            menu_list_data["updated_by"] = mdl2.Menu.updated_by

                            menu_list.append(menu_list_data)

                    menu_list.sort(key=lambda x: x["nm"], reverse=False)

                    data_list["menu"] = menu_list
                    listData.append(data_list)
                # self.log.info(menu_list)
                listData.sort(key=lambda x: x["name"], reverse=False)
                res["data"] = listData
                res["status"] = "Success"
                res["isError"] = constants.NO
                jsonStr = res
            else:
                jsonStr["data"] = []
                jsonStr["isError"] = constants.YES
                jsonStr["status"] = "Failed"
                return jsonStr, 500
        except Exception as ex:
            self.log.exception(" MenuService")
            jsonStr["isError"] = constants.YES
            jsonStr["status"] = "Failed"
            return jsonStr, 500
        # self.log.info("Response "+str(jsonStr))
        return jsonStr

    def getMenuAll(self, request, db):
        jsonStr = {}
        try:
            # self.log.info("Request "+str(Request.json))

            query = db.query(
                Menu,
                Category.nm.label("category_nm"),
            )
            query = query.join(Category, Category.cd == Menu.category_cd)
            query = query.filter(Menu.is_delete == constants.NO)
            search = request.search
            if search:
                query = query.filter(Menu.nm.ilike("%{}%".format(search)))
            query = query.filter(Menu.is_inactive == constants.NO)
            query = query.order_by(Menu.created_dt.asc())
            data = query.all()
            # self.log.info(query.statement.compile(compile_kwargs={"literal_binds": True}))
            db.close()
            res = {}

            listData = []
            listCategory = []
            for mdl in data:
                listCategory.append(mdl.category_nm)

            for mdl in set(listCategory):
                data_list = {}
                data_list["name"] = mdl
                menu_list = []
                for mdl2 in data:
                    # self.log.info(mdl2.Menu.nm)
                    if mdl == mdl2.category_nm:
                        menu_list_data = {}
                        menu_list_data["cd"] = mdl2.Menu.cd
                        menu_list_data["nm"] = mdl2.Menu.nm
                        if mdl2.Menu.img:
                            menu_list_data["img"] = str(self.MENU_URL) + str(
                                mdl2.Menu.img
                            )
                        else:
                            menu_list_data["img"] = ""
                        menu_list_data["desc"] = mdl2.Menu.desc
                        menu_list_data["price"] = mdl2.Menu.price
                        menu_list_data["category_cd"] = mdl2.Menu.category_cd
                        menu_list_data["created_dt"] = mdl2.Menu.created_dt
                        menu_list_data["created_by"] = mdl2.Menu.created_by
                        menu_list_data["is_inactive"] = mdl2.Menu.is_inactive
                        menu_list_data["is_delete"] = mdl2.Menu.is_delete
                        menu_list_data["updated_dt"] = mdl2.Menu.updated_dt
                        menu_list_data["updated_by"] = mdl2.Menu.updated_by

                        menu_list.append(menu_list_data)

                menu_list.sort(key=lambda x: x["nm"], reverse=False)

                data_list["menu"] = menu_list
                listData.append(data_list)
            # self.log.info(menu_list)
            listData.sort(key=lambda x: x["name"], reverse=False)
            res["data"] = listData
            res["status"] = "Success"
            res["isError"] = constants.NO
            jsonStr = res
        except Exception as ex:
            self.log.exception(" MenuService")
            jsonStr["isError"] = constants.YES
            jsonStr["status"] = "Failed"
            return jsonStr, 500
        # self.log.info("Response "+str(jsonStr))
        return jsonStr

    def getMenuByCode(self, request, db):
        jsonStr = {}
        try:
            # self.log.info("Request "+str(Request.json))

            cd = request.cd
            query = db.query(
                Menu,
                Category.cd.label("category_cd"),
                Category.nm.label("category_nm"),
            )
            query = query.join(Category, Category.cd == Menu.category_cd)
            query = query.filter(Menu.is_delete == constants.NO)
            query = query.filter(Menu.is_inactive == constants.NO)
            query = query.filter(Menu.cd == cd)
            data = query.first()
            # self.log.info(query.statement.compile(compile_kwargs={"literal_binds": True}))
            self.log.info(data)
            db.close()
            res = {}
            data_list = {}
            data_list["cd"] = data.Menu.cd
            data_list["nm"] = data.Menu.nm
            if data.Menu.img:
                data_list["img"] = self.MENU_URL + data.Menu.img
            else:
                data_list["img"] = ""
            data_list["desc"] = data.Menu.desc
            data_list["price"] = data.Menu.price
            data_list["category_cd"] = data.Menu.category_cd
            data_list["created_dt"] = data.Menu.created_dt
            data_list["created_by"] = data.Menu.created_by
            data_list["is_inactive"] = data.Menu.is_inactive
            data_list["is_delete"] = data.Menu.is_delete
            data_list["updated_dt"] = data.Menu.updated_dt
            data_list["updated_by"] = data.Menu.updated_by
            data_list["category_cd"] = data.category_cd
            data_list["category_nm"] = data.category_nm
            data_list["is_drink"] = data.Menu.is_drink

            # self.log.info(menu_list)
            res["data"] = data_list
            res["status"] = "Success"
            res["isError"] = constants.NO
            jsonStr = res
        except Exception as ex:
            self.log.error(ex)
            response = JSONResponse(status_code=500, content={"data": str(ex), "isError": constants.YES, "status": constants.STATUS_FAILED})
            return response
        # self.log.info("Response "+str(jsonStr))
        return jsonStr
