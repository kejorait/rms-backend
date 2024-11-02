import base64
import json
from datetime import datetime
import datetime as dt
import os
from io import BytesIO
from fastapi.responses import JSONResponse, FileResponse
from models.table import Table
from models.bill import Bill
from models.app_setting import AppSetting
from helper.jsonHelper import ExtendEncoder
from helper import constants
from utils.tinylog import getLogger, setupLog
from uuid import uuid4
from sqlalchemy import func, Integer
from sqlalchemy.sql.expression import cast, and_
import sqlalchemy
from sqlalchemy.orm import aliased
from fastapi import HTTPException
from PIL import Image


class UploadActivity:

    def getLogo(self, ext, LOGO_FILE_PATH):
        # check if file exists
        if not os.path.exists(LOGO_FILE_PATH + "." + ext):
            # raise HTTPException(status_code=404, detail="File not found")
            return JSONResponse(
                content={
                    "isError": constants.YES,
                    "status": "Failed",
                    "error": "File not found",
                },
                status_code=404,
            )
        return FileResponse(path=LOGO_FILE_PATH + "." + ext)

    def uploadLogo(self, request, db, LOGO_FILE_PATH):
        # Json response
        jsonStr = {}
        file = request.file

        # Open the uploaded image
        image = Image.open(file.file)

        file_path_ico = LOGO_FILE_PATH + ".ico"
        file_path_png = LOGO_FILE_PATH + ".png"

        # Convert the image to a BytesIO object
        buffered = BytesIO()
        image.save(buffered, format="PNG")  # or use "PNG" if your image is in PNG format

        # Encode the image to Base64
        base64_string = base64.b64encode(buffered.getvalue()).decode()
        query = db.query(AppSetting)
        query = query.filter(AppSetting.cd == "logo_base64")
        data = query.first()
        if data:
            data.value = base64_string
        else:
            data = AppSetting(
                cd="logo_base64",
                value=base64_string,
                created_dt=datetime.now(),
                created_by="system",
            )
        db.commit()

        try:
            image.save(file_path_ico, format="ICO")
            image.save(file_path_png, format="PNG")
            jsonStr = {"isError": constants.NO, "status": "Success"}
        except Exception as e:
            jsonStr = {"isError": constants.YES, "status": "Failed", "error": str(e)}
        return jsonStr
