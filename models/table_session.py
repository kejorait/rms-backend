from sqlalchemy import Column,String,Integer,DateTime
from sqlalchemy.orm import declarative_base

from models.base import DATEFIELDS, DeclarativeOrigin

class TableSession(DeclarativeOrigin):
    __tablename__ = "table_session"
    cd = Column(String, primary_key=True)
    table_cd = Column(String)
    created_dt = Column(DateTime)
    created_by = Column(String)
    amount = Column(Integer)
    is_inactive = Column(String)
    is_delete = Column(String)
    is_open = Column(String)
    is_closed = Column(String)
    is_paid = Column(String)
    closed_dt = Column(DateTime)
    closed_by = Column(String)
    user_nm = Column(String)
    bill_cd = Column(String)
    