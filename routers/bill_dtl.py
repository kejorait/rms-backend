from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from helper.database import get_db
from models.request import bill_dtl as bill_dtl
from services.bill_dtl_activity import BillDtlService
from services.print_activity import PrintService

router = APIRouter(
    prefix="/bill-dtl"
)

tags = ["Bill Detail"]

@router.post("/get", tags=tags)
def get_bill_detail(request: bill_dtl.Get, db: Session = Depends(get_db)):
    return BillDtlService().getBillDtlByTable(request, db)


@router.post("/get-by-cd", tags=tags)
def get_bill_detail_by_cd(request: bill_dtl.GetByCd, db: Session = Depends(get_db)):
    return BillDtlService().getBillDtlByBillCd(request, db)


@router.post("/print", tags=tags)
def get_bill_detail_by_cd_print(request: bill_dtl.Print, db: Session = Depends(get_db)):
    return PrintService().printBill(request, db)

@router.post("/print-bill", tags=tags)
def get_bill_detail_by_cd_print(request: bill_dtl.Print, db: Session = Depends(get_db)):
    return BillDtlService().printBill(request, db)


@router.post("/get-all-barista", tags=tags)
def get_bill_all_detail(request: bill_dtl.FromToDt, db: Session = Depends(get_db)):
    return BillDtlService().getBillDtlAllTableBarista(request, db)


@router.post("/get-all-kitchen", tags=tags)
def get_bill_all_detail_kitchen(request: bill_dtl.FromToDt, db: Session = Depends(get_db)):
    return BillDtlService().getBillDtlAllTableKitchen(request, db)

@router.post("/single-create", tags=tags)
def add_bill_detail(request: bill_dtl.Create, db: Session = Depends(get_db)):
    return BillDtlService().addBillDetail(request, db)

@router.post("/create", tags=tags)
def bulk_add_bill_detail(request: bill_dtl.CreateBulk, db: Session = Depends(get_db)):
    return BillDtlService().bulkaddBillDetail(request, db)

@router.post("/update", tags=tags)
def update_bill_detail(request: bill_dtl.Update, db: Session = Depends(get_db)):
    return BillDtlService().updateBillDetail(request, db)

@router.post("/update-qty", tags=tags)
def update_bill_detail_qty(request: bill_dtl.UpdateQty, db: Session = Depends(get_db)):
    return BillDtlService().updateBillDetailQty(request, db)

@router.post("/delete", tags=tags)
def delete_bill_detail(request: bill_dtl.Delete, db: Session = Depends(get_db)):
    return BillDtlService().deleteBillDetail(request, db)

@router.post("/bulk-delete", tags=tags)
def delete_bill_detail_bulk(request: bill_dtl.DeleteBulk, db: Session = Depends(get_db)):
    return BillDtlService().deleteBillDetailBulk(request, db)

@router.post("/discount", tags=tags)
def discount_bill_detail(request: bill_dtl.Discount, db: Session = Depends(get_db)):
    return BillDtlService().discountBillDtl(request, db)