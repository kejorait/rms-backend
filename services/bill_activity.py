import datetime as dt

from fastapi.responses import JSONResponse

from helper import constants
from models.app_setting import AppSetting
from models.bill import Bill
from models.table_session import TableSession
from services.sm.bill_dtl_activity import SmBillDtl
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
            response = JSONResponse(
                status_code=500,
                content={
                    "data": str(ex),
                    "isError": constants.YES,
                    "status": constants.STATUS_FAILED,
                },
            )
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
        # try:
        # self.log.info("Response "+str(jsonStr))
        cd = request.cd

        bill = db.query(Bill).get(cd)

        bill.bill_total = request.bill_total if request.bill_total else 0

        bill.billiard_is_paid = constants.YES
        bill.billiard_closed_dt = request.closed_dt
        bill.billiard_total = request.billiard_total if request.billiard_total else 0
        bill.billiard_price = request.price
        bill.billiard_paid_dt = dt.datetime.now()
        bill.biliard_paid_by = request.paid_by

        bill.paid_type = request.paid_type
        bill.paid_amount = request.paid_amount
        bill.is_paid = constants.YES
        bill.paid_by = request.paid_by
        dsc_billiard_subtotal = float(
            request.billiard_total if request.billiard_total else 0
        ) - float(bill.billiard_discount if bill.billiard_discount else 0)
        dsc_bill_subtotal = float(
            request.bill_total if request.bill_total else 0
        ) - float(bill.bill_discount if bill.bill_discount else 0)

        bill.dsc_billiard_subtotal = dsc_billiard_subtotal
        bill.dsc_bill_subtotal = dsc_bill_subtotal

        query = db.query(AppSetting)
        query = query.filter(AppSetting.is_delete == constants.NO)
        query = query.filter(AppSetting.is_inactive == constants.NO)
        data = query.all()

        data_settings = {setting.cd: setting.value for setting in data}

        if data_settings["pb1_bl"] == "":
            data_settings["pb1_bl"] = 0
        if data_settings["service_bl"] == "":
            data_settings["service_bl"] = 0
        if data_settings["pb1"] == "":
            data_settings["pb1"] = 0
        if data_settings["service"] == "":
            data_settings["service"] = 0

        # Ensure data settings are converted to floats for percentage calculations
        data_settings["pb1_bl"] = float(data_settings["pb1_bl"])
        data_settings["service_bl"] = float(data_settings["service_bl"])
        data_settings["pb1"] = float(data_settings["pb1"])
        data_settings["service"] = float(data_settings["service"])

        # Calculate billiard discount and service total
        dsc_billiard_total = (
            (dsc_billiard_subtotal * data_settings["pb1_bl"] / 100)
            + (dsc_billiard_subtotal * data_settings["service_bl"] / 100)
            + dsc_billiard_subtotal
        )

        # Calculate bill discount and service total
        dsc_bill_total = (
            (dsc_bill_subtotal * data_settings["pb1"] / 100)
            + (dsc_bill_subtotal * data_settings["service"] / 100)
            + dsc_bill_subtotal
        )

        # Calculate grand total
        bill.grand_total = round(dsc_bill_total + dsc_billiard_total)

        bill.paid_change = bill.grand_total - request.paid_amount
        bill.paid_dt = dt.datetime.now()

        query = db.query(TableSession.cd).filter(TableSession.bill_cd == cd)
        table_session = query.all()

        for tbs in table_session:
            query = db.query(TableSession).get(tbs.cd)
            query.is_paid = constants.YES

        db.commit()

        jsonStr["data"] = {"paid_change": bill.paid_change}
        jsonStr["isError"] = constants.NO
        jsonStr["status"] = "Success"

        # except Exception as ex:
        #     self.log.exception(" BillService")
        #     jsonStr["isError"] = constants.YES
        #     jsonStr["status"] = "Failed"
        #     return jsonStr, 500
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

            query = db.query(
                Bill.cd
            )
            from_dt_utc = dt.datetime.fromtimestamp(from_dt)
            to_dt_utc = dt.datetime.fromtimestamp(to_dt)
            query = query.filter(Bill.is_paid == constants.YES)
            query = query.filter(Bill.is_delete == constants.NO)
            query = query.filter(Bill.created_dt >= from_dt_utc)
            query = query.filter(Bill.created_dt <= to_dt_utc)
            query = query.order_by(Bill.created_dt.desc())
            # print(query.statement.compile(compile_kwargs={"literal_binds": True}))
            row = query.all()
            cds = []
            for mdl in row:
                cds.append(mdl)
            cds = list(set(cds))
            listData = []
            grand_total = 0
            dsc_billiard_total = 0
            dsc_bill_total = 0
            for mdl in cds:
                data = {}
                detail = SmBillDtl.getBillDtl(SmBillDtl, mdl.cd, db, "bill")
                if detail:
                    if "data" in detail:
                        data = detail["data"]
                        data["data"] = None
                        data["dsc_billiard_total"] = 0
                        data["bill_dt"] = data["created_dt"]
                        if "bill_dt" in data:
                            data["session_created_dt"] = data["bill_dt"]
                        if "table_session" in data:
                            if "closed_dt" in data["table_session"]:
                                data["session_closed_dt"] = data["table_session"]["closed_dt"]
                            if "minutes_total" in data["table_session"]:
                                data["minutes_total"] = data["table_session"]["minutes_total"]
                            if "session_created_dt" in data["table_session"]:
                                data["session_created_dt"] = data["table_session"]["session_created_dt"]
                            if "dsc_billiard_total" in data["table_session"]:
                                dsc_billiard_total_detail = data["table_session"]["dsc_billiard_total"]
                                data["dsc_billiard_total"] = dsc_billiard_total_detail
                                dsc_billiard_total += dsc_billiard_total_detail
                        if "bill_cd" in detail["data"]:
                            bill_cd = detail["data"]["bill_cd"]
                            data["bill_cd"] = bill_cd
                        if "dsc_bill_total" in detail["data"]:
                            dsc_bill_total_detail = detail["data"]["dsc_bill_total"]
                            data["dsc_bill_total"] = dsc_bill_total_detail
                            dsc_bill_total += dsc_bill_total_detail
                        if "grand_total" in detail["data"]:
                            grand_total_detail = detail["data"]["grand_total"]
                            data["grand_total"] = grand_total_detail
                            data["total"] = grand_total_detail
                            grand_total += grand_total_detail
                listData.append(data)
            res = {}

            listData.sort(key=lambda x: x["bill_dt"], reverse=True)
            res["data"] = listData
            res["billiard_total"] = dsc_billiard_total
            res["bill_total"] = dsc_bill_total
            res["total"] = grand_total
            # jsonStr = json.dumps(res, default=str)
            jsonStr = res
        except Exception as ex:
            self.log.exception(" BillDtlService")
            jsonStr["isError"] = constants.YES
            jsonStr["status"] = "Failed"

            return jsonStr, 500
        # self.log.info("Response " + str(jsonStr))
        return jsonStr
