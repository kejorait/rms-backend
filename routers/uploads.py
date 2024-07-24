import os
from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from helper.database import get_db
from sqlalchemy.orm import Session
from models.request import category
from services.category_activity import CategoryService

SECRET_KEY = os.getenv("SECRET_KEY")

router = APIRouter(
    prefix="/uploads"
)

MENU_PATH = os.getenv("MENU_PATH")
USER_PATH = os.getenv("USER_PATH")
CATEGORY_PATH = os.getenv("CATEGORY_PATH")
UPLOADS_PATH = os.getenv("UPLOADS_PATH")

MENU_FOLDER = "./" + UPLOADS_PATH+ "/" + MENU_PATH
USER_FOLDER = "./" + UPLOADS_PATH+ "/" + USER_PATH
CATEGORY_FOLDER = "./" + UPLOADS_PATH+ "/" + CATEGORY_PATH

MENU_ROUTE = "/" + MENU_PATH + "/"
USER_ROUTE = "/" + USER_PATH + "/"
CATEGORY_ROUTE = "/" + CATEGORY_PATH + "/"

os.makedirs(MENU_FOLDER, exist_ok=True)
os.makedirs(USER_FOLDER, exist_ok=True)
os.makedirs(CATEGORY_FOLDER, exist_ok=True)

@router.get(CATEGORY_ROUTE+"{name}")
def display_file_category(name: str):
    return FileResponse(path=os.path.join(CATEGORY_FOLDER, name))

@router.get(MENU_ROUTE+"{name}")
def display_file_menu(name: str):
    return FileResponse(path=os.path.join(MENU_FOLDER, name))


@router.get(USER_ROUTE+"{name}")
def display_file_user(name: str):
    return FileResponse(path=os.path.join(USER_FOLDER, name))