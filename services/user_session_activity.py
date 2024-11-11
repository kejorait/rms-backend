import datetime as dt
from helper import constants
from utils.tinylog import getLogger, setupLog
from uuid import uuid4
from fastapi.requests import Request

class UserSessionService:
    name = "UserSession"
    setupLog(serviceName=__file__)
    
    def __init__(self):
        self.log = getLogger(serviceName=__file__)
        # self.log.info(" init  UserSessionService ")
        self.content = Request.json

    def logging(self, msg):
        self.log.info(msg)

    # Create Session
    def addSession(self, request, db):
        jsonStr = {}
        try:
            # self.log.info("Response "+str(jsonStr))
            UserSession = UserSession()
            UserSession.cd = uuid4().hex
            UserSession.employee_cd = request.employee_cd
            UserSession.created_dt = dt.datetime.now()
            UserSession.is_delete = constants.NO

            db.session.add(UserSession)
            db.session.commit()
            
            jsonStr["data"] = constants.STATUS_SUCCESS
            jsonStr["isError"] = constants.NO
            jsonStr["status"] = "Success"

        except Exception as ex:
            self.log.exception(" UserSessionService")
            jsonStr["isError"] = constants.YES
            jsonStr["status"] = "Failed"
        # self.log.info("Response " + str(jsonStr))

        return jsonStr
    
    # Delete Session
    def deleteSession(self, request, db):
        jsonStr = {}
        try:
            # self.log.info("Response "+str(jsonStr))
            cd = request.cd
            UserSession = db.session.query(UserSession).get(cd)
            UserSession.is_delete = "Y"

            db.session.commit()

            jsonStr["data"] = constants.STATUS_SUCCESS
            jsonStr["isError"] = constants.NO
            jsonStr["status"] = "Success"

        except Exception as ex:
            self.log.exception(" UserSessionService")
            jsonStr["isError"] = constants.YES
            jsonStr["status"] = "Failed"
        # self.log.info("Response " + str(jsonStr))
        return jsonStr

    