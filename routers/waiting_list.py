import os
from fastapi import APIRouter, Depends
from helper.database import get_db
from sqlalchemy.orm import Session
from models.request import waiting_list
from services.waiting_list_activity import WaitingListService

SECRET_KEY = os.getenv("SECRET_KEY")

router = APIRouter(
    prefix="/waiting-list"
)

@router.post("/get")
def get_all_waiting_list(request: waiting_list.Get, db: Session = Depends(get_db)):
    return WaitingListService().getAllWaitingList(request, db)


@router.post("/get-dtl")
def get_waiting_list_dtl(request: waiting_list.GetDtl, db: Session = Depends(get_db)):
    return WaitingListService().getWaitingListDtl(request, db)


@router.post("/create")
def add_waiting_list(request: waiting_list.Create, db: Session = Depends(get_db)):
    return WaitingListService().addWaitingList(request, db)


@router.post("/delete")
def delete_waiting_list(request: waiting_list.Delete, db: Session = Depends(get_db)):
    return WaitingListService().deleteWaitingList(request, db)
