import multiprocessing
import os
import re

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Response
from fastapi_socketio import SocketManager

# chromedriver_autoinstaller.install()
os.makedirs("./logs", exist_ok=True)
import router

load_dotenv(override=True)

app = FastAPI(
    swagger_ui_parameters={"defaultModelsExpandDepth": -1})
socket_manager = SocketManager(app=app, mount_location='/socket.io', cors_allowed_origins=[])

# @app.get("/")
# async def index():
#     return {"message": "Socket.IO server running!"}

# Socket.IO event listener for "new-order" messages
@socket_manager.on('new-order')
async def handle_new_order(sid, data):
    await socket_manager.emit('new-order', data)

# Set up CORS for development environment
allowed_origin_patterns = [
    r"^http?://localhost(:[0-9]+)?$",
    r"^https?://([a-zA-Z0-9-]+\.)*kejora\.my\.id(:[0-9]+)?$",
    r"http://100.92.3.3:5173",
]
@app.middleware("http")
async def cors_middleware(request: Request, call_next):
    origin = request.headers.get("origin")

    # Handle CORS preflight request for OPTIONS
    if request.method == "OPTIONS" and origin and any(re.match(pattern, origin) for pattern in allowed_origin_patterns):
        response = Response(status_code=204)  # Return 204 No Content   
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization"
        return response

    # Handle other requests
    response = await call_next(request)
    if origin and any(re.match(pattern, origin) for pattern in allowed_origin_patterns):
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"

    return response



app.include_router(router.router)