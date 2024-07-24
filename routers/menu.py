from fastapi import APIRouter, Depends
from services.menu_activity import MenuService
from helper.database import get_db
from sqlalchemy.orm import Session
from models.request import menu

router = APIRouter(
    prefix="/menu"
)


@router.post("/get")
def get_menu(request: menu.Get, db: Session = Depends(get_db)):
    return MenuService().getMenu(request, db)

@router.post("/get-all")
def get_menu_all(request: menu.GetAll, db: Session = Depends(get_db)):
    return MenuService().getMenuAll(request, db)

@router.post("/get-by-cd")
def get_menu_by_code(request: menu.GetByCd, db: Session = Depends(get_db)):
    return MenuService().getMenuByCode(request, db)

@router.post("/create")
def add_menu(request: menu.Create, db: Session = Depends(get_db)):
    print("add")
    return MenuService().addMenu(request, db)

@router.post("/update")
def update_menu(request: menu.Update, db: Session = Depends(get_db)):
    return MenuService().updateMenu(request, db)

@router.post("/delete")
def delete_menu(request: menu.Delete, db: Session = Depends(get_db)):
    return MenuService().deleteMenu(request, db)
