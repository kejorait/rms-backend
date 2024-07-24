import json
import os
import datetime
from fastapi.responses import JSONResponse
from rich.console import Console
from models.stock import Stock
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


class StockService:

    name = "Stock"
    setupLog(serviceName=__file__)

    ALLOWED_EXTENSIONS = set(["png", "jpg", "jpeg"])
    MENU_PATH = os.getenv("MENU_PATH")
    MENU_FOLDER = "./" + MENU_PATH
    MENU_URL = os.getenv("HOST") + "/" + MENU_PATH + "/"

    def __init__(self):
        self.log = getLogger(serviceName=__file__)
        # self.log.info(" init  StockService ")

    def allowed_file(self, filename):
        return (
            "." in filename
            and filename.rsplit(".", 1)[1].lower() in self.ALLOWED_EXTENSIONS
        )

    def addStock(self, request, db):
        jsonStr = {}
        try:
            # self.log.info("Response "+str(jsonStr))
            stock = Stock()
            stock.cd = uuid4().hex
            stock.nm = request.nm
            stock.amount = request.amount
            stock.desc = request.desc
            stock.price = request.price
            stock.created_dt = datetime.datetime.now()
            stock.created_by = request.created_by
            stock.is_delete = constants.NO
            stock.is_inactive = constants.NO

            db.add(stock)
            db.commit()

        except Exception as ex:
            self.log.error(ex)
            response = JSONResponse(
                status_code=500,
                content={"data": str(ex), "isError": constants.YES, "status": "Failed"},
            )
            response.status_code = 500
            return response
        return jsonStr

    def updateStock(self, request, db):
        jsonStr = {}
        try:
            reqdata = Request.form
            # self.log.info("Response "+str(jsonStr))
            cd = reqdata["cd"]
            stock = db.query(Stock).get(cd)
            stock.nm = reqdata["nm"]
            stock.desc = reqdata["desc"]
            stock.price = reqdata["price"]
            stock.category_cd = reqdata["category_cd"]
            stock.updated_dt = datetime.datetime.now()
            stock.updated_by = reqdata["updated_by"]

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
                    stock.img = filename

            db.commit()

        except Exception as ex:
            self.log.error(ex)
            response = JSONResponse(
                status_code=500,
                content={"data": str(ex), "isError": constants.YES, "status": "Failed"},
            )
            response.status_code = 500
            return response
        # self.log.info("Response "+str(jsonStr))
        return jsonStr

    def deleteStock(self, request, db):
        jsonStr = {}
        try:
            # self.log.info("Request "+str(Request.json))
            cd = Request.json["cd"]
            stock = db.query(Stock).get(cd)
            stock.updated_dt = datetime.datetime.now()
            stock.updated_by = Request.json["updated_by"]
            stock.is_delete = constants.YES

            db.commit()

            jsonStr["isError"] = constants.NO
            jsonStr["status"] = "Success"
        except Exception as ex:
            self.log.exception(" StockService")
            jsonStr["isError"] = constants.YES
            jsonStr["status"] = "Failed"
            return jsonStr, 500
        # self.log.info("Response "+str(jsonStr))
        return jsonStr

    def getStock(self, request, db):
        jsonStr = {}
        try:
            # self.log.info("Request "+str(Request.json))
            if "bill_cd" in Request.json:
                bill_cd = Request.json["bill_cd"]
            else:
                # self.log.exception(" StockService")
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
                    Stock,
                    Category.nm.label("category_nm"),
                )
                query = query.join(Category, Category.cd == Stock.category_cd)
                query = query.filter(Stock.is_delete == constants.NO)
                query = query.filter(Stock.is_inactive == constants.NO)
                query = query.order_by(Stock.created_dt.asc())
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
                    stock_list = []
                    for mdl2 in data:
                        # self.log.info(mdl2.nm)
                        if mdl == mdl2.category_nm:
                            stock_list_data = {}
                            stock_list_data["cd"] = mdl2.cd
                            stock_list_data["nm"] = mdl2.nm
                            if mdl2.img:
                                stock_list_data["img"] = self.MENU_URL + mdl2.img
                            else:
                                stock_list_data["img"] = ""
                            stock_list_data["desc"] = mdl2.desc
                            stock_list_data["price"] = mdl2.price
                            stock_list_data["category_cd"] = mdl2.category_cd
                            stock_list_data["created_dt"] = mdl2.created_dt
                            stock_list_data["created_by"] = mdl2.created_by
                            stock_list_data["is_inactive"] = mdl2.is_inactive
                            stock_list_data["is_delete"] = mdl2.is_delete
                            stock_list_data["updated_dt"] = mdl2.updated_dt
                            stock_list_data["updated_by"] = mdl2.updated_by

                            stock_list.append(stock_list_data)

                    stock_list.sort(key=lambda x: x["nm"], reverse=False)

                    data_list["stock"] = stock_list
                    listData.append(data_list)
                # self.log.info(stock_list)
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
            self.log.exception(" StockService")
            jsonStr["isError"] = constants.YES
            jsonStr["status"] = "Failed"
            return jsonStr, 500
        # self.log.info("Response "+str(jsonStr))
        return jsonStr

    def getStockAll(self, request, db, sort_by, sort_order):
        jsonStr = {}
        try:
            # self.log.info("Request "+str(Request.json))

            query = db.query(Stock)
            query = query.filter(Stock.is_delete == constants.NO)
            search = request.search
            if search:
                query = query.filter(Stock.nm.ilike("%{}%".format(search)))
            query = query.filter(Stock.is_inactive == constants.NO)
            if sort_by:
                column = getattr(Stock, sort_by, None)
                if column:
                    if sort_order == "desc":
                        query = query.order_by(column.desc())
                    else:
                        query = query.order_by(column.asc())
            else:
                query = query.order_by(Stock.created_dt.desc())
            data = query.all()
            self.log.info(query.statement.compile(compile_kwargs={"literal_binds": True}))
            db.close()
            res = {}

            listData = []
            for mdl in data:
                data_list = {}
                data_list["cd"] = mdl.cd
                data_list["nm"] = mdl.nm
                data_list["amount"] = mdl.amount
                data_list["desc"] = mdl.desc
                data_list["price"] = mdl.price
                data_list["created_dt"] = mdl.created_dt
                data_list["created_by"] = mdl.created_by
                data_list["is_inactive"] = mdl.is_inactive
                data_list["is_delete"] = mdl.is_delete
                data_list["updated_dt"] = mdl.updated_dt
                data_list["updated_by"] = mdl.updated_by

                listData.append(data_list)

            res["data"] = listData
            res["status"] = constants.STATUS_SUCCESS
            res["isError"] = constants.NO
            jsonStr = res
        except Exception as ex:
            self.log.error(ex)
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
        return listData

    def getStockByCode(self, request, db):
        jsonStr = {}
        try:
            # self.log.info("Request "+str(Request.json))

            cd = request.cd
            query = db.query(
                Stock,
                Category.cd.label("category_cd"),
                Category.nm.label("category_nm"),
            )
            query = query.join(Category, Category.cd == Stock.category_cd)
            query = query.filter(Stock.is_delete == constants.NO)
            query = query.filter(Stock.is_inactive == constants.NO)
            query = query.filter(Stock.cd == cd)
            data = query.first()
            # self.log.info(query.statement.compile(compile_kwargs={"literal_binds": True}))
            self.log.info(data)
            db.close()
            res = {}
            data_list = {}
            data_list["cd"] = data.cd
            data_list["nm"] = data.nm
            if data.img:
                data_list["img"] = self.MENU_URL + data.img
            else:
                data_list["img"] = ""
            data_list["desc"] = data.desc
            data_list["price"] = data.price
            data_list["category_cd"] = data.category_cd
            data_list["created_dt"] = data.created_dt
            data_list["created_by"] = data.created_by
            data_list["is_inactive"] = data.is_inactive
            data_list["is_delete"] = data.is_delete
            data_list["updated_dt"] = data.updated_dt
            data_list["updated_by"] = data.updated_by
            data_list["category_cd"] = data.category_cd
            data_list["category_nm"] = data.category_nm
            data_list["is_drink"] = data.is_drink

            # self.log.info(stock_list)
            res["data"] = data_list
            res["status"] = "Success"
            res["isError"] = constants.NO
            jsonStr = res
        except Exception as ex:
            self.log.error(ex)
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
