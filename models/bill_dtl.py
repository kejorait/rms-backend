from sqlalchemy import Column, DateTime, Integer, String

from models.base import DeclarativeOrigin


class BillDtl(DeclarativeOrigin):
    __tablename__ = "bill_dtl"
    cd = Column(String, primary_key=True)
    bill_cd = Column(String)
    process_status = Column(String)
    menu_cd = Column(String)
    user_nm = Column(String)
    qty = Column(Integer)
    init_qty = Column(Integer)
    price = Column(Integer, default=0)
    discount = Column(Integer, default=0)
    created_dt = Column(DateTime)
    created_by = Column(String)
    is_inactive = Column(String)
    is_delete = Column(String)
    updated_dt = Column(DateTime)
    split_qty = Column(Integer)
    desc = Column(String)