import datetime as dt
import os
from datetime import datetime
from itertools import groupby
from shutil import copyfileobj
from uuid import uuid4

import bcrypt
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

from helper import constants
from models.role import Role
from models.user import User
from models.user_credential import UserCredential
from utils.tinylog import getLogger, setupLog


class UserService:
    name = "user"
    setupLog(serviceName=__file__)
    load_dotenv()

    ALLOWED_EXTENSIONS = set(["png", "jpg", "jpeg"])
    API_PREFIX = os.getenv("API_PREFIX")
    USER_PATH = os.getenv("USER_PATH")
    USER_FOLDER = "./" + "uploads" + "/" + USER_PATH
    USER_URL = API_PREFIX + "/" + "uploads" + "/" + USER_PATH + "/"

    def __init__(self):
        self.log = getLogger(serviceName=__file__)
        # self.log.info(" init  UserService ")

    def allowed_file(self, filename):
        return (
            "." in filename
            and filename.rsplit(".", 1)[1].lower() in self.ALLOWED_EXTENSIONS
        )

    # Get All User by Role
    def getUserByRole(self, request, db):
        jsonStr = {}
        try:
            # self.log.info("Request " + str(Request.json))
            # print(vars(request.json))
            role = request.role

            query = db.query(User, Role)
            query = query.join(Role, User.role_cd == Role.cd)
            query = query.group_by(User.cd)
            query = query.group_by(Role.cd)
            query = query.filter(Role.cd == role)
            query = query.filter(User.is_delete == constants.NO)
            query = query.filter(User.is_inactive == constants.NO)
            query = query.filter(User.is_resign == constants.NO)
            data = query.all()

            db.close()

            res = {}

            listData = []
            for mdl in data:
                data_list = {}
                data_list["cd"] = mdl.User.cd
                data_list["name"] = mdl.User.name
                data_list["username"] = mdl.User.username
                if mdl.User.created_dt:
                    data_list["created_dt"] = datetime.timestamp(mdl.User.created_dt)
                else:
                    data_list["created_dt"] = ""
                data_list["created_by"] = mdl.User.created_by
                data_list["is_inactive"] = mdl.User.is_inactive
                data_list["is_delete"] = mdl.User.is_delete
                if mdl.User.img:
                    data_list["img"] = str(self.USER_URL) + str(mdl.User.img)
                else:
                    data_list["img"] = ""
                listData.append(data_list)

            res["data"] = listData
            res["status"] = "Success"
            res["isError"] = constants.NO
            jsonStr = res
            # self.log.info("Response " + str(jsonStr))
        except Exception as ex:
            self.log.exception(" UserService")
            jsonStr["isError"] = constants.YES
            jsonStr["status"] = "Failed"
        return jsonStr

    # Get All User by Role
    def getAllUser(self, request, db):
        jsonStr = {}
        try:
            # self.log.info("Request " + str(Request.json))

            query = db.query(User.cd, User, Role.nm.label("role_nm"))
            search = request.search
            if search:
                query = query.filter(User.name.ilike("%{}%".format(search)))
            query = query.join(Role, Role.cd == User.role_cd)
            query = query.filter(User.role_cd != "supervisor")
            query = query.filter(User.role_cd != "owner")
            query = query.filter(User.is_delete == constants.NO)
            query = query.filter(User.is_inactive == constants.NO)
            query = query.filter(User.is_resign == constants.NO)
            data = query.all()
            db.close()
            res = {}

            db.close()

            res = {}

            listData = []
            for mdl in data:
                data_list = {}
                data_list["cd"] = mdl.User.cd
                data_list["name"] = mdl.User.name
                data_list["username"] = mdl.User.username
                data_list["role"] = mdl.User.role_cd
                data_list["role_nm"] = mdl.role_nm
                data_list["created_dt"] = mdl.User.created_dt
                data_list["created_by"] = mdl.User.created_by
                data_list["is_inactive"] = mdl.User.is_inactive
                data_list["is_delete"] = mdl.User.is_delete
                if mdl.User.img:
                    data_list["img"] = self.USER_URL + mdl.User.img
                else:
                    data_list["img"] = ""
                listData.append(data_list)
            # self.log.info(listData)
            INFO = sorted(listData, key=lambda x: x["role_nm"])
            # self.log.info(INFO)
            listUser = []
            for key, value in groupby(INFO, lambda x: x["role_nm"]):
                roles = {}
                roles["role_nm"] = key
                roles["user"] = list(value)
                listUser.append(roles)

            res["data"] = listUser
            res["status"] = "Success"
            res["isError"] = constants.NO
            jsonStr = res
            # self.log.info("Response " + str(jsonStr))
        except Exception as ex:
            self.log.exception(" UserService")
            jsonStr["isError"] = constants.YES
            jsonStr["status"] = "Failed"
        return jsonStr

    # Get User By Id
    def getUser(self, request, db):
        jsonStr = {}
        try:
            # self.log.info("Request "+str(Request.json))
            user_cd = request.user_cd

            query = db.query(Role, User)

            query = query.join(Role, Role.cd == User.role_cd)
            query = query.filter(User.cd == user_cd)
            mdl = query.first()
            # self.log.info(data)
            db.close()

            res = {}
            data_list = {}
            data_list["cd"] = mdl.User.cd
            data_list["username"] = mdl.User.username
            data_list["name"] = mdl.User.name
            data_list["role_cd"] = mdl.User.role_cd
            data_list["role_nm"] = mdl.Role.nm
            data_list["created_dt"] = datetime.timestamp(mdl.User.created_dt)
            data_list["created_by"] = mdl.User.created_by
            data_list["is_inactive"] = mdl.User.is_inactive
            data_list["is_delete"] = mdl.User.is_delete
            if mdl.User.img:
                data_list["img"] = self.USER_URL + mdl.User.img
            else:
                data_list["img"] = ""
            res["data"] = data_list
            res["status"] = "Success"
            res["isError"] = constants.NO
            # jsonStr = json.dumps(res, default=str)
            jsonStr = res
            # self.log.info("Response "+str(jsonStr))
        except Exception as ex:
            self.log.exception(" UserService")
            jsonStr["isError"] = constants.YES
            jsonStr["status"] = "Failed"
        return jsonStr

    # Create User
    def addUser(self, request, db):
        jsonStr = {}

        try:
            # self.log.info("Response "+str(jsonStr))
            query = db.query(User.username)
            query = query.filter(User.username == request.username)
            query = query.filter(User.is_delete == constants.NO)
            query = query.filter(User.is_inactive == constants.NO)
            row = query.first()
            if row:
                self.log.exception(" UserService")
                jsonStr["data"] = "username is used"
                jsonStr["isError"] = constants.YES
                jsonStr["status"] = "Failed"
                return jsonStr, 500
            else:

                user_cd = uuid4().hex
                user = User()

                user.cd = user_cd
                user.name = request.name
                user.username = request.username
                user.role_cd = request.role_cd
                user.created_dt = dt.datetime.now()
                user.created_by = request.created_by
                user.is_delete = constants.NO
                user.is_inactive = constants.NO
                user.is_resign = constants.NO
                if request.file is None:
                    user.img = None
                else:
                    file = request.file
                    if file and self.allowed_file(file.filename):
                        # self.log.info(file.filename)
                        filename = str(file.filename)
                        filename_data = filename[:-4]
                        filename_ext = filename[-4:]
                        timenow = str(dt.datetime.now())
                        datenow = timenow[:-16]
                        timenow = timenow[11:]
                        filename = (
                            filename_data + "-" + datenow + "-" + timenow + filename_ext
                        )
                        filename = secure_filename(filename)
                        # self.log.info(filename)
                        file_path = os.path.join(self.USER_FOLDER, filename)
                        with open(file_path, "wb") as buffer:
                            # Copy the file contents into the buffer
                            copyfileobj(file.file, buffer)
                        jsonStr["data"] = "Success"
                        jsonStr["isError"] = constants.NO
                        jsonStr["status"] = "Success"
                        user.img = filename
                db.add(user)
                db.commit()
                userCredential = UserCredential()
                userCredential.cd = uuid4().hex

                userCredential.user_cd = user_cd
                password = request.password.encode("utf8")
                self.log.info(password)
                userCredential.password = bcrypt.hashpw(
                    password, bcrypt.gensalt()
                ).decode("utf8")
                # self.log.info(userCredential.password)
                userCredential.created_dt = dt.datetime.now()
                userCredential.is_delete = constants.NO

                db.add(userCredential)
                db.commit()
                jsonStr["data"] = constants.STATUS_SUCCESS
                jsonStr["isError"] = constants.NO
                jsonStr["status"] = "Success"

        except Exception as ex:
            self.log.exception(" UserService")
            jsonStr["isError"] = constants.YES
            jsonStr["status"] = "Failed"
        # self.log.info("Response "+str(jsonStr))

        return jsonStr

    # Update User
    def updateUser(self, request, db):
        jsonStr = {}
        try:
            # self.log.info(reqdata)
            # self.log.info("Response "+str(jsonStr))
            user_cd = request.cd
            user = db.query(User).get(user_cd)
            user.name = request.name
            user.username = request.username
            user.role_cd = request.role_cd
            user.updated_dt = dt.datetime.now()
            user.updated_by = request.updated_by
            if request.file is None:
                user.img = None
            else:
                file = request.file
                if file and self.allowed_file(file.filename):
                    filename = str(file.filename)
                    filename_data = filename[:-4]
                    filename_ext = filename[-4:]
                    timenow = str(dt.datetime.now())
                    datenow = timenow[:-16]
                    timenow = timenow[11:]
                    filename = (
                        filename_data + "-" + datenow + "-" + timenow + filename_ext
                    )
                    filename = secure_filename(filename)
                    self.log.info(filename)
                    file_path = os.path.join(self.USER_FOLDER, filename)
                    with open(file_path, "wb") as buffer:
                        # Copy the file contents into the buffer
                        copyfileobj(file.file, buffer)
                    jsonStr["data"] = request
                    jsonStr["isError"] = constants.NO
                    jsonStr["status"] = constants.STATUS_SUCCESS
                    user.img = filename
            db.commit()

            query = db.query(UserCredential)
            query = query.filter(UserCredential.user_cd == user_cd)
            query = query.filter(UserCredential.is_delete == constants.NO)
            data = query.first()
            usercredcd = data.cd
            userCredential = db.query(UserCredential).get(usercredcd)
            password = request.password.encode("utf8")
            self.log.info(password)
            userCredential.password = bcrypt.hashpw(password, bcrypt.gensalt()).decode(
                "utf8"
            )
            # self.log.info(userCredential.password)
            userCredential.updated_dt = dt.datetime.now()
            self.log.info(userCredential)
            db.commit()

            jsonStr["data"] = constants.STATUS_SUCCESS
            jsonStr["isError"] = constants.NO
            jsonStr["status"] = "Success"

        except Exception as ex:
            self.log.exception(" MenuService")
            jsonStr["isError"] = constants.YES
            jsonStr["status"] = "Failed"
        # self.log.info("Response "+str(jsonStr))
        return jsonStr

    # Delete User
    def deleteUser(self, request, db):
        jsonStr = {}
        try:
            # self.log.info("Request "+str(Request.json))
            cd = request.cd
            user = db.query(User).get(cd)
            user.is_delete = "Y"

            db.commit()

            jsonStr["data"] = constants.STATUS_SUCCESS_DELETE
            jsonStr["isError"] = constants.NO
            jsonStr["status"] = "Success"

        except Exception as ex:
            self.log.exception(" MenuService")
            jsonStr["isError"] = constants.YES
            jsonStr["status"] = "Failed"
        # self.log.info("Response "+str(jsonStr))
        return jsonStr
