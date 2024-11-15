import os

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from helper.database import get_db
from models.request import table
from services.dining_table_activity import DiningTableService

SECRET_KEY = os.getenv("SECRET_KEY")

router = APIRouter(
    prefix="/dining-table"
)

tags = ["Dining Table"]

@router.post("/get", tags=tags)
async def get_all_dining_table(request: table.Get, db: Session = Depends(get_db)):
    return DiningTableService().getAllDiningTable(request, db)

# @router.post("/create", tags=tags)
# async def create_table(request: table.Create, db: Session = Depends(get_db)):
#     return TableService().createTable(request, db)

# @router.post("/update", tags=tags)
# async def update_table(request: table.Update, db: Session = Depends(get_db)):
#     return TableService().updateTable(request, db)

# @router.post("/delete", tags=tags)
# async def delete_table(request: table.Delete, db: Session = Depends(get_db)):
#     return TableService().deleteTable(request, db)

# @router.post("/delete-bulk", tags=tags)
# async def delete_table_bulk(request: table.DeleteBulk, db: Session = Depends(get_db)):
#     return TableService().deleteTableBulk(request, db)