from sqlalchemy import Column, DateTime, Integer, String

from models.base import DeclarativeOrigin


class Menu(DeclarativeOrigin):
    __tablename__ = 'menu'
    cd = Column(String, primary_key=True)
    nm = Column(String)
    img = Column(String)
    desc = Column(String)
    price = Column(Integer)
    discount = Column(Integer, default=0)
    stock = Column(Integer, default=0)
    category_cd = Column(String)
    created_dt = Column(DateTime)
    created_by = Column(String)
    updated_dt = Column(DateTime)
    updated_by = Column(String)
    is_delete = Column(String)
    is_inactive = Column(String)
    is_drink = Column(String)