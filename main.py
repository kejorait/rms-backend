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
from models.request.user import GetByRole

from routers import bill, bill_dtl

load_dotenv()

app = FastAPI(root_path="/api/v1")
# app = FastAPI(docs_url=None, redoc_url=None)

ENV = os.getenv("ENV")
SECRET_KEY = os.getenv("SECRET_KEY")

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
Base = declarative_base()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

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
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Authentication token")
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

app.include_router(bill.router)

app.include_router(bill_dtl.router)

@app.post("/menu")
def get_menu(request: BaseModel, db: Session = Depends(get_db)):
    return MenuService().getMenu(request, db)

@app.post("/menu-all")
def get_menu_all(request: BaseModel, db: Session = Depends(get_db)):
    return MenuService().getMenuAll(request, db)

@app.post("/menu-by-cd")
def get_menu_by_code(request: BaseModel, db: Session = Depends(get_db)):
    return MenuService().getMenuByCode(request, db)

@app.post("/add-menu")
def add_menu(request: BaseModel, db: Session = Depends(get_db)):
    return MenuService().addMenu(request, db)

@app.get(MENU_ROUTE)
def display_file_menu(name: str):
    return FileResponse(path=os.path.join(MENU_FOLDER, name))

@app.get(USER_ROUTE)
def display_file_user(name: str):
    return FileResponse(path=os.path.join(USER_FOLDER, name))

@app.get(CATEGORY_ROUTE)
def display_file_category(name: str):
    return FileResponse(path=os.path.join(CATEGORY_FOLDER, name))

@app.post("/update-menu")
def update_menu(request: BaseModel, db: Session = Depends(get_db)):
    return MenuService().updateMenu(request, db)

@app.post("/delete-menu")
def delete_menu(request: BaseModel, db: Session = Depends(get_db)):
    return MenuService().deleteMenu(request, db)

@app.post("/get-user-by-role")
def get_user_by_role(request: GetByRole, db: Session = Depends(get_db)):
    return UserService().getUserByRole(request, db)

@app.post("/get-all-user")
def get_all_user(request: BaseModel, db: Session = Depends(get_db)):
    return UserService().getAllUser(request, db)

@app.post("/get-user")
def get_user(request: BaseModel, db: Session = Depends(get_db)):
    return UserService().getUser(request, db)

@app.post("/update-user")
def update_user(request: BaseModel, db: Session = Depends(get_db)):
    return UserService().updateUser(request, db)

@app.post("/delete-user")
def delete_user(request: BaseModel, db: Session = Depends(get_db)):
    return UserService().deleteUser(request, db)

@app.post("/get-all-table")
def get_all_table(request: BaseModel, db: Session = Depends(get_db)):
    return TableService().getAllTable(request, db)

@app.post("/get-all-waiting-list")
def get_all_waiting_list(request: BaseModel, db: Session = Depends(get_db)):
    return WaitingListService().getAllWaitingList(request, db)

@app.post("/get-waiting-list-dtl")
def get_waiting_list_dtl(request: BaseModel, db: Session = Depends(get_db)):
    return WaitingListService().getWaitingListDtl(request, db)

@app.post("/add-waiting-list")
def add_waiting_list(request: BaseModel, db: Session = Depends(get_db)):
    return WaitingListService().addWaitingList(request, db)

@app.post("/delete-waiting-list")
def delete_waiting_list(request: BaseModel, db: Session = Depends(get_db)):
    return WaitingListService().deleteWaitingList(request, db)

@app.post("/check-user-credential")
def check_user_credential(request: BaseModel, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    return UserCredentialService().checkCredential(request, db, SECRET_KEY, token)

@app.post("/check-user-credential-admin")
def check_user_credential_admin(request: BaseModel, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    return UserCredentialService().checkCredentialAdmin(request, db, SECRET_KEY, token)

@app.post("/check-user-credential-supervisor")
def check_user_credential_supervisor(request: BaseModel, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    return UserCredentialService().checkCredentialSupervisor(request, db, SECRET_KEY, token)

# Bill Summary Controller
@app.post("/get-bill-summary")
def GetBillSummary(request: BaseModel, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    return BillService().getBillSummary(request, db)

@app.post("/get-bill-summary")
def GetBillSummary(request: BaseModel, db: Session = Depends(get_db)):
    return BillService().getBillSummary(request, db)

@app.post("/add-user")
def AddUser(request: BaseModel, db: Session = Depends(get_db)):
    return UserService().addUser(request, db)

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
        uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    else:
        uvicorn.run("main:app", host="0.0.0.0", port=3000)
