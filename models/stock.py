from sqlalchemy import Column,String,Integer,DateTime
from sqlalchemy.orm import declarative_base

from models.base import DATEFIELDS, DeclarativeOrigin

class Stock(DeclarativeOrigin):
    __tablename__ = 'stock'
    cd = Column(String, primary_key=True)
    nm = Column(String)
    amount = Column(Integer)
    desc = Column(String)
    price = Column(Integer)
    created_dt = Column(DateTime)
    created_by = Column(String)
    updated_dt = Column(DateTime)
    updated_by = Column(String)
    is_delete = Column(String)
    is_inactive = Column(String)