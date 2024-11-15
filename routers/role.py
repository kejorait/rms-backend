import os

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from helper.database import get_db
from models.request import role
from services.role_activity import RoleService

SECRET_KEY = os.getenv("SECRET_KEY")

router = APIRouter(
    prefix="/role"
)

tags = ["Role"]

@router.post("/get", tags=tags)
def get_role(request: role.Get, db: Session = Depends(get_db)):
    return RoleService().getAllRole(request, db)