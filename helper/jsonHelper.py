import decimal
import json
import datetime
from decimal import Decimal

from sqlalchemy import inspect
from sqlalchemy.engine import Row

from helper import constants
from helper.helper import datetimeToLongJS


class ExtendEncoder(json.JSONEncoder):
    def default(self, o, *args, **kw):
        if "toDict" in dir(o):
            return o.toDict()
        elif isinstance(o, decimal.Decimal):
            fval = float(o)
            tmpo = fval if fval % 1 else int(fval)
            return tmpo
        elif isinstance(o, Row):
            ndict = {}
            for n in o.keys():
                ndict[n] = o[n]
            return ndict
        elif isinstance(o, datetime.datetime):
            return datetimeToLongJS(o)

        return super(ExtendEncoder, self).default(o, *args, **kw)

    def objToJson(self, o):
        res = dict(o.__dict__)
        res.pop("_sa_instance_state", None)
        return res

    def to_dict(self, obj, with_relationships=True):
        d = {}
        for column in obj.__table__.columns:
            if with_relationships and len(column.foreign_keys) > 0:
                # Skip foreign keys
                continue
            d[column.name] = getattr(obj, column.name)

        if with_relationships:
            for relationship in inspect(type(obj)).relationships:
                val = getattr(obj, relationship.key)
                d[relationship.key] = self.to_dict(val) if val else None
        return d
