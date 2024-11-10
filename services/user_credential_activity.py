import datetime as dt
import json
import os
from datetime import datetime
from uuid import uuid4

import bcrypt
import jwt
from fastapi import HTTPException
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from helper import constants
from helper.helper import (create_access_token, create_refresh_token,
                           datetimeToLongJS, response_cookies)
from helper.jsonHelper import ExtendEncoder
from models.user import User
from models.user_credential import UserCredential
from models.user_session import UserSession
from utils.tinylog import getLogger, setupLog


class UserCredentialService:
    name = "user_credential"
    setupLog(serviceName=__file__)
    
    def __init__(self):
        self.log = getLogger(serviceName=__file__)
        ## self.log.info(" init  UserCredentialService ")
        self.content = Request.json
        self.env = os.getenv("ENV")
    def toDict(self, yoi):
        m = {}
        for key, val in yoi.__dict__.items():
            if (isinstance(val, datetime)):
                m[key] = datetimeToLongJS(val)
            else:
                m[key] = val
        return m
    
    # Check User Credential
    def login(self, request, db, SECRET_KEY):
        jsonStr = {}
        try:
            username = request.username
            password = request.password.encode()

            query = db.query(User, UserCredential)
            query = query.join(User, User.cd == UserCredential.user_cd)
            query = query.filter(User.username == username)
            
            data = query.first()

            db.close()
            if data is not None:
                pwhash = bcrypt.hashpw(password, data[1].password.encode('utf8')).decode('utf8')
                if data[1].password == pwhash:
                    query = db.query(UserSession)
                    query = query.filter(UserSession.user_cd == data[0].cd)
                    query = query.filter(UserSession.is_delete == constants.NO)
                    data_session = query.first()
                    db.close()
                    if data_session:
                        update_session = db.query(UserSession).get(data_session.cd)
                        update_session.updated_dt = dt.datetime.now()
                        update_session.is_delete = constants.YES
                        db.commit()
                    
                    user = json.loads(json.dumps(data[0], cls=ExtendEncoder))

                    access_token_expires = dt.timedelta(minutes=constants.ACCESS_TOKEN_EXPIRE_MINUTES)
                    access_token = create_access_token(
                        data=user, secret_key=SECRET_KEY, expires_delta=access_token_expires
                    )

                    refresh_token_expires = dt.timedelta(days=constants.REFRESH_TOKEN_EXPIRE_DAYS)
                    refresh_token = create_refresh_token(
                        data=user, secret_key=SECRET_KEY, expires_delta=refresh_token_expires
                    )

                    jsonStr["data"] = constants.STATUS_SUCCESS
                    jsonStr["isError"] = constants.NO
                    jsonStr["status"] = "Success"
                    jsonStr["access_token"] = access_token
                    jsonStr["refresh_token"] = refresh_token

                    usersession = UserSession()
                    usersession.cd = uuid4().hex
                    usersession.user_cd = data[0].cd
                    usersession.created_dt = dt.datetime.now()
                    usersession.is_delete = constants.NO

                    db.add(usersession)
                    db.commit()
                else:
                    raise Exception("Wrong Password")
            else:
                raise Exception("User Not Found")

        except Exception as ex:
            self.log.error(ex)
            response = JSONResponse(status_code=500, content={"data": str(ex), "isError": constants.YES, "status": constants.STATUS_FAILED})
            return response
        
        response = JSONResponse(content=jsonStr)
        return response
    
    def checkCredential(self, request, db, SECRET_KEY):
        jsonStr = {}
        try:
            ## self.log.info("Response "+str(jsonStr))
            username = request.username
            password = request.password.encode()

            query = db.query(User,
                                     UserCredential)
            query = query.join(User,
                               User.cd == UserCredential.user_cd)
            query = query.filter(User.username == username)
            
            data = query.first()

            db.close()
            if data is not None:
                pwhash = bcrypt.hashpw(password, data[1].password.encode('utf8')).decode('utf8')
                # #self.log.info(data.password)
                # #self.log.info(pwhash)
                # #self.log.info(data[0])
                if data[1].password == pwhash:
                    query = db.query(
                    UserSession
                )
                    query = query.filter(UserSession.user_cd == data[0].cd)
                    query = query.filter(UserSession.is_delete == constants.NO)
                    data_session = query.first()
                    db.close()
                    if data_session:
                        update_session = db.query(UserSession).get(data_session.cd)
                        update_session.updated_dt = dt.datetime.now()
                        update_session.is_delete = constants.YES
                        db.commit()
                    user = json.dumps(data[0], cls=ExtendEncoder)
                    token = jwt.encode(json.loads(user), str(SECRET_KEY))
                    # header_str = headerstr(self.env)
                    # token_str = tokenstr(token, self.env)
                    # headers = [ ('Set-Cookie', header_str) ]
                    jsonStr["data"] = constants.STATUS_SUCCESS
                    jsonStr["isError"] = constants.NO
                    jsonStr["status"] = "Success"

                    usersession = UserSession()
                    usersession.cd = uuid4().hex
                    usersession.user_cd = data[0].cd
                    usersession.created_dt = dt.datetime.now()
                    usersession.is_delete = constants.NO

                    db.add(usersession)
                    db.commit()
                else:
                    raise Exception("Wrong Password")
            else:
                raise Exception("User Not Found")

        except Exception as ex:
            self.log.error(ex)
            raise HTTPException(status_code=500, detail=str(ex))
        # print(headers)
        headers = response_cookies(self.env, token)
        response = JSONResponse(content=jsonStr, headers=headers)
        return response
    
    def loginAdmin(self, request, db, SECRET_KEY):
        jsonStr = {}
        try:
            username = request.username
            password = request.password.encode()

            query = db.query(User, UserCredential)
            query = query.join(User, User.cd == UserCredential.user_cd)
            query = query.filter(User.role_cd.in_(['owner', 'supervisor']))
            query = query.filter(User.username == username)
            # self.log.info(query.statement.compile(compile_kwargs={"literal_binds": True}))
            
            data = query.first()

            db.close()
            if data is not None:
                pwhash = bcrypt.hashpw(password, data[1].password.encode('utf8')).decode('utf8')
                if data[1].password == pwhash:
                    query = db.query(UserSession)
                    query = query.filter(UserSession.user_cd == data[0].cd)
                    query = query.filter(UserSession.is_delete == constants.NO)
                    data_session = query.first()
                    db.close()
                    if data_session:
                        update_session = db.query(UserSession).get(data_session.cd)
                        update_session.updated_dt = dt.datetime.now()
                        update_session.is_delete = constants.YES
                        db.commit()
                    
                    user = json.loads(json.dumps(data[0], cls=ExtendEncoder))

                    access_token_expires = dt.timedelta(minutes=constants.ACCESS_TOKEN_EXPIRE_MINUTES)
                    access_token = create_access_token(
                        data=user, secret_key=SECRET_KEY, expires_delta=access_token_expires
                    )

                    refresh_token_expires = dt.timedelta(days=constants.REFRESH_TOKEN_EXPIRE_DAYS)
                    refresh_token = create_refresh_token(
                        data=user, secret_key=SECRET_KEY, expires_delta=refresh_token_expires
                    )

                    jsonStr["data"] = constants.STATUS_SUCCESS
                    jsonStr["isError"] = constants.NO
                    jsonStr["status"] = "Success"
                    jsonStr["access_token"] = access_token
                    jsonStr["refresh_token"] = refresh_token

                    usersession = UserSession()
                    usersession.cd = uuid4().hex
                    usersession.user_cd = data[0].cd
                    usersession.created_dt = dt.datetime.now()
                    usersession.is_delete = constants.NO

                    db.add(usersession)
                    db.commit()
                else:
                    raise Exception("Wrong Password")
            else:
                raise Exception("User Not Found")

        except Exception as ex:
            self.log.error(ex)
            response = JSONResponse(status_code=500, content={"data": str(ex), "isError": constants.YES, "status": constants.STATUS_FAILED})
            return response
        
        response = JSONResponse(content=jsonStr)
        return response
    
    def checkCredentialSupervisor(self, request, db, SECRET_KEY):
        jsonStr = {}
        try:
            ## self.log.info("Response "+str(jsonStr))
            password = request.password.encode()

            query = db.query(User, UserCredential)
            query = query.join(User, User.cd == UserCredential.user_cd)
            query = query.filter(User.role_cd.in_(['supervisor', 'owner']))  # Check for both roles

            # Fetch all matching records
            users_data = query.all()

            jsonStr["isError"] = constants.YES
            jsonStr["status"] = "Failed"
            status = 500

            for data in users_data:
                pwhash = bcrypt.hashpw(password, data[1].password.encode('utf8')).decode('utf8')
                # #self.log.info(data.password)
                # #self.log.info(pwhash)
                # #self.log.info(data[0])
                if data[1].password == pwhash:

                    jsonStr["data"] = constants.STATUS_SUCCESS
                    jsonStr["isError"] = constants.NO
                    jsonStr["status"] = "Success"
                    status = 200
                    
            return jsonStr, status

        except Exception as ex:
            self.log.exception(" UserService")
            jsonStr["isError"] = constants.YES
            jsonStr["status"] = "Failed"
            response = jsonStr, 500
            return response