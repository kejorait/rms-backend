import os

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from helper.database import get_db
from models.request import category
from services.category_activity import CategoryService

SECRET_KEY = os.getenv("SECRET_KEY")

router = APIRouter(
    prefix="/category"
)

tags = ["Category"]

@router.post("/get", tags=tags)
def GetAllCategory(request: category.Get, db: Session = Depends(get_db)):
    return CategoryService().getAllCategory(request, db)


@router.post("/get-by-cd", tags=tags)
def GetCategoryByCd(request: category.GetDtl, db: Session = Depends(get_db)):
    return CategoryService().getCategoryByCd(request, db)


@router.post("/create", tags=tags)
def add_category(request: category.Create = Depends(), db: Session = Depends(get_db)):
    return CategoryService().addCategory(request, db)


@router.post("/update", tags=tags)
def update_category(request: category.Update = Depends(), db: Session = Depends(get_db)):
    return CategoryService().updateCategory(request, db)


@router.post("/delete", tags=tags)
def delete_category(request: category.Delete, db: Session = Depends(get_db)):
    return CategoryService().deleteCategory(request, db)

