import math
from collections import defaultdict
from datetime import datetime

from sqlalchemy import not_

from helper import constants
from models.app_setting import AppSetting
from models.bill import Bill
from models.bill_dtl import BillDtl
from models.menu import Menu
from models.table import Table
from models.table_session import TableSession
from models.user import User
from models.waiting_list import WaitingList
from utils.tinylog import getLogger


class SmBillDtl:

    def __init__(self):
        self.log = getLogger(serviceName=__file__)

    def getBillDtl(self, cd, db, type):
        jsonStr = {"status": "Success", "isError": constants.NO}
        table_cd = None
        bill_cd = None
        if type == "table":
            table_cd = cd
        if type == "bill":
            bill_cd = cd
        res = {"table_session": "", "subtotal": 0}
        waiting_list = False

        # try:
        # Fetch initial bill details
        query = db.query(
            Bill.cd,
            Bill.is_closed,
            Bill.is_paid,
            Bill.user_nm,
            Bill.created_by,
            Bill.table_cd,
            Bill.paid_type,
            Bill.paid_amount,
            Bill.billiard_total,
            Bill.billiard_discount,
            Bill.pb1,
            Bill.pb1_bl.label("pb1_bl"),
            Bill.service,
            Bill.service_bl.label("service_bl"),
            Bill.bill_discount,
            Bill.bill_total,
        )
        query = query.filter(
            Bill.is_delete == constants.NO, Bill.is_inactive == constants.NO
        )
        if bill_cd:
            query = query.filter(Bill.cd == bill_cd)
        if table_cd:
            query = query.filter(Bill.table_cd == table_cd)
            query = query.filter(Bill.is_paid == constants.NO)
            query = query.filter(not_(Bill.user_nm.ilike("%Split%")))

        query = query.order_by(Bill.created_dt.desc())
        # self.log.info(query.statement.compile(compile_kwargs={"literal_binds": True}))
        bill = query.first()

        if bill:
            bill_cd = bill.cd
            table_cd = bill.table_cd
            bill_discount = bill.bill_discount
            res["bill_discount"] = bill_discount
            billiard_discount = bill.billiard_discount
            res["billiard_discount"] = billiard_discount

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
                    TableSession.table_cd == table_cd,
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
                                (tbs.closed_dt - tbs.session_created_dt).total_seconds()
                            )
                            data_list["total_open"] += current_open
                            session_list["current_open"] = current_open
                            session_list["session_created_dt"] = tbs.session_created_dt
                            session_list["session_closed_dt"] = tbs.closed_dt
                            minutes = current_open / 60
                            session_list["minutes"] = 1 if minutes <= 1 else minutes
                            time_interval = tbs.interval if tbs.interval else 1
                            price_per_interval = tbs.price if tbs.price else 1
                            round_value = math.ceil(minutes)
                            result = round_value * price_per_interval / time_interval
                            session_price = round(result)
                            session_list["subtotal"] += result
                            data_list["billiard_total"] += session_price

                    if tbs.session_is_open == constants.NO:
                        if tbs.session_is_closed == constants.YES:
                            session_list["session_created_dt"] = tbs.session_created_dt
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
                data_list["session_created_dt"] = table_session[0].session_created_dt
                # data_list["session_amount"] = table_session.session_amount
                data_list["sessions"] = sessionList
                data_list["session_is_open"] = table_session[0].session_is_open
                data_list["session_is_closed"] = table_session[0].session_is_closed
                data_list["closed_dt"] = table_session[0].closed_dt

                # Add logic for determining `session_status`
                if table_session[0].session_is_open == constants.YES:
                    session_status = "OPEN"
                elif table_session[0].session_is_open == constants.NO:
                    session_status = "FIXED"
                else:
                    session_status = "CLOSED"  # In case no conditions match

                # Add `session_status` to `data_list`
                data_list["session_status"] = session_status

            res["table_session"] = data_list

        # Close the session and fetch main query details
        db.close()

        # Main bill detail query for menu items
        bill_dtl_query = (
            db.query(
                Table.cd,
                Table.nm.label("table_nm"),
                BillDtl,
                BillDtl.price,
                BillDtl.discount,
                Menu.nm.label("menu_nm"),
                Menu.img,
                Bill.user_nm,
            )
            .join(Menu, Menu.cd == BillDtl.menu_cd)
            .join(Bill, Bill.cd == BillDtl.bill_cd)
            .join(Table, Table.cd == Bill.table_cd)
            .filter(BillDtl.qty > 0)
            .order_by(BillDtl.created_dt.asc())
        )

        if bill_cd:
            bill_dtl_query = bill_dtl_query.filter(Bill.cd == bill_cd)

        data = bill_dtl_query.all()
        db.close()

        listData = []
        for mdl in data:
            if mdl.BillDtl.qty > 0:
                data_list = {
                    "cd": mdl.BillDtl.cd,
                    "bill_cd": mdl.BillDtl.bill_cd,
                    "created_dt": datetime.timestamp(mdl.BillDtl.created_dt),
                    "created_by": mdl.BillDtl.created_by,
                    "is_inactive": mdl.BillDtl.is_inactive,
                    "is_delete": mdl.BillDtl.is_delete,
                    "process_status": mdl.BillDtl.process_status,
                    "menu_cd": mdl.BillDtl.menu_cd,
                    "user_nm": mdl.BillDtl.user_nm,
                    "menu_nm": mdl.menu_nm,
                    "menu_img": mdl.img,
                    "qty": mdl.BillDtl.qty,
                    "desc": mdl.BillDtl.desc,
                    "split_qty": mdl.BillDtl.split_qty,
                    "init_qty": mdl.BillDtl.init_qty,
                    "updated_dt": mdl.BillDtl.updated_dt,
                    "price": mdl.price,
                    "discount": mdl.discount,
                    "price_discount": mdl.price - mdl.discount,
                    "total": (mdl.price - mdl.discount) * mdl.BillDtl.qty,
                }
                res["subtotal"] += data_list["total"]
                listData.append(data_list)

        # Calculate additional charges and set bill status
        query = db.query(AppSetting)
        query = query.filter(AppSetting.is_delete == constants.NO)
        query = query.filter(AppSetting.is_inactive == constants.NO)
        data = query.all()

        data_settings = {setting.cd: setting.value for setting in data}

        service = (
            bill.service
            if bill and bill.service is not None
            else data_settings.get("service", 0)
        )
        # res["pb1"] = res["subtotal"] * float(pb1) / 100
        # res["service"] = res["subtotal"] * float(service) / 100

        # res["total"] = res["subtotal"] + res["pb1"] + res["service"]
        if bill:
            bill_total = res["subtotal"]
            pb1 = data_settings["pb1"]
            if bill.pb1:
                if bill.pb1 != '':
                    pb1 = bill.pb1
            service = data_settings["service"]
            if bill.service:
                if bill.service != '':
                    service = bill.service
            if pb1 == '':
                pb1 = 0
            if service == '':
                service = 0
            bill_total = float(bill_total)
            pb1 = float(pb1)
            service = float(service)
            bill_discount = bill.bill_discount or 0
            bill_discount = float(bill_discount)
            res["dsc_bill_subtotal"] = bill_total - bill_discount
            res["pb1"] = pb1 * res["dsc_bill_subtotal"] / 100
            res["service"] = service * res["dsc_bill_subtotal"] / 100
            res["dsc_bill_total"] = (
                res["dsc_bill_subtotal"] + res["pb1"] + res["service"]
            )
            res["dsc_bill_total"] = float(res["dsc_bill_total"])

        if bill:

            if bill.is_closed == constants.NO and bill.is_paid == constants.YES:
                status = "EMPTY"
            elif bill.is_closed == constants.YES and bill.is_paid == constants.NO:
                status = "CLOSED"
            else:
                status = "OCCUPIED"
        else:
            status = "EMPTY"

        res["bill_status"] = status

        # Fetch table name or handle waiting list
        table_name_query = (
            db.query(Table.nm, Table.is_billiard).filter(Table.cd == table_cd).first()
        )
        if table_name_query:
            res["table_nm"] = table_name_query.nm
            res["table_cd"] = table_cd
            res["is_billiard"] = table_name_query.is_billiard
        else:
            waiting_list = True
            waiting_query = (
                db.query(
                    WaitingList.cd,
                    WaitingList.nm.label("table_nm"),
                    BillDtl,
                    Menu.price,
                    Menu.nm.label("menu_nm"),
                    Menu.img,
                    Bill.user_nm,
                )
                .join(Menu, Menu.cd == BillDtl.menu_cd)
                .join(Bill, Bill.cd == BillDtl.bill_cd)
                .join(WaitingList, WaitingList.cd == Bill.table_cd)
                .filter(Bill.cd == bill_cd)
                .order_by(BillDtl.created_dt.asc())
            )
            waiting_data = waiting_query.all()
            db.close()

            if waiting_data:
                res["table_nm"] = (
                    "Waiting List - " + waiting_data[0].table_nm if waiting_list else ""
                )
                listData = [
                    {
                        "cd": mdl.BillDtl.cd,
                        "bill_cd": mdl.BillDtl.bill_cd,
                        "created_dt": datetime.timestamp(mdl.BillDtl.created_dt),
                        "created_by": mdl.BillDtl.created_by,
                        "is_inactive": mdl.BillDtl.is_inactive,
                        "is_delete": mdl.BillDtl.is_delete,
                        "process_status": mdl.BillDtl.process_status,
                        "menu_cd": mdl.BillDtl.menu_cd,
                        "user_nm": mdl.BillDtl.user_nm,
                        "menu_nm": mdl.menu_nm,
                        "menu_img": mdl.img,
                        "qty": mdl.BillDtl.qty,
                        "desc": mdl.BillDtl.desc,
                        "split_qty": mdl.BillDtl.qty - mdl.BillDtl.split_qty,
                        "updated_dt": mdl.BillDtl.updated_dt,
                        "price": mdl.price,
                        "total": mdl.price * mdl.BillDtl.qty,
                    }
                    for mdl in waiting_data
                    if mdl.BillDtl.qty > 0
                ]

        # Final response composition
        if bill:
            serviced_by = db.query(User.name).filter(User.cd == bill.created_by).first()
            res["serviced_by"] = serviced_by.name
            res["user_nm"] = bill.user_nm
            res["bill_cd"] = bill.cd
            res["paid_type"] = bill.paid_type
            res["paid_amount"] = bill.paid_amount

            billiard_total = 0
            if "table_session" in res:
                if "billiard_total" in res["table_session"]:
                    billiard_total = res["table_session"]["billiard_total"]

            billiard_discount = bill.billiard_discount if bill.billiard_discount else 0
            billiard_discount = float(billiard_discount)

            res["dsc_billiard_subtotal"] = billiard_total - billiard_discount
            res["dsc_billiard_subtotal"] = float(res["dsc_billiard_subtotal"])

            res["table_session"]["dsc_billiard_total"] = res["dsc_billiard_subtotal"]

            service_bl = data_settings["service_bl"]
            if bill.service_bl:
                if bill.service_bl != '':
                    service_bl = bill.service_bl
            pb1_bl = data_settings["pb1_bl"]
            if bill.pb1_bl:
                if bill.pb1_bl != '':
                    pb1_bl = bill.pb1_bl
            if pb1_bl == '':
                pb1_bl = 0
            if service_bl == '':
                service_bl = 0
            res["table_session"]["pb1_bl"] = (
                res["dsc_billiard_subtotal"] * float(pb1_bl) / 100
            )
            res["table_session"]["service_bl"] = (
                res["dsc_billiard_subtotal"] * float(service_bl) / 100
            )
            res["table_session"]["dsc_billiard_total"] = (
                res["dsc_billiard_subtotal"]
                + res["table_session"]["pb1_bl"]
                + res["table_session"]["service_bl"]
            )
            res["table_session"]["dsc_billiard_total"] = round(
                res["table_session"]["dsc_billiard_total"]
            )

        else:
            res["serviced_by"] = ""
            res["user_nm"] = ""
            res["bill_cd"] = ""
            res["paid_type"] = ""
            res["paid_amount"] = 0

        res["time"] = datetime.now()
        res["data"] = {}
        res["orders"] = listData

        # Initialize defaultdict to store grouped data
        grouped_data = []

        # Dictionary to track items and accumulate qty and total by name
        accumulated_data = defaultdict(lambda: {"qty": 0, "total": 0, "items": []})

        # Loop through the listData and group by 'name'
        for item in listData:
            name = item["menu_nm"]

            # Update the qty and total for the current name
            accumulated_data[name]["qty"] += item["qty"]
            accumulated_data[name]["total"] += item[
                "total"
            ]  # calculate the total as qty * price

            # Append the item to the list under the current name
            accumulated_data[name]["items"].append(item)

        # Convert accumulated data into the final grouped array
        for name, data in accumulated_data.items():
            grouped_data.append(
                {
                    "name": name,
                    "qty": data["qty"],
                    "total": data["total"],  # Use 'total' instead of 'price'
                    "items": data["items"],
                }
            )

        # Assign the final grouped data to the response dictionary
        res["grouped_data"] = grouped_data

        res["grand_total"] = round(
            res["dsc_bill_total"] + res["table_session"]["dsc_billiard_total"]
            if res["table_session"] != ""
            else 0
        )
        jsonStr["data"] = {}
        jsonStr["data"]["is_waitinglist"] = waiting_list
        jsonStr["data"].update(res)

        # except Exception as ex:
        #     self.log.exception("Error in getBillDtlByTable")
        #     jsonStr.update({"isError": constants.YES, "status": "Failed"})
        #     return jsonStr, 500

        return jsonStr
