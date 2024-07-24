   
from fastapi import Depends

from helper.helper import get_pagination, paginate
from services.stock_activity import StockService


class StockController:
    def __init__(self):
        self.pagination = Depends(get_pagination)
        # self.log.info(" init  StockService ")

    name = "StockController"
    def getStockAll(self, request, db, pagination: dict, sort_by: str, sort_order: str):
        res = StockService().getStockAll(request, db, sort_by, sort_order)
        paginated_data = paginate(res, pagination)
        return paginated_data
