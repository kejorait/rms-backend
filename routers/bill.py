from fastapi import APIRouter, Depends
from services.bill_activity import BillService
from helper.database import get_db
from sqlalchemy.orm import Session
from models.request import bill

router = APIRouter(
    prefix="/bill"
)


@router.post("/create")
def add_bill(request: bill.Create, db: Session = Depends(get_db)):
    return BillService().addBill(request, db)


@router.post("/update")
def update_bill(request: bill.Update, db: Session = Depends(get_db)):
    return BillService().updateBill(request, db)


@router.post("/delete")
def delete_bill(request: bill.Delete, db: Session = Depends(get_db)):
    return BillService().deleteBill(request, db)


@router.post("/close")
def close_bill(request: bill.Close, db: Session = Depends(get_db)):
    return BillService().closeBill(request, db)


@router.post("/paid")
def pay_bill(request: bill.Paid, db: Session = Depends(get_db)):
    return BillService().paidBill(request, db)

@router.post("/summary")
def GetBillSummary(request: bill.FromToDt, db: Session = Depends(get_db)):
    return BillService().getBillSummary(request, db)