import base64
import os
from datetime import datetime
from io import BytesIO

from fastapi.responses import FileResponse, JSONResponse
from PIL import Image

from helper import constants
from models.app_setting import AppSetting


class UploadActivity:

    def getLogo(self,db, ext, LOGO_FILE_PATH):
        # check if file exists
        if not os.path.exists(LOGO_FILE_PATH + "." + ext):
            # Check if logo_base64 is provided (e.g., from app settings)
            logo_base64 = db.query(AppSetting).filter(AppSetting.cd == "logo_base64").first().value
            if logo_base64:
                try:
                    # Decode the base64 string into bytes
                    logo_data = base64.b64decode(logo_base64)

                    # Use PIL to open the image from the byte data
                    image = Image.open(BytesIO(logo_data))

                    # Save the image as either .ico or .png based on the requested extension
                    if ext == 'ico':
                        # Save the image as ICO
                        image.save(LOGO_FILE_PATH + ".ico", format="ICO")
                    elif ext == 'png':
                        # Save the image as PNG
                        image.save(LOGO_FILE_PATH + ".png", format="PNG")
                    else:
                        return JSONResponse(
                            content={
                                "isError": constants.YES,
                                "status": "Failed",
                                "error": "Unsupported file extension",
                            },
                            status_code=400,
                        )

                    # Return the saved image file
                    return FileResponse(path=LOGO_FILE_PATH + "." + ext)

                except Exception as e:
                    return JSONResponse(
                        content={
                            "isError": constants.YES,
                            "status": "Failed",
                            "error": f"Error processing Base64 image: {str(e)}",
                        },
                        status_code=500,
                    )
            else:
                return JSONResponse(
                    content={
                        "isError": constants.YES,
                        "status": "Failed",
                        "error": "File not found and no Base64 logo available",
                    },
                    status_code=404,
                )
        # If the file exists, return it as a file response
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
