import os

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from helper.database import get_db
from models.request import auth
from services.user_credential_activity import UserCredentialService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = os.getenv("SECRET_KEY")

router = APIRouter(
    prefix="/auth"
)

@router.post("/login")
async def login(
    request: auth.Login,
    db: Session = Depends(get_db)
):
    return UserCredentialService().login(request, db, SECRET_KEY)

# @router.post("/login-check")
# async def check_user_credential(
#     request: auth.Login,
#     db: Session = Depends(get_db)
# ):
#     return UserCredentialService().checkCredential(request, db, SECRET_KEY)

@router.post("/admin/login")
async def login_admin(
    request: auth.Login,
    db: Session = Depends(get_db)
):
    return UserCredentialService().checkCredentialAdmin(request, db, SECRET_KEY)