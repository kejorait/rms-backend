import datetime as dt
from datetime import datetime
from uuid import uuid4

from helper import constants, printSelenium
from models.app_setting import AppSetting
from models.bill import Bill
from models.bill_dtl import BillDtl
from models.menu import Menu
from models.table import Table
from models.table_session import TableSession
from models.user import User
from models.waiting_list import WaitingList
from utils.tinylog import getLogger, setupLog


class BillDtlService:

    name = "billDtl"
    setupLog(serviceName=__file__)

    def __init__(self):
        self.log = getLogger(serviceName=__file__)
        # self.log.info(" init  BillDtlService ")

    # Get Bill Detail
    def getBillDtlByTable(self, request, db):
        jsonStr = {"status": "Success", "isError": constants.NO}
        table_cd = request.table_cd
        res = {"table_session": "", "subtotal": 0}
        bill_cd = None
        waiting_list = False

        try:
            # Fetch initial bill details
            query = (
                db.query(Bill.cd, Bill.is_closed, Bill.is_paid, Bill.user_nm)
                .filter(
                    Bill.table_cd == table_cd,
                    Bill.is_delete == constants.NO,
                    Bill.is_inactive == constants.NO,
                    Bill.is_paid == constants.NO,
                )
                .order_by(Bill.created_dt.desc())
            )
            bill = query.first()

            if bill:
                bill_cd = bill.cd

                # Fetch table session details
                table_session_query = (
                    db.query(
                        TableSession.created_dt.label("session_created_dt"),
                        TableSession.amount.label("session_amount"),
                        TableSession.is_open.label("session_is_open"),
                        TableSession.is_closed.label("session_is_closed"),
                        TableSession.closed_dt,
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
                sessionList = []
                if table_session:
                    for tbs in table_session:
                        session_list = {}

                        if tbs.session_is_open == constants.YES:
                            if tbs.session_is_closed == constants.YES:
                                data_list["total_open"] += round(
                                    (
                                        tbs.closed_dt - tbs.session_created_dt
                                    ).total_seconds()
                                )
                                session_list["session_created_dt"] = (
                                    tbs.session_created_dt
                                )
                                session_list["session_closed_dt"] = tbs.closed_dt

                        if tbs.session_is_open == constants.NO:
                            if tbs.session_is_closed == constants.YES:
                                session_list["session_created_dt"] = (
                                    tbs.session_created_dt
                                )
                                session_list["session_closed_dt"] = tbs.closed_dt
                            data_list["session_amount"] += tbs.session_amount

                        if session_list:
                            sessionList.append(session_list)

                    # Assign query results to `data_list`
                    data_list["session_created_dt"] = table_session[
                        0
                    ].session_created_dt
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
                        "split_qty": mdl.BillDtl.qty - mdl.BillDtl.split_qty,
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
            res["pb1"] = res["subtotal"] * 0.1
            res["service"] = res["subtotal"] * 0.05
            res["total"] = res["subtotal"] + res["pb1"] + res["service"]

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
                db.query(Table.nm, Table.is_billiard)
                .filter(Table.cd == table_cd)
                .first()
            )
            if table_name_query:
                res["table_nm"] = table_name_query.nm
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
                        "Waiting List - " + waiting_data[0].table_nm
                        if waiting_list
                        else ""
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
                res["user_nm"] = bill.user_nm
                res["bill_cd"] = bill.cd
            else:
                res["user_nm"] = ""
                res["bill_cd"] = ""
            res["data"] = listData
            jsonStr.update(res)

        except Exception as ex:
            self.log.exception("Error in getBillDtlByTable")
            jsonStr.update({"isError": constants.YES, "status": "Failed"})
            return jsonStr, 500

        return jsonStr

    def getBillDtlByBillCd(self, request, db):
        waiting_list = False
        jsonStr = {}
        try:
            bill_cd = request.bill_cd

            # Query to get the latest session based on the highest created date in TableSession
            latest_session = (
                db.query(TableSession)
                .filter(TableSession.bill_cd == bill_cd)
                .order_by(TableSession.created_dt.desc())
                .limit(1)
                .subquery()
            )

            query = db.query(
                Table.cd,
                BillDtl,
                Menu.price,
                Menu.nm,
                Menu.img,
                Bill.is_closed,
                Bill.is_paid,
                latest_session.c.created_dt.label("session_created_dt"),
                latest_session.c.amount.label("session_amount"),
                latest_session.c.is_open.label("session_is_open"),
                latest_session.c.is_closed.label("session_is_closed"),
            )

            # Join with the latest session subquery instead of the full TableSession table
            query = query.join(Menu, Menu.cd == BillDtl.menu_cd)
            query = query.join(Bill, Bill.cd == BillDtl.bill_cd)
            query = query.join(Table, Table.cd == Bill.table_cd)
            query = query.join(latest_session, latest_session.c.bill_cd == Bill.cd)
            query = query.filter(Bill.cd == bill_cd)
            query = query.filter(BillDtl.qty > 0)
            query = query.order_by(BillDtl.created_dt.asc())
            data = query.all()

            db.close()
            res = {}
            listData = []

            if data:
                for mdl in data:
                    if mdl.BillDtl.qty > 0:
                        session_status = (
                            "CLOSED"  # Default status if none of the conditions match
                        )
                        if mdl.session_is_open == constants.YES:
                            session_status = "OPEN"
                        elif mdl.session_is_open == constants.NO:
                            session_status = "FIXED"

                        data_list = {
                            "table_cd": mdl.cd,
                            "cd": mdl.BillDtl.cd,
                            "bill_cd": mdl.BillDtl.bill_cd,
                            "created_dt": datetime.timestamp(mdl.BillDtl.created_dt),
                            "created_by": mdl.BillDtl.created_by,
                            "is_inactive": mdl.BillDtl.is_inactive,
                            "is_delete": mdl.BillDtl.is_delete,
                            "process_status": mdl.BillDtl.process_status,
                            "menu_cd": mdl.BillDtl.menu_cd,
                            "user_nm": mdl.BillDtl.user_nm,
                            "menu_nm": mdl.nm,
                            "menu_img": mdl.img,
                            "qty": int(mdl.BillDtl.qty),
                            "desc": mdl.BillDtl.desc,
                            "split_qty": int(mdl.BillDtl.qty - mdl.BillDtl.split_qty),
                            "updated_dt": mdl.BillDtl.updated_dt,
                            "price": mdl.price,
                            "total": float(mdl.price) * int(mdl.BillDtl.qty),
                            "session_status": session_status,
                            "session_created_dt": mdl.session_created_dt,
                            "session_amount": mdl.session_amount,
                            "session_is_open": mdl.session_is_open,
                            "session_is_closed": mdl.session_is_closed,
                        }
                        listData.append(data_list)
            else:
                # Query WaitingList as fallback
                query = db.query(
                    WaitingList.cd,
                    WaitingList.nm.label("table_nm"),
                    BillDtl,
                    Menu.price,
                    Menu.nm.label("menu_nm"),
                    Menu.img,
                    Bill.user_nm,
                    Bill.is_closed,
                    Bill.is_paid,
                )
                query = query.join(Menu, Menu.cd == BillDtl.menu_cd)
                query = query.join(Bill, Bill.cd == BillDtl.bill_cd)
                query = query.join(WaitingList, WaitingList.cd == Bill.table_cd)
                query = query.filter(Bill.cd == bill_cd)
                query = query.filter(BillDtl.qty > 0)
                query = query.order_by(BillDtl.created_dt.asc())
                data = query.all()

                db.close()
                waiting_list = True

                res["table_nm"] = data[0].table_nm if data else ""
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
                            "qty": int(mdl.BillDtl.qty),
                            "desc": mdl.BillDtl.desc,
                            "split_qty": int(mdl.BillDtl.qty - mdl.BillDtl.split_qty),
                            "init_qty": mdl.BillDtl.init_qty,
                            "updated_dt": mdl.BillDtl.updated_dt,
                            "price": mdl.price,
                            "total": float(mdl.price) * int(mdl.BillDtl.qty),
                        }
                        listData.append(data_list)

            # Check bill status
            query = db.query(Bill).filter(Bill.cd == bill_cd)
            data_bill = query.first()
            db.close()

            status = ""
            if data_bill:
                if (
                    data_bill.is_closed == constants.NO
                    and data_bill.is_paid == constants.YES
                ):
                    status = "EMPTY"
                elif (
                    data_bill.is_closed == constants.YES
                    and data_bill.is_paid == constants.NO
                ):
                    status = "CLOSED"
                elif (
                    data_bill.is_closed == constants.NO
                    and data_bill.is_paid == constants.NO
                ):
                    status = "OCCUPIED"

            res["data"] = listData
            res["status"] = "Success"
            res["bill_status"] = status
            res["isError"] = constants.NO
            jsonStr = res

        except Exception as ex:
            self.log.exception(" BillDtlService")
            jsonStr["isError"] = constants.YES
            jsonStr["status"] = "Failed"
            return jsonStr, 500

        return jsonStr

    def getBillDtlByBillCdPrint(self, request, db):
        waiting_list = False
        jsonStr = {}
        try:
            # self.log.info("Response "+str(jsonStr))
            bill_cd = request.bill_cd

            query = db.query(
                Table.cd,
                Table.nm.label("table_nm"),
                BillDtl,
                Menu.price,
                Menu.nm,
                Menu.img,
            )

            query = query.join(Menu, Menu.cd == BillDtl.menu_cd)
            query = query.join(Bill, Bill.cd == BillDtl.bill_cd)
            query = query.join(Table, Table.cd == Bill.table_cd)
            query = query.filter(Bill.cd == bill_cd)
            query = query.order_by(BillDtl.created_dt.asc())
            data = query.all()
            # self.log.info(query.statement.compile(compile_kwargs={"literal_binds": True}))
            db.close()
            res = {}
            if len(data) < 1:
                query = db.query(
                    WaitingList.cd,
                    WaitingList.nm.label("table_nm"),
                    BillDtl,
                    Menu.price,
                    Menu.nm,
                    Menu.img,
                )

                query = query.join(Menu, Menu.cd == BillDtl.menu_cd)
                query = query.join(Bill, Bill.cd == BillDtl.bill_cd)
                query = query.join(WaitingList, WaitingList.cd == Bill.table_cd)
                query = query.filter(Bill.cd == bill_cd)
                query = query.order_by(BillDtl.created_dt.asc())
                data = query.all()
                # self.log.info(query.statement.compile(compile_kwargs={"literal_binds": True}))
                db.close()
                waiting_list = True

            listData = []
            subtotal = 0
            for mdl in data:
                if mdl.BillDtl.qty > 0:
                    data_list = {}
                    data_list["table_cd"] = mdl.cd
                    data_list["cd"] = mdl.BillDtl.cd
                    data_list["bill_cd"] = mdl.BillDtl.bill_cd
                    data_list["created_dt"] = datetime.timestamp(mdl.BillDtl.created_dt)
                    data_list["created_by"] = mdl.BillDtl.created_by
                    data_list["is_inactive"] = mdl.BillDtl.is_inactive
                    data_list["is_delete"] = mdl.BillDtl.is_delete
                    data_list["process_status"] = mdl.BillDtl.process_status
                    data_list["menu_cd"] = mdl.BillDtl.menu_cd
                    data_list["user_nm"] = mdl.BillDtl.user_nm
                    data_list["menu_nm"] = mdl.nm
                    data_list["menu_img"] = mdl.img
                    data_list["qty"] = int(mdl.BillDtl.qty)
                    data_list["desc"] = mdl.BillDtl.desc
                    data_list["split_qty"] = int(
                        mdl.BillDtl.qty - mdl.BillDtl.split_qty
                    )
                    data_list["updated_dt"] = mdl.BillDtl.updated_dt
                    data_list["price"] = mdl.BillDtl.price
                    data_list["discount"] = mdl.BillDtl.discount
                    price_discount = float(mdl.BillDtl.price) - float(
                        mdl.BillDtl.discount
                    )
                    data_list["total"] = float(price_discount) * int(mdl.BillDtl.qty)
                    subtotal += float(mdl.price) * data_list["qty"]
                    listData.append(data_list)
                res["subtotal"] = subtotal
                res["service"] = subtotal * 0.05
                res["pb1"] = (subtotal + subtotal * 0.05) * 0.1
                res["total"] = (
                    subtotal + (subtotal + subtotal * 0.05) * 0.1 + subtotal * 0.05
                )
            if data:
                res["table_nm"] = data[0].table_nm
                if waiting_list:
                    res["table_nm"] = "Waiting List - " + data[0].table_nm
                res["no"] = data[0].BillDtl.bill_cd
            else:
                res["table_nm"] = ""
                res["no"] = ""
            # res["address = "Jl. Satu Maret No.5, RT.5/RW.2, Pegadungan, Kec. Kalideres, Kota Jakarta Barat, Daerah Khusus Ibukota Jakarta 11830"
            res["time"] = dt.datetime.now()
            # res["cashier = "Cashier"
            res["data"] = listData
            res["status"] = "Success"
            res["isError"] = constants.NO
            # jsonStr = json.dumps(res, default=str)
            jsonStr = res
        except Exception as ex:
            self.log.exception(" BillDtlService")
            jsonStr["isError"] = constants.YES
            jsonStr["status"] = "Failed"

            return jsonStr, 500
        # self.log.info("Response " + str(jsonStr))
        # print("Response: " + str(jsonStr))
        return jsonStr

    def getBillDtlAllTableBarista(self, request, db):
        jsonStr = {}
        try:
            # self.log.info("Response "+str(jsonStr))

            query = db.query(Table)

            query = query.join(Bill, Bill.table_cd == Table.cd)
            query = query.join(BillDtl, BillDtl.bill_cd == Bill.cd)
            query = query.filter(Bill.is_closed == constants.NO)
            query = query.filter(BillDtl.qty > 0)
            query = query.group_by(Table)
            # query = query.filter(BillDtl.process_status != "DONE")
            data = query.all()
            # self.log.info(query.statement.compile(compile_kwargs={"literal_binds": True}))
            db.close()
            query = db.query(WaitingList)

            query = query.join(Bill, Bill.table_cd == WaitingList.cd)
            query = query.join(BillDtl, BillDtl.bill_cd == Bill.cd)
            query = query.filter(Bill.is_closed == constants.NO)
            query = query.filter(BillDtl.qty > 0)
            query = query.group_by(WaitingList)
            # query = query.filter(BillDtl.process_status != "DONE")
            data_wl = query.all()
            # self.log.info(query.statement.compile(compile_kwargs={"literal_binds": True}))
            db.close()
            data = data + data_wl
            res = {}

            listData = []
            for mdl in data:

                query = db.query(BillDtl)
                query = query.join(Bill, BillDtl.bill_cd == Bill.cd)
                query = query.filter(Bill.table_cd == mdl.cd)
                # query = query.filter(BillDtl.process_status != "DONE")
                query = query.filter(Bill.is_paid == constants.NO)
                query = query.filter(BillDtl.qty > 0)
                query = query.order_by(BillDtl.created_dt.asc())
                row = query.all()
                db.close()
                data_list = {}
                data_list["table_cd"] = mdl.cd
                data_list["table_nm"] = mdl.nm
                if row:
                    row_dtl = []
                    table_dt = dt.datetime(1, 1, 1, 0, 0)
                    for x in row:
                        if x.created_dt > table_dt:
                            table_dt = x.created_dt
                        # self.log.info(x.cd)
                        query = db.query(Menu.nm)
                        query = query.filter(Menu.cd == x.menu_cd)
                        query = query.filter(Menu.is_drink == constants.YES)
                        # self.log.info(query.statement.compile(compile_kwargs={"literal_binds": True}))
                        menu = query.first()
                        db.close()
                        row_list = {}

                        if menu:
                            if x.qty > 0:
                                row_list["menu_nm"] = menu.nm
                                row_list["bill_dtl_cd"] = x.cd
                                row_list["bill_dtl_dt"] = x.created_dt
                                row_list["bill_dtl_qty"] = x.qty
                                row_list["bill_dtl_desc"] = x.desc
                                row_list["process_status"] = x.process_status
                                row_dtl.append(row_list)

                        # self.log.info(row_list)
                    # self.log.info(row_dtl)
                    data_list["orders"] = row_dtl

                    if len(row_dtl) != 0:
                        listData.append(data_list)

                data_list["table_dt"] = table_dt
            listData.sort(key=lambda x: x["table_dt"], reverse=True)
            res["data"] = listData
            res["status"] = "Success"
            res["isError"] = constants.NO
            # jsonStr = json.dumps(res, default=str)
            jsonStr = res
        except Exception as ex:
            self.log.exception(" BillDtlService")
            jsonStr["isError"] = constants.YES
            jsonStr["status"] = "Failed"

            return jsonStr, 500
        # self.log.info("Response " + str(jsonStr))
        return jsonStr

    def getBillDtlAllTableKitchen(self, request, db):
        jsonStr = {}
        try:
            # self.log.info("Response "+str(jsonStr))

            query = db.query(Table)

            query = query.join(Bill, Bill.table_cd == Table.cd)
            query = query.join(BillDtl, BillDtl.bill_cd == Bill.cd)
            query = query.group_by(Table)
            query = query.filter(Bill.is_closed == constants.NO)
            query = query.filter(BillDtl.qty > 0)
            data = query.all()
            # self.log.info(query.statement.compile(compile_kwargs={"literal_binds": True}))
            db.close()
            query = db.query(WaitingList)

            query = query.join(Bill, Bill.table_cd == WaitingList.cd)
            query = query.join(BillDtl, BillDtl.bill_cd == Bill.cd)
            query = query.group_by(WaitingList)
            query = query.filter(Bill.is_closed == constants.NO)
            query = query.filter(BillDtl.qty > 0)
            data_wl = query.all()
            # self.log.info(query.statement.compile(compile_kwargs={"literal_binds": True}))
            db.close()
            data = data + data_wl
            # self.log.info(data)
            res = {}

            listData = []
            for mdl in data:

                query = db.query(BillDtl)
                query = query.join(Bill, BillDtl.bill_cd == Bill.cd)
                query = query.filter(Bill.table_cd == mdl.cd)
                # query = query.filter(BillDtl.process_status != "DONE")
                query = query.filter(Bill.is_paid == constants.NO)
                query = query.filter(BillDtl.qty > 0)
                query = query.order_by(BillDtl.created_dt.asc())
                # self.log.info(query.statement.compile(compile_kwargs={"literal_binds": True}))
                row = query.all()
                db.close()
                data_list = {}
                data_list["table_cd"] = mdl.cd
                data_list["table_nm"] = mdl.nm
                if row:
                    row_dtl = []
                    table_dt = dt.datetime(1, 1, 1, 0, 0)
                    for x in row:
                        # self.log.info(x.cd)
                        if x.created_dt > table_dt:
                            table_dt = x.created_dt
                        query = db.query(Menu.nm)
                        query = query.filter(Menu.cd == x.menu_cd)
                        query = query.filter(Menu.is_drink == constants.NO)
                        menu = query.first()
                        db.close()
                        row_list = {}
                        if menu:
                            if x.qty > 0:
                                row_list["menu_nm"] = menu.nm
                                row_list["bill_dtl_cd"] = x.cd
                                row_list["bill_dtl_dt"] = x.created_dt
                                row_list["bill_dtl_qty"] = x.qty
                                row_list["bill_dtl_desc"] = x.desc
                                row_list["process_status"] = x.process_status
                                row_dtl.append(row_list)
                    # self.log.info(row_dtl)
                    data_list["orders"] = row_dtl

                    if len(row_dtl) != 0:
                        listData.append(data_list)
                data_list["table_dt"] = table_dt
            listData.sort(key=lambda x: x["table_dt"], reverse=True)
            res["data"] = listData
            res["status"] = "Success"
            res["isError"] = constants.NO
            # jsonStr = json.dumps(res, default=str)
            jsonStr = res
        except Exception as ex:
            self.log.exception(" BillDtlService")
            jsonStr["isError"] = constants.YES
            jsonStr["status"] = "Failed"

            return jsonStr, 500
        # self.log.info("Response " + str(jsonStr))
        return jsonStr

    # Create Bill Detail
    def addBillDetail(self, request, db):
        jsonStr = {}

        try:
            billDtl = BillDtl()
            billDtl.cd = uuid4().hex
            billDtl.bill_cd = request.bill_cd
            billDtl.process_status = request.process_status
            billDtl.menu_cd = request.menu_cd
            billDtl.user_nm = request.user_nm
            billDtl.qty = request.qty
            billDtl.desc = request.desc
            billDtl.created_dt = dt.datetime.now()
            billDtl.created_by = request.created_by
            billDtl.is_delete = constants.NO
            billDtl.is_inactive = constants.NO

            db.add(billDtl)
            db.commit()

            jsonStr["data"] = constants.STATUS_SUCCESS
            jsonStr["isError"] = constants.NO
            jsonStr["status"] = "Success"

        except Exception as ex:
            self.log.exception(" BillDtlService")
            jsonStr["isError"] = constants.YES
            jsonStr["status"] = "Failed"

            return jsonStr, 500
        # self.log.info("Response " + str(jsonStr))

        return jsonStr

    def bulkaddBillDetail(self, request, db):
        jsonStr = {}
        try:
            query = db.query(Bill)
            query = query.filter(Bill.cd == request.bill_cd)
            query = query.filter(Bill.is_closed == constants.NO)
            query = query.filter(Bill.is_paid == constants.NO)
            billdata = query.first()
            # self.log.info(query.statement.compile(compile_kwargs={"literal_binds": True}))
            db.close()
            # self.log.info("Response "+str(jsonStr))

            if billdata:
                # query = db.query(AppSetting)
                # query = query.filter(AppSetting.is_delete == constants.NO)
                # query = query.filter(AppSetting.is_inactive == constants.NO)
                # query = query.filter(
                #     AppSetting.cd.in_(["printer", "paper_width", "paper_height"])
                # )
                # print_query = query.all()

                # Extracting individual values
                # print_settings = {setting.cd: setting.value for setting in print_query}

                query = db.query(Table.nm)
                query = query.filter(Table.cd == billdata.table_cd)
                table_nm = query.first()
                printData = {}
                printData["menu_items"] = []
                printData["table_nm"] = table_nm.nm
                printData["created_dt"] = dt.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                query = db.query(User.name)
                query = query.filter(User.cd == request.orders[0].created_by)
                printData["created_by"] = query.first().name
                # printData["print_settings"] = print_settings

                for mdl in request.orders:
                    billDtl = BillDtl()
                    billDtl.cd = uuid4().hex
                    billDtl.bill_cd = request.bill_cd
                    billDtl.process_status = "NEW_ORDER"
                    billDtl.menu_cd = mdl.menu_cd
                    if "desc" in mdl:
                        billDtl.desc = mdl.desc
                    else:
                        billDtl.desc = ""
                    billDtl.qty = mdl.qty

                    menu = db.query(Menu).filter(Menu.cd == mdl.menu_cd).first()
                    billDtl.price = menu.price
                    billDtl.discount = menu.discount
                    billDtl.init_qty = mdl.qty
                    billDtl.split_qty = 0
                    billDtl.created_dt = dt.datetime.now()
                    billDtl.created_by = mdl.created_by
                    billDtl.is_delete = constants.NO
                    billDtl.is_inactive = constants.NO

                    db.add(billDtl)
                    db.commit()

                    printData["menu_items"].append({"menu_nm": menu.nm, "qty": mdl.qty})

                    jsonStr["data"] = constants.STATUS_SUCCESS
                    jsonStr["isError"] = constants.NO
                    jsonStr["status"] = "Success"

                if request.print_to_printer:
                    printSelenium.printBill(db, "new_order", printData)
                
            else:
                query = db.query(Bill)
                query = query.filter(Bill.cd == request.bill_cd)
                billinfo = query.first()
                db.close()
                self.log.info(billinfo)
                if billinfo.is_paid == constants.YES:
                    jsonStr["data"] = "Bill is PAID"
                if billinfo.is_closed == constants.YES:
                    jsonStr["data"] = "Bill is CLOSED"
                jsonStr["isError"] = constants.YES
                jsonStr["status"] = "Failed"

                return jsonStr, 500

        except Exception as ex:
            self.log.exception(" BillDtlService")
            jsonStr["isError"] = constants.YES
            jsonStr["status"] = "Failed"

            return jsonStr, 500
        # self.log.info("Response " + str(jsonStr))

        return jsonStr

    # Update Bill Detail
    def updateBillDetail(self, request, db):
        jsonStr = {}
        try:
            # self.log.info("Response "+str(jsonStr))

            cd = request.cd
            billDtl = db.query(BillDtl).get(cd)
            billDtl.process_status = request.process_status
            billDtl.updated_dt = dt.datetime.now()

            db.commit()

            jsonStr["data"] = constants.STATUS_SUCCESS
            jsonStr["isError"] = constants.NO
            jsonStr["status"] = "Success"

        except Exception as ex:
            self.log.exception(" BillDtlService")
            jsonStr["isError"] = constants.YES
            jsonStr["status"] = "Failed"

            return jsonStr, 500
        # self.log.info("Response " + str(jsonStr))
        return jsonStr
        # Update Bill Detail

    def updateBillDetailQty(self, request, db):
        jsonStr = {}
        try:
            # self.log.info("Response "+str(jsonStr))

            cd = request.bill_dtl_cd
            billDtl = db.query(BillDtl).get(cd)
            billDtl.qty = request.qty
            billDtl.updated_dt = dt.datetime.now()

            db.commit()

            jsonStr["data"] = constants.STATUS_SUCCESS
            jsonStr["isError"] = constants.NO
            jsonStr["status"] = "Success"

        except Exception as ex:
            self.log.exception(" BillDtlService")
            jsonStr["isError"] = constants.YES
            jsonStr["status"] = "Failed"

            return jsonStr, 500
        # self.log.info("Response " + str(jsonStr))
        return jsonStr

    # Delete Bill Detail
    def deleteBillDetail(self, request, db):
        jsonStr = {}
        try:
            # self.log.info("Response "+str(jsonStr))
            cd = request.cd
            billDtl = db.query(BillDtl).get(cd)
            billDtl.is_delete = "Y"

            db.commit()

            jsonStr["data"] = constants.STATUS_SUCCESS
            jsonStr["isError"] = constants.NO
            jsonStr["status"] = "Success"

        except Exception as ex:
            self.log.exception(" BillDtlService")
            jsonStr["isError"] = constants.YES
            jsonStr["status"] = "Failed"
            return jsonStr, 500
        # self.log.info("Response " + str(jsonStr))
        return jsonStr

    # Delete Bill Detail
    def deleteBillDetailBulk(self, request, db):
        jsonStr = {}
        try:
            # self.log.info("Response "+str(jsonStr))
            data = request.data
            for mdl in data:

                # self.log.info(mdl)
                query = db.query(BillDtl.split_qty)
                query = query.filter(BillDtl.cd == mdl["bill_dtl_cd"])
                # self.log.info(query.statement.compile(compile_kwargs={"literal_binds": True}))
                row = query.first()
                db.close()
                billDtl = db.query(BillDtl).get(mdl["bill_dtl_cd"])
                billDtl.qty = mdl["qty"]

                db.commit()

            jsonStr["data"] = constants.STATUS_SUCCESS
            jsonStr["isError"] = constants.NO
            jsonStr["status"] = "Success"

        except Exception as ex:
            self.log.exception(" BillDtlService")
            jsonStr["isError"] = constants.YES
            jsonStr["status"] = "Failed"
            return jsonStr, 500
        # self.log.info("Response " + str(jsonStr))
        return jsonStr
