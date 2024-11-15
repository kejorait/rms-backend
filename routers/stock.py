
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from helper.database import get_db
from models.request import stock
from services.stock_activity import StockService

router = APIRouter(prefix="/stock")

tags = ["Stock"]

@router.post("/get-all", tags=tags)
def get_stock_all(request: stock.GetAll, db: Session = Depends(get_db)):
    res = StockService().getStockAll(request, db)
    return res


@router.post("/get-by-cd", tags=tags)
def get_stock_by_code(request: stock.GetByCd, db: Session = Depends(get_db)):
    return StockService().getStockByCode(request, db)


@router.post("/create", tags=tags)
def add_stock(request: stock.Create, db: Session = Depends(get_db)):
    print("add")
    return StockService().addStock(request, db)


@router.post("/update", tags=tags)
def update_stock(request: stock.Update, db: Session = Depends(get_db)):
    return StockService().updateStock(request, db)


@router.post("/delete", tags=tags)
def delete_stock(request: stock.Delete, db: Session = Depends(get_db)):
    return StockService().deleteStock(request, db)

@router.post("/delete-bulk", tags=tags)
def delete_stock_bulk(request: stock.DeleteBulk, db: Session = Depends(get_db)):
    return StockService().deleteStockBulk(request, db)