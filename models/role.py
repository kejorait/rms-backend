from sqlalchemy import Column,String,Integer,DateTime
from sqlalchemy.orm import declarative_base

from models.base import DATEFIELDS, DeclarativeOrigin

class Role(DeclarativeOrigin):
    __tablename__ = "role"
    cd = Column(String, primary_key=True)
    nm = Column(String)
    created_by = Column(String)
    created_dt = Column(DateTime)
    updated_by = Column(String)
    updated_dt = Column(DateTime)
    is_delete = Column(String)