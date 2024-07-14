from sqlalchemy import Column,String,Integer,DateTime
from sqlalchemy.orm import declarative_base

from models.base import DATEFIELDS, DeclarativeOrigin

class User(DeclarativeOrigin):
    __tablename__ = "user"
    cd = Column(String, primary_key=True)
    name = Column(String)
    username = Column(String)
    role_cd = Column(String)
    created_by = Column(String)
    created_dt = Column(DateTime)
    updated_by = Column(String)
    updated_dt = Column(DateTime)
    is_inactive = Column(String)
    is_delete = Column(String)
    is_resign = Column(String)
    img = Column(String)