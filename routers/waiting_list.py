import os

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from helper.database import get_db
from models.request import waiting_list
from services.waiting_list_activity import WaitingListService

SECRET_KEY = os.getenv("SECRET_KEY")

router = APIRouter(
    prefix="/waiting-list"
)

tags = ["Waiting List"]

@router.post("/get", tags=tags)
def get_all_waiting_list(request: waiting_list.Get, db: Session = Depends(get_db)):
    return WaitingListService().getAllWaitingList(request, db)


@router.post("/get-dtl", tags=tags)
def get_waiting_list_dtl(request: waiting_list.GetDtl, db: Session = Depends(get_db)):
    return WaitingListService().getWaitingListDtl(request, db)


@router.post("/create", tags=tags)
def add_waiting_list(request: waiting_list.Create, db: Session = Depends(get_db)):
    return WaitingListService().addWaitingList(request, db)


@router.post("/delete", tags=tags)
def delete_waiting_list(request: waiting_list.Delete, db: Session = Depends(get_db)):
    return WaitingListService().deleteWaitingList(request, db)
