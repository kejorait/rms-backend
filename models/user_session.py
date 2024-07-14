from sqlalchemy import Column,String,Integer,DateTime
from sqlalchemy.orm import declarative_base

from models.base import DATEFIELDS, DeclarativeOrigin

class UserSession(DeclarativeOrigin):
    __tablename__ = "user_session"
    cd = Column(String, primary_key=True)
    user_cd = Column(String)
    created_dt = Column(DateTime)
    updated_dt = Column(DateTime)
    is_delete = Column(String)