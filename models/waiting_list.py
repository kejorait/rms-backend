from sqlalchemy import Column,String,Integer,DateTime
from sqlalchemy.orm import declarative_base

from models.base import DATEFIELDS, DeclarativeOrigin

class WaitingList(DeclarativeOrigin):
    __tablename__ = 'waiting_list'
    cd = Column(String, primary_key=True)
    nm = Column(String)
    created_dt = Column(String)
    is_delete = Column(String)
    updated_dt = Column(String)