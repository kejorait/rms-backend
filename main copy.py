import os
from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import jwt
from functools import wraps
from dotenv import load_dotenv
import yaml
from services.menu_activity import MenuService
from services.user_activity import UserService
from services.bill_activity import BillService
from services.table_activity import TableService
from services.waiting_list_activity import WaitingListService
from services.user_credential_activity import UserCredentialService
from services.category_activity import CategoryService
from services.table_session_activity import TableSessionService
from services.app_setting_activity import AppSettingService
from services.role_activity import RoleService
import uvicorn
from models.request.app_setting import Update

from routers import auth, bill, bill_dtl, menu, table, user, waiting_list

load_dotenv()

app = FastAPI(root_path="/api/v1")
# app = FastAPI(docs_url=None, redoc_url=None)

ENV = os.getenv("ENV")

MENU_PATH = os.getenv("MENU_PATH")
USER_PATH = os.getenv("USER_PATH")
CATEGORY_PATH = os.getenv("CATEGORY_PATH")

MENU_FOLDER = "./" + MENU_PATH
USER_FOLDER = "./" + USER_PATH
CATEGORY_FOLDER = "./" + CATEGORY_PATH

MENU_ROUTE = "/" + MENU_PATH + "{name}"
USER_ROUTE = "/" + USER_PATH + "{name}"
CATEGORY_ROUTE = "/" + CATEGORY_PATH + "{name}"

# Initialize origin_list as an empty list in case the file is not found
origin_list = []

try:
    # Attempt to read YAML data from file
    with open("origins.yaml", "r") as f:
        yaml_data_str = f.read()

    # Deserialize YAML data back to Python list
    data = yaml.safe_load(yaml_data_str)
    if isinstance(data, dict) and "origin_list" in data:
        origin_list = data["origin_list"]
    else:
        print("Invalid YAML format: 'origin_list' not found.")
except FileNotFoundError:
    print("YAML file not found. Using empty list.")
except yaml.YAMLError as e:
    print(f"Error loading YAML: {e}")
    # Optionally, handle the exception or log it as needed

# print(origin_list)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["origin_list"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pg_user = os.getenv("PG_USER")
pg_pwd = os.getenv("PG_PWD")
pg_port = os.getenv("PG_PORT")
pg_db = os.getenv("PG_DB")
pg_host = os.getenv("PG_HOST")

DATABASE_URL = f"postgresql://{pg_user}:{pg_pwd}@{pg_host}:{pg_port}/{pg_db}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
SECRET_KEY = os.getenv("SECRET_KEY")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_token(token: str, role_list: list):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        if payload["role_cd"] not in role_list:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Authentication token",
            )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )


app.include_router(bill.router)

app.include_router(bill_dtl.router)

app.include_router(menu.router)

app.include_router(user.router)

app.include_router(auth.router)

app.include_router(table.router)

app.include_router(waiting_list.router)


@app.get(MENU_ROUTE)
def display_file_menu(name: str):
    return FileResponse(path=os.path.join(MENU_FOLDER, name))


@app.get(USER_ROUTE)
def display_file_user(name: str):
    return FileResponse(path=os.path.join(USER_FOLDER, name))


@app.get(CATEGORY_ROUTE)
def display_file_category(name: str):
    return FileResponse(path=os.path.join(CATEGORY_FOLDER, name))



@app.post("/get-bill-summary")
def GetBillSummary(request: BaseModel, db: Session = Depends(get_db)):
    return BillService().getBillSummary(request, db)


@app.post("/get-all-category")
def GetAllCategory(request: BaseModel, db: Session = Depends(get_db)):
    return CategoryService().getAllCategory(request, db)


@app.post("/get-category-by-cd")
def GetCategoryByCd(request: BaseModel, db: Session = Depends(get_db)):
    return CategoryService().getCategoryByCd


@app.post("/add-category")
def add_category(request: BaseModel, db: Session = Depends(get_db)):
    return CategoryService().addCategory(request, db)


@app.post("/update-category")
def update_category(request: BaseModel, db: Session = Depends(get_db)):
    return CategoryService().updateCategory(request, db)


@app.post("/delete-category")
def delete_category(request: BaseModel, db: Session = Depends(get_db)):
    return CategoryService().deleteCategory(request, db)


@app.post("/get-all-role")
def get_role(request: BaseModel, db: Session = Depends(get_db)):
    return RoleService().getAllRole(request, db)


@app.post("/table-session-open")
def table_session_open(request: BaseModel, db: Session = Depends(get_db)):
    return TableSessionService().tableSessionOpen(request, db)


@app.post("/table-session-close")
def table_session_close(request: BaseModel, db: Session = Depends(get_db)):
    return TableSessionService().tableSessionClose(request, db)


@app.post("/table-session-fixed")
def table_session_fixed(request: BaseModel, db: Session = Depends(get_db)):
    return TableSessionService().tableSessionFixed(request, db)


@app.post("/get-all-app-setting")
def get_all_app_setting(request: BaseModel, db: Session = Depends(get_db)):
    return AppSettingService().getAllAppSetting(request, db)


@app.post("/update-app-setting")
def update_app_setting(request: Update, db: Session = Depends(get_db)):
    res = AppSettingService().updateAppSetting(request, db)
    return res


if __name__ == "__main__":
    if ENV == "DEV":
        print("Running in development mode")
        uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    else:
        uvicorn.run("main:app", host="0.0.0.0", port=3000)
