from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends
from helper.helper import get_pagination, paginate
from services.stock_activity import StockService
from controllers.stock import StockController
from helper.database import get_db
from sqlalchemy.orm import Session
from models.request import stock

router = APIRouter(
    prefix="/stock"
)


@router.post("/get")
def get_stock(request: stock.Get, db: Session = Depends(get_db)):
    return StockService().getStock(request, db)

@router.get("/get-all")
def get_stock_all(
    request: stock.GetAll, 
    db: Session = Depends(get_db), 
    pagination: dict = Depends(get_pagination),
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = "asc"
):
    res = StockController().getStockAll(request, db, pagination, sort_by, sort_order)
    return res

@router.post("/get-by-cd")
def get_stock_by_code(request: stock.GetByCd, db: Session = Depends(get_db)):
    return StockService().getStockByCode(request, db)

@router.post("/create")
def add_stock(request: stock.Create, db: Session = Depends(get_db)):
    print("add")
    return StockService().addStock(request, db)

@router.post("/update")
def update_stock(request: stock.Update, db: Session = Depends(get_db)):
    return StockService().updateStock(request, db)

@router.post("/delete")
def delete_stock(request: stock.Delete, db: Session = Depends(get_db)):
    return StockService().deleteStock(request, db)
