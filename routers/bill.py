from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from helper.database import get_db
from models.request import bill
from services.bill_activity import BillService

router = APIRouter(
    prefix="/bill"
)

tags = ["Bill"]

@router.post("/create", tags=tags)
def add_bill(request: bill.Create, db: Session = Depends(get_db)):
    return BillService().addBill(request, db)

@router.post("/update", tags=tags)
def update_bill(request: bill.Update, db: Session = Depends(get_db)):
    return BillService().updateBill(request, db)

@router.post("/delete", tags=tags)
def delete_bill(request: bill.Delete, db: Session = Depends(get_db)):
    return BillService().deleteBill(request, db)

@router.post("/close", tags=tags)
def close_bill(request: bill.Close, db: Session = Depends(get_db)):
    return BillService().closeBill(request, db)


@router.post("/paid", tags=tags)
def pay_bill(request: bill.Paid, db: Session = Depends(get_db)):
    return BillService().paidBill(request, db)

@router.post("/summary", tags=tags)
def GetBillSummary(request: bill.FromToDt, db: Session = Depends(get_db)):
    return BillService().getBillSummary(request, db)