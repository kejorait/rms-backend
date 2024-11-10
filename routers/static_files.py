import os

from fastapi import APIRouter
from fastapi.responses import FileResponse

SECRET_KEY = os.getenv("SECRET_KEY")

router = APIRouter()

@router.get("/cashier/{path:path}")
async def serve_react_app(path: str):
    # Check if the requested file exists in the 'dashboard' folder
    full_path = os.path.join("./static/cashier", path)
    if path != "" and os.path.exists(full_path):
        return FileResponse(full_path)
    else:
        # For any other route under `/cashier`, serve 'index.html' for the SPA
        return FileResponse("./static/cashier/index.html")