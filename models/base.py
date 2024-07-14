import datetime
import decimal
from sqlalchemy import (
     DECIMAL, Column, DateTime, ForeignKey, Integer, String, BigInteger
)
from sqlalchemy.ext.declarative import declarative_base

from helper.helper import datetimeToUTCLongJS
SAINSTANCE = '_sa_instance_state'
DATEFIELDS = "created_dt;updated_dt;logout_dt;login_dt;actn_dt;log_dt;log_last_upd_dt;paid_dt;closed_dt;"

class Base(object):
    # created_dt = Column(
    #     DateTime,
    #     nullable=True
    # )
    # created_by = Column(
    #     String,
    #     nullable=True
    # )

    def toDict(self):
       m = {}
       for key, val in self.__dict__.items():
           if (key == SAINSTANCE):
              continue
           elif (isinstance(val, decimal.Decimal)):
              fval = float(val)
              m[key] = (fval if fval % 1 else int(fval))
           elif (isinstance(val, datetime.datetime)):
               m[key] = datetimeToUTCLongJS(val) if (val) else None
           elif (isinstance(val, list)):
              m[key] = self.listParse(val)
           elif ('toDict' in dir(val)):
              m[key] = val.toDict()
           else:
              m[key] = val
       return m
    

DeclarativeOrigin = declarative_base(cls=Base)
