from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from helper.database import get_db
from models.request import user
from services.user_activity import UserService

router = APIRouter(
    prefix="/user"
)

tags = ["User"]

@router.post("/get-by-role", tags=tags)
def get_user_by_role(request: user.GetByRole, db: Session = Depends(get_db)):
    return UserService().getUserByRole(request, db)


@router.post("/get-all", tags=tags)
def get_all_user(request: user.GetAll, db: Session = Depends(get_db)):
    return UserService().getAllUser(request, db)


@router.post("/get", tags=tags)
def get_user(request: user.Get, db: Session = Depends(get_db)):
    return UserService().getUser(request, db)


@router.post("/update", tags=tags)
def update_user(request: user.Update = Depends(), db: Session = Depends(get_db)):
    return UserService().updateUser(request, db)


@router.post("/delete", tags=tags)
def delete_user(request: user.Delete, db: Session = Depends(get_db)):
    return UserService().deleteUser(request, db)

@router.post("/create", tags=tags)
def AddUser(request: user.Create = Depends(), db: Session = Depends(get_db)):
    return UserService().addUser(request, db)
