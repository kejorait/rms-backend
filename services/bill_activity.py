import datetime as dt
import math

from fastapi.responses import JSONResponse

from helper import constants
from models.app_setting import AppSetting
from models.bill import Bill
from models.bill_dtl import BillDtl
from models.table import Table
from models.table_session import TableSession
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
                Bill, Table.nm.label("table_nm"), WaitingList.nm.label("waiting_nm"), Table.is_billiard.label("is_billiard")
            )
            query = query.join(Table, Table.cd == Bill.table_cd, isouter=True)
            query = query.join(
                WaitingList, WaitingList.cd == Bill.table_cd, isouter=True
            )
            query = query.join(BillDtl, BillDtl.bill_cd == Bill.cd, isouter=True)
            # from_dt_utc = ensure_utc(request.from_dt)
            # to_dt_utc = ensure_utc(request.to_dt)
            from_dt_utc = dt.datetime.fromtimestamp(from_dt)
            to_dt_utc = dt.datetime.fromtimestamp(to_dt)
            query = query.filter(Bill.is_paid == constants.YES)
            query = query.filter(Bill.is_delete == constants.NO)
            query = query.filter(Bill.created_dt >= from_dt_utc)
            query = query.filter(Bill.created_dt <= to_dt_utc)
            query = query.order_by(Bill.created_dt.desc())
            # print(query.statement.compile(compile_kwargs={"literal_binds": True}))
            row = query.all()
            listData = []
            subtotal = 0
            billiard_total = 0
            bill_total = 0
            for mdl in row:
                data = {}
                data["dsc_billiard_total"] = 0
                data["dsc_bill_total"] = 0
                if mdl.waiting_nm:
                    data["table_nm"] = (
                        "Waiting List - " + mdl.table_nm if mdl.table_nm else ""
                    )
                    data["is_billiard"] = constants.NO
                else:
                    data["table_nm"] = (
                        mdl.table_nm
                        if mdl.table_nm
                        else "" + " - " + mdl.Bill.user_nm if mdl.Bill.user_nm else ""
                    )
                    data["is_billiard"] = mdl.is_billiard
                data["bill_dt"] = mdl.Bill.created_dt
                bill_cd = mdl.Bill.cd
                data["bill_cd"] = bill_cd
                dsc_billiard_subtotal = float(
                    mdl.Bill.dsc_billiard_subtotal
                    if mdl.Bill.dsc_billiard_subtotal
                    else 0
                )
                dsc_bill_subtotal = float(
                    mdl.Bill.dsc_bill_subtotal if mdl.Bill.dsc_bill_subtotal else 0
                )
                pb1_bl = float(mdl.Bill.pb1_bl if mdl.Bill.pb1_bl else 0)
                service_bl = float(mdl.Bill.service_bl if mdl.Bill.service_bl else 0)
                pb1 = float(mdl.Bill.pb1 if mdl.Bill.pb1 else 0)
                service = float(mdl.Bill.service if mdl.Bill.service else 0)
                dsc_billiard_total = (dsc_billiard_subtotal * pb1_bl / 100) + (
                    dsc_billiard_subtotal * service_bl / 100
                ) + dsc_billiard_subtotal

                # Calculate bill discount and service total
                dsc_bill_total = (dsc_bill_subtotal * pb1 / 100) + (
                    dsc_bill_subtotal * service / 100
                ) + dsc_bill_subtotal
                data["billiard_total"] = (
                    mdl.Bill.billiard_total if mdl.Bill.billiard_total else 0
                )
                data["dsc_billiard"] = (
                    mdl.Bill.billiard_discount if mdl.Bill.billiard_discount else 0
                )
                data["dsc_billiard_subtotal"] = dsc_billiard_subtotal
                data["dsc_billiard_total"] = dsc_billiard_total
                data["bill_total"] = mdl.Bill.bill_total if mdl.Bill.bill_total else 0
                data["dsc_bill"] = (
                    mdl.Bill.bill_discount if mdl.Bill.bill_discount else 0
                )
                data["dsc_bill_subtotal"] = dsc_bill_subtotal
                data["dsc_bill_total"] = dsc_bill_total
                data["pb1_bl"] = pb1_bl
                data["service_bl"] = service_bl
                data["pb1"] = pb1
                data["service"] = service
                grand_total = dsc_billiard_total + dsc_bill_total
                if grand_total == 0:
                    billiard_sub = float(data["billiard_total"] - data["dsc_billiard"])
                    bill_sub = float(data["bill_total"] - data["dsc_bill"])
                    billiard_tot = (
                        billiard_sub * pb1_bl / 100
                        + billiard_sub * service_bl / 100
                        + billiard_sub
                    )
                    bill_tot = (
                        bill_sub * pb1 / 100
                        + bill_sub * service / 100
                        + bill_sub
                    )
                    grand_total = billiard_tot + bill_tot
                    data["dsc_bill_total"] = bill_tot
                    data["dsc_billiard_total"] = billiard_tot
                data["grand_total"] = grand_total
                data["total"] = grand_total
                data["user_nm"] = mdl.Bill.user_nm if mdl.Bill.user_nm else ""
                subtotal += data["total"]
                # Fetch table session details
                table_session_query = (
                    db.query(
                        TableSession.created_dt.label("session_created_dt"),
                        TableSession.amount.label("session_amount"),
                        TableSession.is_open.label("session_is_open"),
                        TableSession.is_closed.label("session_is_closed"),
                        TableSession.closed_dt,
                        TableSession.interval,
                        TableSession.price,
                    )
                    .filter(
                        TableSession.is_inactive == constants.NO,
                        TableSession.is_delete == constants.NO,
                        TableSession.bill_cd == bill_cd,
                    )
                    .order_by(TableSession.created_dt.desc())
                )

                # self.log.info(table_session_query.statement.compile(compile_kwargs={"literal_binds": True}))
                table_session = table_session_query.all()

                # Initialize `data_list` to store results and determine session status
                data_list = {}
                data_list["total_open"] = 0
                data_list["session_amount"] = 0
                data_list["billiard_total"] = 0
                data_list["minutes_total"] = 0
                sessionList = []
                if table_session:
                    for tbs in table_session:
                        session_list = {}
                        session_list["price_per_interval"] = tbs.price
                        session_list["time_interval"] = tbs.interval
                        if tbs.session_is_open == constants.YES:
                            session_list["session_status"] = "OPEN"
                        elif tbs.session_is_open == constants.NO:
                            session_list["session_status"] = "FIXED"
                        else:
                            session_list["session_status"] = (
                                "CLOSED"  # In case no conditions match
                            )
                        session_list["session_amount"] = tbs.session_amount
                        session_list["current_open"] = None
                        session_list["subtotal"] = 0
                        session_list["minutes"] = 0
                        if tbs.session_is_open == constants.YES:
                            if tbs.session_is_closed == constants.YES:
                                current_open = round(
                                    (
                                        tbs.closed_dt - tbs.session_created_dt
                                    ).total_seconds()
                                )
                                data_list["total_open"] += current_open
                                session_list["current_open"] = current_open
                                session_list["session_created_dt"] = (
                                    tbs.session_created_dt
                                )
                                session_list["session_closed_dt"] = tbs.closed_dt
                                minutes = current_open / 60
                                session_list["minutes"] = 1 if minutes <= 1 else minutes
                                time_interval = tbs.interval if tbs.interval else 1
                                price_per_interval = tbs.price if tbs.price else 1
                                round_value = math.ceil(minutes)
                                result = (
                                    round_value * price_per_interval / time_interval
                                )
                                session_price = round(result)
                                session_list["subtotal"] += result
                                data_list["billiard_total"] += session_price

                        if tbs.session_is_open == constants.NO:
                            if tbs.session_is_closed == constants.YES:
                                session_list["session_created_dt"] = (
                                    tbs.session_created_dt
                                )
                                session_list["session_closed_dt"] = tbs.closed_dt
                            data_list["session_amount"] += tbs.session_amount
                            minutes = tbs.session_amount / 60
                            session_list["minutes"] = 1 if minutes <= 1 else minutes
                            time_interval = tbs.interval if tbs.interval else 1
                            price_per_interval = tbs.price if tbs.price else 1
                            round_value = math.ceil(
                                minutes / time_interval
                            )  # Rounds up to 26
                            result = round_value * price_per_interval
                            session_price = result
                            session_list["subtotal"] += session_price
                            data_list["billiard_total"] += session_price

                        if session_list:
                            data_list["minutes_total"] += session_list["minutes"]
                            sessionList.append(session_list)

                    # Assign query results to `data_list`
                    data_list["session_created_dt"] = table_session[
                        0
                    ].session_created_dt
                    # data_list["session_amount"] = table_session.session_amount
                    data_list["sessions"] = sessionList
                    data_list["session_is_open"] = table_session[0].session_is_open
                    data_list["session_is_closed"] = table_session[0].session_is_closed
                    data_list["session_closed_dt"] = table_session[0].closed_dt
                billiard_total += data["dsc_billiard_total"]
                bill_total += data["dsc_bill_total"]
                data.update(data_list)
                listData.append(data)
            res = {}

            listData.sort(key=lambda x: x["bill_dt"], reverse=True)
            res["data"] = listData
            subtotal = float(subtotal)
            # res["subtotal"] = subtotal
            # res["service"] = subtotal * 0.05
            # res["pb1"] = (subtotal + subtotal * 0.05) * 0.1'
            res["billiard_total"] = billiard_total
            res["bill_total"] = bill_total
            res["total"] = bill_total + billiard_total
            # jsonStr = json.dumps(res, default=str)
            jsonStr = res
        except Exception as ex:
            self.log.exception(" BillDtlService")
            jsonStr["isError"] = constants.YES
            jsonStr["status"] = "Failed"

            return jsonStr, 500
        # self.log.info("Response " + str(jsonStr))
        return jsonStr
