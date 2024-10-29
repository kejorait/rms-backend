from sqlalchemy import Column, DateTime, Integer, String

from models.base import DeclarativeOrigin


class Bill(DeclarativeOrigin):
    __tablename__ = "bill"
    cd = Column(String, primary_key=True)
    bill_total = Column(Integer)
    paid_type = Column(String)
    paid_amount = Column(Integer)
    paid_change = Column(Integer)
    table_cd = Column(String)
    created_dt = Column(DateTime)
    created_by = Column(String)
    is_inactive = Column(String)
    is_delete = Column(String)
    is_closed = Column(String)
    is_paid = Column(String)
    closed_dt = Column(DateTime)
    closed_by = Column(String)
    moved_dt = Column(DateTime)
    moved_by = Column(String)
    paid_dt = Column(DateTime)
    paid_by = Column(String)
    user_nm = Column(String)
    is_waitinglist = Column(String)