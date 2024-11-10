import datetime as dt
import json
import os
from shutil import copyfileobj
from uuid import uuid4

from fastapi.responses import JSONResponse
from sqlalchemy import func
from werkzeug.utils import secure_filename

from helper import constants
from helper.jsonHelper import ExtendEncoder
from models.category import Category
from utils.tinylog import getLogger, setupLog


class CategoryService:

    name = "Category"
    setupLog(serviceName=__file__)

    ALLOWED_EXTENSIONS = set(["png", "jpg", "jpeg"])
    API_PREFIX = os.getenv("API_PREFIX")
    CATEGORY_PATH = os.getenv("CATEGORY_PATH")
    CATEGORY_FOLDER = "./" + "uploads" + "/" + CATEGORY_PATH
    CATEGORY_URL = API_PREFIX + "/" + "uploads" + "/" + CATEGORY_PATH + "/"

    def __init__(self):
        self.log = getLogger(serviceName=__file__)
        # self.log.info(" init  RoleService ")
        # request.json = request.json

    def allowed_file(self, filename):
        return (
            "." in filename
            and filename.rsplit(".", 1)[1].lower() in self.ALLOWED_EXTENSIONS
        )

    def addCategory(self, request, db):
        jsonStr = {}
        try:
            # self.log.info("Response "+str(jsonStr))
            reqdata = request

            category_cd = uuid4().hex
            category = Category()

            category.cd = category_cd
            category.nm = reqdata.nm
            category.created_dt = dt.datetime.now()
            category.created_by = reqdata.created_by
            category.is_delete = constants.NO
            category.is_inactive = constants.NO

            if reqdata.file is None:
                jsonStr["data"] = "No file"
                jsonStr["isError"] = constants.NO
                jsonStr["status"] = constants.STATUS_SUCCESS
            else:
                file = reqdata.file
                # if user does not select file, browser also
                # submit a empty part without filename
                if file.filename == "":
                    jsonStr["data"] = "No selected file"
                    jsonStr["isError"] = constants.NO
                    jsonStr["status"] = constants.STATUS_SUCCESS
                if file and self.allowed_file(file.filename):
                    filename = str(file.filename)
                    filename_data, filename_ext = os.path.splitext(filename)
                    timenow = str(dt.datetime.now())
                    datenow = timenow[:-16]
                    timenow = timenow[11:]
                    filename = (
                        filename_data + "-" + datenow + "-" + timenow + filename_ext
                    )
                    filename = secure_filename(filename)
                    # self.log.info(filename)
                    file_path = os.path.join(self.CATEGORY_FOLDER, filename)
                    with open(file_path, "wb") as buffer:
                        # Copy the file contents into the buffer
                        copyfileobj(file.file, buffer)
                    jsonStr["data"] = reqdata
                    jsonStr["isError"] = constants.NO
                    jsonStr["status"] = constants.STATUS_SUCCESS
                    category.img = filename

            db.add(category)
            db.commit()

        except Exception as ex:
            # self.log.exception(" UserService")
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

        return jsonStr

    def updateCategory(self, request, db):
        jsonStr = {}

        try:
            # self.log.info("Response "+str(jsonStr))
            reqdata = request

            cd = reqdata.cd

            category = db.query(Category).get(cd)
            category.nm = reqdata.nm
            category.updated_dt = dt.datetime.now()
            category.updated_by = reqdata.updated_by

            if reqdata.file is None:
                jsonStr["data"] = "No file"
                jsonStr["isError"] = constants.NO
                jsonStr["status"] = constants.STATUS_SUCCESS
            else:
                file = reqdata.file
                # if user does not select file, browser also
                # submit a empty part without filename
                if file.filename == "":
                    jsonStr["data"] = "No selected file"
                    jsonStr["isError"] = constants.NO
                    jsonStr["status"] = constants.STATUS_SUCCESS
                if file and self.allowed_file(file.filename):
                    filename = str(file.filename)
                    filename_data, filename_ext = os.path.splitext(filename)
                    timenow = str(dt.datetime.now())
                    datenow = timenow[:-16]
                    timenow = timenow[11:]
                    filename = (
                        filename_data + "-" + datenow + "-" + timenow + filename_ext
                    )
                    filename = secure_filename(filename)
                    # self.log.info(filename)
                    file_path = os.path.join(self.CATEGORY_FOLDER, filename)
                    with open(file_path, "wb") as buffer:
                        # Copy the file contents into the buffer
                        copyfileobj(file.file, buffer)
                    jsonStr["data"] = reqdata
                    jsonStr["isError"] = constants.NO
                    jsonStr["status"] = constants.STATUS_SUCCESS
                    category.img = filename

            db.commit()

        except Exception as ex:
            # self.log.exception(" UserService")
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

        return jsonStr

    def deleteCategory(self, request, db):
        jsonStr = {}

        try:
            # self.log.info("Response "+str(jsonStr))

            cd = request.cd

            category = db.query(Category).get(cd)
            category.deleted_dt = dt.datetime.now()

            category.is_delete = constants.YES
            category.is_inactive = constants.YES
            category.deleted_by = request.deleted_by

            category_obj = category
            db.commit()

            jsonStr["data"] = json.loads(json.dumps(category_obj, cls=ExtendEncoder))
            jsonStr["isError"] = constants.NO
            jsonStr["status"] = "Success"

        except Exception as ex:
            self.log.exception(" UserService")
            jsonStr["isError"] = constants.YES
            jsonStr["status"] = "Failed"
        # self.log.info("Response "+str(jsonStr))

        return jsonStr

    def getAllCategory(self, request, db):
        jsonStr = {}
        try:
            # self.log.info("Response "+str(jsonStr))

            query = db.query(func.distinct(Category.cd), Category)
            query = query.filter(Category.is_delete == constants.NO)
            query = query.filter(Category.is_inactive == constants.NO)
            if request.search:
                query = query.filter(Category.nm.ilike ("%{}%".format(request.search)))
            query = query.order_by(Category.nm.asc())
            row = query.all()
            # cd = row.cd
            db.close()

            res = {}

            listData = []
            for mdl in row:
                data_list = {}
                data_list["cd"] = mdl.Category.cd
                data_list["nm"] = mdl.Category.nm
                if mdl.Category.img:
                    data_list["img"] = self.CATEGORY_URL + mdl.Category.img if mdl.Category.img else ""
                else:
                    data_list["img"] = ""
                data_list["created_dt"] = mdl.Category.created_dt
                data_list["created_by"] = mdl.Category.created_by
                data_list["updated_dt"] = mdl.Category.created_dt
                data_list["updated_by"] = mdl.Category.created_by
                listData.append(data_list)

            res["data"] = listData
            res["status"] = "Success"
            res["isError"] = constants.NO
            jsonStr = res
            # self.log.info("Response " + str(jsonStr))
        except Exception as ex:
            self.log.exception(" RoleService")
            jsonStr["isError"] = constants.YES
            jsonStr["status"] = "Failed"
        return jsonStr

    def getCategoryByCd(self, request, db):
        jsonStr = {}
        # try:
            # Log initial processing
            # self.log.info("Processing request for category with cd: %s", request.cd)

            # Query the database for categories matching the conditions
        query = db.query(Category).filter(
            Category.is_delete == constants.NO,
            Category.is_inactive == constants.NO,
            Category.cd == request.cd,
        )
        rows = query.first()

        listData = {}
        listData.update(json.loads(json.dumps(rows, cls=ExtendEncoder)))
        listData["img"] = self.CATEGORY_URL + listData["img"] if listData["img"] else ""

        # Construct response
        res = {"data": listData, "status": "Success", "isError": constants.NO}
        jsonStr = res
        # self.log.info("Response: %s", jsonStr)
        return jsonStr

        # except Exception as ex:
        #     # Log the exception details
        #     self.log.exception("An error occurred in getCategoryByCd")

        #     # Handle the exception response
        #     jsonStr = {"isError": constants.YES, "status": "Failed"}
        return jsonStr
