from sqlalchemy import Column,String,Integer,DateTime
from sqlalchemy.orm import declarative_base

from models.base import DATEFIELDS, DeclarativeOrigin

class BillDtl(DeclarativeOrigin):
    __tablename__ = "bill_dtl"
    cd = Column(String, primary_key=True)
    bill_cd = Column(String)
    process_status = Column(String)
    menu_cd = Column(String)
    user_nm = Column(String)
    qty = Column(Integer)
    init_qty = Column(Integer)
    created_dt = Column(DateTime)
    created_by = Column(String)
    is_inactive = Column(String)
    is_delete = Column(String)
    updated_dt = Column(DateTime)
    split_qty = Column(Integer)
    desc = Column(String)