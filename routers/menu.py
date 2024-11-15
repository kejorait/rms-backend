from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from helper.database import get_db
from models.request import menu
from services.menu_activity import MenuService

router = APIRouter(prefix="/menu")

tags = ["Menu"]

@router.post("/get", tags=tags)
def get_menu(request: menu.Get, db: Session = Depends(get_db)):
    return MenuService().getMenu(request, db)


@router.post("/get-all", tags=tags)
def get_menu_all(request: menu.GetAll, db: Session = Depends(get_db)):
    return MenuService().getMenuAll(request, db)


@router.post("/get-by-cd", tags=tags)
def get_menu_by_code(request: menu.GetByCd, db: Session = Depends(get_db)):
    return MenuService().getMenuByCode(request, db)


@router.post("/create", tags=tags)
def add_menu(request: menu.Create = Depends(), db: Session = Depends(get_db)):
    return MenuService().addMenu(request, db)

@router.post("/update", tags=tags)
def update_menu(request: menu.Update = Depends(), db: Session = Depends(get_db)):
    return MenuService().updateMenu(request, db)

@router.post("/delete", tags=tags)
def delete_menu(request: menu.Delete, db: Session = Depends(get_db)):
    return MenuService().deleteMenu(request, db)
