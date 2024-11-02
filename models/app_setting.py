from sqlalchemy import Column,String,Integer,DateTime
from sqlalchemy.orm import declarative_base

from models.base import DATEFIELDS, DeclarativeOrigin

class AppSetting(DeclarativeOrigin):
    __tablename__ = 'app_setting'
    cd = Column(String, primary_key=True)
    nm = Column(String)
    desc = Column(String)
    value = Column(String)
    created_dt = Column(DateTime)
    created_by = Column(String)
    updated_dt = Column(DateTime)
    updated_by = Column(String)
    is_inactive = Column(String, default='N')
    is_delete = Column(String, default='N')