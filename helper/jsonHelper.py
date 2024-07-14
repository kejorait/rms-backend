import decimal
import json
import datetime
from decimal import Decimal

from sqlalchemy.engine import Row

from helper import constants
from helper.helper import datetimeToLongJS

class ExtendEncoder(json.JSONEncoder):
    def default(self, o, *args, **kw):
        if ('toDict' in dir(o)):
            return o.toDict()
        elif (isinstance(o, decimal.Decimal)):
            fval = float(o)
            tmpo = (fval if fval % 1 else int(fval))
            return tmpo
        elif (isinstance(o, Row)):
            ndict = {}
            for n in o.keys():
                ndict[n] = o[n]
            return ndict
        elif (isinstance(o, datetime.datetime)):
            return datetimeToLongJS(o)

        return super(ExtendEncoder, self).default(o, *args, **kw)
