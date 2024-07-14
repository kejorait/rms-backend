from sqlalchemy import Column,String,Integer,DateTime
from sqlalchemy.orm import declarative_base

from models.base import DATEFIELDS, DeclarativeOrigin

class Table(DeclarativeOrigin):
    __tablename__ = 'table'
    cd = Column(String, primary_key=True)
    nm = Column(String)
    desc = Column(String)
    is_billiard = Column(String)
    created_dt = Column(DateTime)
    created_by = Column(String)
    updated_dt = Column(DateTime)
    updated_by = Column(String)
    is_inactive = Column(String)
    is_delete = Column(String)