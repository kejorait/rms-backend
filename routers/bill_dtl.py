from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from helper.database import get_db
from models.request import bill_dtl as bill_dtl
from services.bill_dtl_activity import BillDtlService

router = APIRouter(
    prefix="/bill-dtl"
)


@router.post("/get")
def get_bill_detail(request: bill_dtl.Get, db: Session = Depends(get_db)):
    return BillDtlService().getBillDtlByTable(request, db)


@router.post("/get-by-cd")
def get_bill_detail_by_cd(request: bill_dtl.GetByCd, db: Session = Depends(get_db)):
    return BillDtlService().getBillDtlByBillCd(request, db)


@router.post("/print")
def get_bill_detail_by_cd_print(request: bill_dtl.Print, db: Session = Depends(get_db)):
    return BillDtlService().getBillDtlByBillCdPrint(request, db)


@router.post("/get-all-barista")
def get_bill_all_detail(request: bill_dtl.FromToDt, db: Session = Depends(get_db)):
    return BillDtlService().getBillDtlAllTableBarista(request, db)


@router.post("/get-all-kitchen")
def get_bill_all_detail_kitchen(request: bill_dtl.FromToDt, db: Session = Depends(get_db)):
    return BillDtlService().getBillDtlAllTableKitchen(request, db)


@router.post("/single-create")
def add_bill_detail(request: bill_dtl.Create, db: Session = Depends(get_db)):
    return BillDtlService().addBillDetail(request, db)


@router.post("/create")
def bulk_add_bill_detail(request: bill_dtl.CreateBulk, db: Session = Depends(get_db)):
    return BillDtlService().bulkaddBillDetail(request, db)


@router.post("/update")
def update_bill_detail(request: bill_dtl.Update, db: Session = Depends(get_db)):
    return BillDtlService().updateBillDetail(request, db)


@router.post("/update-qty")
def update_bill_detail_qty(request: bill_dtl.UpdateQty, db: Session = Depends(get_db)):
    return BillDtlService().updateBillDetailQty(request, db)


@router.post("/delete")
def delete_bill_detail(request: bill_dtl.Delete, db: Session = Depends(get_db)):
    return BillDtlService().deleteBillDetail(request, db)


@router.post("/bulk-delete")
def delete_bill_detail_bulk(request: bill_dtl.DeleteBulk, db: Session = Depends(get_db)):
    return BillDtlService().deleteBillDetailBulk(request, db)
