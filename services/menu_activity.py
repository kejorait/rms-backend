import datetime
import json
import os
from shutil import copyfileobj
from uuid import uuid4

from dotenv import load_dotenv
from fastapi.responses import JSONResponse
from werkzeug.utils import secure_filename

from helper import constants
from helper.jsonHelper import ExtendEncoder
from models.app_setting import AppSetting
from models.bill import Bill
from models.category import Category
from models.menu import Menu
from models.table import Table
from models.waiting_list import WaitingList
from utils.tinylog import getLogger, setupLog

load_dotenv()


class MenuService:

    name = "Menu"
    setupLog(serviceName=__file__)

    ALLOWED_EXTENSIONS = set(["png", "jpg", "jpeg"])
    API_PREFIX = os.getenv("API_PREFIX")
    MENU_PATH = os.getenv("MENU_PATH")
    MENU_FOLDER = "./"+ "uploads" + "/" + MENU_PATH
    MENU_URL = API_PREFIX + "/" + "uploads" + "/" + MENU_PATH + "/"

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

            # self.log.info("Response "+str(jsonStr))
            menu = Menu()
            menu.cd = uuid4().hex
            menu.nm = request.nm
            menu.desc = request.desc
            menu.price = request.price
            menu.price_2 = request.price_2

            menu.category_cd = request.category_cd
            menu.created_dt = datetime.datetime.now()
            menu.created_by = request.created_by
            menu.is_delete = constants.NO
            menu.is_inactive = constants.NO
            menu.discount = request.discount
            menu.is_drink = request.is_drink
            menu.stock = request.stock

            if request.file is None:
                menu.img = None
            else:
                file = request.file
                if file and self.allowed_file(file.filename):
                    filename = str(file.filename)
                    filename_data, filename_ext = os.path.splitext(filename)
                    timenow = str(datetime.datetime.now())
                    datenow = timenow[:-16]
                    timenow = timenow[11:]
                    filename = (
                        filename_data
                        + "-"
                        + datenow
                        + "-"
                        + timenow
                        + filename_ext
                    )
                    filename = secure_filename(filename)
                    # self.log.info(filename)
                    file_path = os.path.join(self.MENU_FOLDER, filename)
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    # if os.path.exists(file_path):
                    with open(file_path, "wb") as buffer:
                        # Copy the file contents into the buffer
                        copyfileobj(file.file, buffer)
                    
                    jsonStr["data"] = "Success"
                    jsonStr["isError"] = constants.NO
                    jsonStr["status"] = "Success"
                    menu.img = filename

            db.add(menu)
            db.commit()
            db.refresh(menu)

        except Exception as ex:
            # self.log.error(ex)
            response = JSONResponse(
                status_code=500,
                content={"data": str(ex), "isError": constants.YES, "status": "Failed"},
            )
            response.status_code = 500
            return response
        jsonStr["isError"] = constants.NO
        jsonStr["status"] = "Success"
        jsonStr["data"] = json.loads(json.dumps(menu, cls=ExtendEncoder))
        return jsonStr

    def updateMenu(self, request, db):
        jsonStr = {}
        try:
            # self.log.info("Response "+str(jsonStr))
            cd = request.cd
            menu = db.query(Menu).get(cd)
            menu.nm = request.nm
            menu.desc = request.desc
            menu.price = request.price
            menu.price_2 = request.price_2
            menu.category_cd = request.category_cd
            menu.updated_dt = datetime.datetime.now()
            menu.updated_by = request.updated_by
            menu.is_drink = request.is_drink
            menu.discount = request.discount
            menu.stock = request.stock

            if request.file is None:
                menu.img = None
            else:
                file = request.file
                # if user does not select file, browser also
                # submit a empty part without filename
                if file.filename == "":
                    jsonStr["data"] = "No selected file"
                    jsonStr["isError"] = constants.NO
                    jsonStr["status"] = "Success"
                if file and self.allowed_file(file.filename):
                    filename = str(file.filename)
                    filename_data, filename_ext = os.path.splitext(filename)
                    timenow = str(datetime.datetime.now())
                    datenow = timenow[:-16]
                    timenow = timenow[11:]
                    filename = (
                        filename_data
                        + "-"
                        + datenow
                        + "-"
                        + timenow
                        + filename_ext
                    )
                    filename = secure_filename(filename)
                    # self.log.info(filename)
                    file_path = os.path.join(self.MENU_FOLDER, filename)
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    with open(file_path, "wb") as buffer:
                        # Copy the file contents into the buffer
                        copyfileobj(file.file, buffer)

                    jsonStr["data"] = "Success"
                    jsonStr["isError"] = constants.NO
                    jsonStr["status"] = "Success"
                    menu.img = filename

            db.commit()
            db.refresh(menu)

        except Exception as ex:
            # self.log.error(ex)
            response = JSONResponse(
                status_code=500,
                content={"data": str(ex), "isError": constants.YES, "status": "Failed"},
            )
            response.status_code = 500
            return response
        # self.log.info("Response "+str(jsonStr))
        jsonStr["isError"] = constants.NO
        jsonStr["status"] = "Success"
        jsonStr["data"] = json.loads(json.dumps(menu, cls=ExtendEncoder))

        return jsonStr

    def deleteMenu(self, request, db):
        jsonStr = {}
        try:
            # self.log.info("Request "+str(Request.json))
            cd = request.cd
            menu = db.query(Menu).get(cd)
            menu.updated_dt = datetime.datetime.now()
            menu.updated_by = request.updated_by
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
            bill_cd = request.bill_cd
            if not bill_cd:
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
                            menu_list_data["price_2"] = mdl2.Menu.price_2
                            menu_list_data["discount"] = mdl2.Menu.discount
                            menu_list_data["stock"] = mdl2.Menu.stock
                            menu_list_data["final_price"] = 0
                            base_price = mdl2.Menu.price2 if mdl2.Menu.price2 else mdl2.Menu.price if mdl2.Menu.price else 0
                            
                            # Get price2_time setting
                            price2_time_query = db.query(AppSetting.value)\
                                .filter(AppSetting.cd == 'price2_time')\
                                .filter(AppSetting.is_inactive == constants.NO)\
                                .filter(AppSetting.is_delete == constants.NO)\
                                .first()
                                
                            current_hour = datetime.datetime.now().hour
                            
                            # If price2_time is set and current time is past that hour, use price2
                            if price2_time_query:
                                try:
                                    price2_hour = int(price2_time_query[0])
                                    if 0 <= price2_hour <= 24 and current_hour >= price2_hour:
                                        base_price = mdl2.Menu.price2 if mdl2.Menu.price2 else mdl2.Menu.price if mdl2.Menu.price else 0
                                except (ValueError, TypeError):
                                    pass  # If price2_time is not a valid number, use default price logic
                                    
                            menu_list_data["final_price"] = base_price - (mdl2.Menu.discount if mdl2.Menu.discount else 0)
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
                        menu_list_data["price_2"] = mdl2.Menu.price_2
                        menu_list_data["discount"] = mdl2.Menu.discount
                        menu_list_data["stock"] = mdl2.Menu.stock
                        menu_list_data["final_price"] = 0
                        base_price = mdl2.Menu.price2 if mdl2.Menu.price2 else mdl2.Menu.price if mdl2.Menu.price else 0
                        
                        # Get price2_time setting
                        price2_time_query = db.query(AppSetting.value)\
                            .filter(AppSetting.cd == 'price2_time')\
                            .filter(AppSetting.is_inactive == constants.NO)\
                            .filter(AppSetting.is_delete == constants.NO)\
                            .first()
                            
                        current_hour = datetime.datetime.now().hour
                        
                        # If price2_time is set and current time is past that hour, use price2
                        if price2_time_query:
                            try:
                                price2_hour = int(price2_time_query[0])
                                if 0 <= price2_hour <= 24 and current_hour >= price2_hour:
                                    base_price = mdl2.Menu.price2 if mdl2.Menu.price2 else mdl2.Menu.price if mdl2.Menu.price else 0
                            except (ValueError, TypeError):
                                pass  # If price2_time is not a valid number, use default price logic
                                
                        menu_list_data["final_price"] = base_price - (mdl2.Menu.discount if mdl2.Menu.discount else 0)
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
            # self.log.info(data)
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
            data_list["price_2"] = data.Menu.price_2
            data_list["discount"] = data.Menu.discount
            data_list["stock"] = data.Menu.stock
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
            # self.log.error(ex)
            response = JSONResponse(
                status_code=500,
                content={
                    "data": str(ex),
                    "isError": constants.YES,
                    "status": constants.STATUS_FAILED,
                },
            )
            return response
        # self.log.info("Response "+str(jsonStr))
        return jsonStr
