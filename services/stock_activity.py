import os
import datetime
from fastapi.responses import JSONResponse
from models.stock import Stock
from helper.jsonHelper import ExtendEncoder
from helper import constants
from utils.tinylog import getLogger, setupLog
from uuid import uuid4
from dotenv import load_dotenv

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
            stock_obj = ExtendEncoder().to_dict(stock)

            db.add(stock)
            db.commit()

            jsonStr["data"] = stock_obj
            jsonStr["isError"] = constants.NO
            jsonStr["status"] = constants.STATUS_SUCCESS

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
            # self.log.info("Response "+str(jsonStr))
            cd = request.cd
            stock = db.query(Stock).get(cd)
            stock.nm = request.nm
            stock.amount = request.amount
            stock.desc = request.desc
            stock.price = request.price
            stock.updated_dt = datetime.datetime.now()
            stock.updated_by = request.updated_by
            stock_obj = ExtendEncoder().to_dict(stock)
            db.commit()

            jsonStr["data"] = stock_obj
            jsonStr["isError"] = constants.NO
            jsonStr["status"] = constants.STATUS_SUCCESS

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
            cd = request.cd
            stock = db.query(Stock).get(cd)
            stock.updated_dt = datetime.datetime.now()
            stock.updated_by = request.updated_by
            stock.is_delete = constants.YES
            stock_obj = ExtendEncoder().to_dict(stock)

            db.commit()

            jsonStr["data"] = stock_obj
            jsonStr["isError"] = constants.NO
            jsonStr["status"] = "Success"
        except Exception as ex:
            jsonStr = JSONResponse(
                status_code=500,
                content={
                    "data": str(ex),
                    "isError": constants.YES,
                    "status": constants.STATUS_FAILED,
                },
            )
        # self.log.info("Response "+str(jsonStr))
        return jsonStr

    def deleteStockBulk(self, request, db):
        jsonStr = {"data": [], "isError": constants.NO, "status": "Success"}
        try:
            # Check if cd is a list
            cds = request.cd if isinstance(request.cd, list) else [request.cd]
            
            for cd in cds:
                stock = db.query(Stock).get(cd)
                if stock:
                    stock.updated_dt = datetime.datetime.now()
                    stock.updated_by = request.updated_by
                    stock.is_delete = constants.YES
                    stock_obj = ExtendEncoder().to_dict(stock)
                    jsonStr["data"].append(stock_obj)
                else:
                    jsonStr["data"].append({"cd": cd, "status": "Not Found"})
            
            db.commit()
        except Exception as ex:
            jsonStr = JSONResponse(
                status_code=500,
                content={
                    "data": str(ex),
                    "isError": constants.YES,
                    "status": constants.STATUS_FAILED,
                },
            )
        # self.log.info("Response "+str(jsonStr))
        return jsonStr
    
    def getStockAll(self, request, db):
        # self.log.info("Request "+str(Request.json))

        search = request.search
        sort_by = request.sort_by
        sort_order = request.sort_order
        
        query = db.query(Stock)
        query = query.filter(Stock.is_delete == constants.NO)
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
        # self.log.info(query.statement.compile(compile_kwargs={"literal_binds": True}))
        db.close()

        listData = []
        row_no = 1
        for mdl in data:
            data_list = {}
            data_list["row_no"] = row_no
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
            row_no = row_no + 1

            listData.append(data_list)

            jsonStr = {}
            jsonStr["data"] = listData
            jsonStr["isError"] = constants.NO
            jsonStr["status"] = constants.STATUS_SUCCESS

        return jsonStr

    def getStockByCode(self, request, db):
        jsonStr = {}
        try:
            # self.log.info("Request "+str(request))

            cd = request.cd
            query = db.query(Stock)
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
            data_list["amount"] = data.amount
            data_list["desc"] = data.desc
            data_list["price"] = data.price
            data_list["created_dt"] = data.created_dt
            data_list["created_by"] = data.created_by
            data_list["is_inactive"] = data.is_inactive
            data_list["is_delete"] = data.is_delete
            data_list["updated_dt"] = data.updated_dt
            data_list["updated_by"] = data.updated_by

            # self.log.info(stock_list)
            res["data"] = data_list
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
        return jsonStr
