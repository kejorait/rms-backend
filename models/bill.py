from sqlalchemy import Column, DateTime, Integer, Numeric, String

from models.base import DeclarativeOrigin


class Bill(DeclarativeOrigin):
    __tablename__ = "bill"
    cd = Column(String, primary_key=True)
    bill_total = Column(Numeric)
    paid_type = Column(String)
    paid_amount = Column(Integer)
    paid_change = Column(Integer)
    billiard_amount = Column(Integer)
    billiard_total = Column(Numeric)
    billiard_price = Column(Integer)
    grand_total = Column(Numeric)
    table_cd = Column(String)
    created_dt = Column(DateTime)
    created_by = Column(String)
    is_inactive = Column(String, default='N')
    is_delete = Column(String, default='N')
    is_closed = Column(String, default='N')
    is_paid = Column(String, default='N')
    is_paid_billiard = Column(String, default='N')
    closed_dt = Column(DateTime)
    billiard_closed_dt = Column(DateTime)
    closed_by = Column(String)
    moved_dt = Column(DateTime)
    moved_by = Column(String)
    paid_dt = Column(DateTime)
    paid_by = Column(String)
    billiard_paid_dt = Column(DateTime)
    billiard_paid_by = Column(String)
    user_nm = Column(String)
    is_waitinglist = Column(String)