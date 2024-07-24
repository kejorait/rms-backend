import os
from fastapi import APIRouter, Depends
from helper.database import get_db
from sqlalchemy.orm import Session
from models.request import table
from services.table_activity import TableService

SECRET_KEY = os.getenv("SECRET_KEY")

router = APIRouter(
    prefix="/table"
)

@router.post("/get")
async def get_all_table(request: table.Get, db: Session = Depends(get_db)):
    return TableService().getAllTable(request, db)

@router.post("/create")
async def create_table(request: table.Create, db: Session = Depends(get_db)):
    return TableService().createTable(request, db)

@router.post("/update")
async def update_table(request: table.Update, db: Session = Depends(get_db)):
    return TableService().updateTable(request, db)

@router.post("/delete")
async def delete_table(request: table.Delete, db: Session = Depends(get_db)):
    return TableService().deleteTable(request, db)