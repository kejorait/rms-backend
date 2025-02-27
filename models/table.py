from sqlalchemy import Column, DateTime, String

from models.base import DeclarativeOrigin


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
    serial_sent = Column(String, default='Y')
    sent_closed = Column(String, default='Y')
    serial_status = Column(String, default='OFF')
    serial_off_dt = Column(DateTime)
    