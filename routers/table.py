import os

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from helper.database import get_db
from models.request import table
from services.table_activity import TableService

SECRET_KEY = os.getenv("SECRET_KEY")

router = APIRouter(
    prefix="/table"
)

@router.post("/get")
async def get_all_table(request: table.Get, db: Session = Depends(get_db)):
    return TableService().getAllTable(request, db)

@router.post("/get-billiard")
async def get_all_table_billiard(request: table.Get, db: Session = Depends(get_db)):
    return TableService().getAllTableBilliard(request, db)

@router.post("/create")
async def create_table(request: table.Create, db: Session = Depends(get_db)):
    return TableService().createTable(request, db)

@router.post("/update")
async def update_table(request: table.Update, db: Session = Depends(get_db)):
    return TableService().updateTable(request, db)

@router.post("/delete")
async def delete_table(request: table.Delete, db: Session = Depends(get_db)):
    return TableService().deleteTable(request, db)

@router.post("/delete-bulk")
async def delete_table_bulk(request: table.DeleteBulk, db: Session = Depends(get_db)):
    return TableService().deleteTableBulk(request, db)

@router.post("/get-by-cd")
def get_table_by_code(request: table.GetByCd, db: Session = Depends(get_db)):
    return TableService().getTableByCode(request, db)