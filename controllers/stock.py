from fastapi import Depends
from fastapi.responses import JSONResponse

from helper import constants
from helper.helper import get_pagination, paginate
from services.stock_activity import StockService


class StockController:
    def __init__(self):
        self.pagination = Depends(get_pagination)
        # self.log.info(" init  StockService ")

    name = "StockController"

    def getStockAll(self, request, db, pagination: dict, sort_by: str, sort_order: str):
        try:
            res = StockService().getStockAll(request, db, sort_by, sort_order)
            paginated_data = paginate(
                res, pagination, constants.STATUS_SUCCESS, constants.NO
            )
        except Exception as ex:
            paginated_data = JSONResponse(
                status_code=500,
                content={
                    "data": str(ex),
                    "isError": constants.YES,
                    "status": constants.STATUS_FAILED,
                },
            )
        return paginated_data
