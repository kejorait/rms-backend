import datetime as dt

from fastapi.responses import JSONResponse

from helper import constants
from models.bill import Bill
from models.bill_dtl import BillDtl
from models.menu import Menu
from models.table import Table
from models.waiting_list import WaitingList
from utils.tinylog import getLogger, setupLog


class BillService:
    name = "bill"
    setupLog(serviceName=__file__)

    def __init__(self):
        self.log = getLogger(serviceName=__file__)

    # Create Bill
    def addBill(self, request, db):
        jsonStr = {}

        try:
            bill = Bill()
            bill.cd = request.cd
            bill.table_cd = request.table_cd
            bill.created_dt = dt.datetime.now()
            bill.created_by = request.created_by
            bill.is_inactive = constants.NO
            bill.is_delete = constants.NO
            bill.is_closed = constants.NO
            bill.is_paid = constants.NO
            bill.user_nm = request.user_nm

            db.add(bill)
            db.commit()

            jsonStr["data"] = constants.STATUS_SUCCESS
            jsonStr["isError"] = constants.NO
            jsonStr["status"] = "Success"

        except Exception as ex:
            self.log.error(ex)
            response = JSONResponse(status_code=500, content={"data": str(ex), "isError": constants.YES, "status": constants.STATUS_FAILED})
            return response
        # self.log.info("Response " + str(jsonStr))

        return jsonStr

    # Update Bill
    def updateBill(self, request, db):
        jsonStr = {}
        try:
            # self.log.info("Response "+str(jsonStr))

            cd = request.cd
            bill = db.query(Bill).get(cd)
            bill.table_cd = request.table_cd
            bill.user_nm = request.user_nm
            bill.moved_by = request.moved_by
            bill.moved_dt = dt.datetime.now()

            db.commit()

            jsonStr["data"] = constants.STATUS_SUCCESS
            jsonStr["isError"] = constants.NO
            jsonStr["status"] = "Success"

        except Exception as ex:
            self.log.exception(" BillService")
            jsonStr["isError"] = constants.YES
            jsonStr["status"] = "Failed"
            return jsonStr, 500
        # self.log.info("Response " + str(jsonStr))
        return jsonStr

    # Delete Bill
    def deleteBill(self, request, db):
        jsonStr = {}
        try:
            # self.log.info("Response "+str(jsonStr))
            cd = request.cd
            bill = db.query(Bill).get(cd)
            bill.is_delete = "Y"

            db.commit()

            jsonStr["data"] = constants.STATUS_SUCCESS
            jsonStr["isError"] = constants.NO
            jsonStr["status"] = "Success"

        except Exception as ex:
            self.log.exception(" BillService")
            jsonStr["isError"] = constants.YES
            jsonStr["status"] = "Failed"
            return jsonStr, 500
        # self.log.info("Response " + str(jsonStr))
        return jsonStr

    # Close Bill
    def closeBill(self, request, db):
        jsonStr = {}
        try:
            # self.log.info("Response "+str(jsonStr))
            cd = request.cd
            bill = db.query(Bill).get(cd)
            bill.closed_by = request.closed_by
            bill.closed_dt = dt.datetime.now()
            bill.is_closed = constants.YES

            db.commit()

            jsonStr["data"] = constants.STATUS_SUCCESS
            jsonStr["isError"] = constants.NO
            jsonStr["status"] = "Success"

        except Exception as ex:
            self.log.exception(" BillService")
            jsonStr["isError"] = constants.YES
            jsonStr["status"] = "Failed"
            return jsonStr, 500
        # self.log.info("Response " + str(jsonStr))
        return jsonStr

    # Paid Bill
    def paidBill(self, request, db):
        jsonStr = {}
        try:
            # self.log.info("Response "+str(jsonStr))
            cd = request.cd
            bill = db.query(Bill).get(cd)
            bill.paid_type = request.paid_type
            bill.paid_amount = request.paid_amount
            bill.bill_total = request.bill_total
            bill.paid_change = request.bill_total - request.paid_amount
            bill.is_paid = constants.YES
            bill.paid_by = request.paid_by
            bill.paid_dt = dt.datetime.now()

            db.commit()

            jsonStr["data"] = {
                "paid_change": bill.paid_change
            }
            jsonStr["isError"] = constants.NO
            jsonStr["status"] = "Success"

        except Exception as ex:
            self.log.exception(" BillService")
            jsonStr["isError"] = constants.YES
            jsonStr["status"] = "Failed"
            return jsonStr, 500
        # self.log.info("Response " + str(jsonStr))
        return jsonStr

    # Get Bill Detail
    def getBillSummary(self, request, db):
        waiting_list = False
        jsonStr = {}
        try:
            # self.log.info("Response "+str(jsonStr))
            from_dt = request.from_dt
            to_dt = request.to_dt

            query = db.query(Bill, Table.nm.label("table_nm"))
            query = query.join(Table, Table.cd == Bill.table_cd)
            query = query.join(BillDtl, BillDtl.bill_cd == Bill.cd)
            query = query.filter(Bill.created_dt >= from_dt)
            query = query.filter(Bill.created_dt <= to_dt)
            query = query.order_by(Bill.created_dt.desc())
            # self.log.info(query.statement.compile(compile_kwargs={"literal_binds": True}))
            row = query.all()
            query = db.query(Bill, WaitingList.nm.label("table_nm"))
            query = query.join(WaitingList, WaitingList.cd == Bill.table_cd)
            query = query.join(BillDtl, BillDtl.bill_cd == Bill.cd)
            query = query.filter(Bill.created_dt >= from_dt)
            query = query.filter(Bill.created_dt <= to_dt)
            query = query.order_by(Bill.created_dt.desc())
            row_wl = query.all()
            total_row = row_wl + row
            # self.log.info(query.statement.compile(compile_kwargs={"literal_binds": True}))
            db.close()
            listData = []
            subtotal = 0
            for mdl in total_row:
                data = {}
                if "TABLE" not in mdl.table_nm:
                    data["table_nm"] = "Waiting List - " + mdl.table_nm
                else:
                    data["table_nm"] = mdl.table_nm + " - " + mdl.Bill.user_nm
                data["bill_dt"] = mdl.Bill.created_dt
                data["bill_cd"] = mdl.Bill.cd
                query = db.query(BillDtl.qty, BillDtl.price).select_from(BillDtl)
                query = query.join(Menu, Menu.cd == BillDtl.menu_cd)
                query = query.filter(BillDtl.bill_cd == mdl.Bill.cd)
                # self.log.info(query.statement.compile(compile_kwargs={"literal_binds": True}))
                bill_dtl = query.all()
                self.log.info(bill_dtl)
                totalData = 0
                for mdl in bill_dtl:
                    if mdl.qty > 0:
                        totalData += float(mdl.price * mdl.qty)
                data["total"] = totalData
                subtotal += totalData
                listData.append(data)
            res = {}

            listData.sort(key=lambda x: x["bill_dt"], reverse=True)
            res["data"] = listData
            res["subtotal"] = subtotal
            res["service"] = subtotal * 0.05
            res["pb1"] = (subtotal + subtotal * 0.05) * 0.1
            res["total"] = (
                (subtotal + subtotal * 0.05) * 0.1 + subtotal * 0.05 + subtotal
            )
            # jsonStr = json.dumps(res, default=str)
            jsonStr = res
        except Exception as ex:
            self.log.exception(" BillDtlService")
            jsonStr["isError"] = constants.YES
            jsonStr["status"] = "Failed"

            return jsonStr, 500
        # self.log.info("Response " + str(jsonStr))
        return jsonStr
