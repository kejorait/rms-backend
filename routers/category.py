import os
from fastapi import APIRouter, Depends
from helper.database import get_db
from sqlalchemy.orm import Session
from models.request import category
from services.category_activity import CategoryService

SECRET_KEY = os.getenv("SECRET_KEY")

router = APIRouter(
    prefix="/category"
)

@router.post("/get")
def GetAllCategory(request: category.Get, db: Session = Depends(get_db)):
    return CategoryService().getAllCategory(request, db)


@router.post("/get-by-cd")
def GetCategoryByCd(request: category.Get, db: Session = Depends(get_db)):
    return CategoryService().getCategoryByCd


@router.post("/create")
def add_category(request: category.Create = Depends(), db: Session = Depends(get_db)):
    return CategoryService().addCategory(request, db)


@router.post("/update")
def update_category(request: category.Update = Depends(), db: Session = Depends(get_db)):
    return CategoryService().updateCategory(request, db)


@router.post("/delete")
def delete_category(request: category.Delete, db: Session = Depends(get_db)):
    return CategoryService().deleteCategory(request, db)

