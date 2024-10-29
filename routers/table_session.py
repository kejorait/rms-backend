import os
from fastapi import APIRouter, Depends
from helper.database import get_db
from sqlalchemy.orm import Session
from models.request import table_session
from services.table_session_activity import TableSessionService

SECRET_KEY = os.getenv("SECRET_KEY")

router = APIRouter(
    prefix="/table-session"
)


@router.post("/open")
def table_session_open(request: table_session.Open, db: Session = Depends(get_db)):
    return TableSessionService().tableSessionOpen(request, db)


@router.post("/close")
def table_session_close(request: table_session.Close, db: Session = Depends(get_db)):
    return TableSessionService().tableSessionClose(request, db)


@router.post("/fixed")
def table_session_fixed(request: table_session.Fixed, db: Session = Depends(get_db)):
    return TableSessionService().tableSessionFixed(request, db)