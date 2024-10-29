import os
from models.request import app_setting
from fastapi import APIRouter, Depends
from helper.database import get_db
from services.app_setting_activity import AppSettingService
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/app-setting"
)

@router.post("/update")
def update_app_setting(request: app_setting.Update, db: Session = Depends(get_db)):
    return AppSettingService().updateAppSetting(request, db)

@router.post("/get")
def get_all_app_setting(request: app_setting.Get, db: Session = Depends(get_db)):
    return AppSettingService().getAllAppSetting(request, db)

@router.get("/printers")
def get_printers():
    return AppSettingService().getPrinters()