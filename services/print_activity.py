from datetime import datetime

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


class PrintService:

    name = "print"
    setupLog(serviceName=__file__)

    def __init__(self):
        self.log = getLogger(serviceName=__file__)
        # self.log.info(" init  BillDtlService ")

    def printBill(self, request, db):
        waiting_list = False
        jsonStr = {}
        try:
            # self.log.info("Response "+str(jsonStr))
            bill_cd = request.bill_cd

            query = db.query(
                Table.cd,
                Table.nm.label("table_nm"),
                Bill.created_by,
                User.name,
                BillDtl,
                Menu.price,
                Menu.nm,
                Menu.img,
            )
            query = query.join(Menu, Menu.cd == BillDtl.menu_cd)
            query = query.join(Bill, Bill.cd == BillDtl.bill_cd)
            query = query.join(Table, Table.cd == Bill.table_cd)
            query = query.join(User, User.cd == BillDtl.created_by)
            query = query.filter(Bill.cd == bill_cd)
            query = query.order_by(BillDtl.created_dt.asc())
            data = query.all()
            db.close()
            res = {}
            if len(data) < 1:
                query = db.query(
                    WaitingList.cd,
                    WaitingList.nm.label("table_nm"),
                    BillDtl,
                    Bill.created_by,
                    User.name,
                    Menu.price,
                    Menu.nm,
                    Menu.img,
                )

                query = query.join(Menu, Menu.cd == BillDtl.menu_cd)
                query = query.join(Bill, Bill.cd == BillDtl.bill_cd)
                query = query.join(WaitingList, WaitingList.cd == Bill.table_cd)
                query = query.join(User, User.cd == BillDtl.created_by)
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
                res["dining_total"] = (
                    subtotal + (subtotal + subtotal * 0.05) * 0.1 + subtotal * 0.05
                )
            if data:
                res["created_by"] = data[0].name
                res["table_nm"] = data[0].table_nm
                res["table_cd"] = data[0].cd
                if waiting_list:
                    res["table_nm"] = "Waiting List - " + data[0].table_nm
                res["no"] = data[0].BillDtl.bill_cd
            else:
                res["created_by"] = ""
                res["table_nm"] = ""
                res["table_cd"] = ""
                res["no"] = ""
            # res["address = "Jl. Satu Maret No.5, RT.5/RW.2, Pegadungan, Kec. Kalideres, Kota Jakarta Barat, Daerah Khusus Ibukota Jakarta 11830"
            res["time"] = datetime.now()
            # res["cashier = "Cashier"
            res["data"] = listData
            res["status"] = "Success"
            res["isError"] = constants.NO
            # jsonStr = json.dumps(res, default=str)
            jsonStr = res
            jsonStr["dining_total"] = 0
        except Exception as ex:
            self.log.exception(" BillDtlService")
            jsonStr["isError"] = constants.YES
            jsonStr["status"] = "Failed"

            return jsonStr, 500

        query = db.query(AppSetting)
        query = query.filter(AppSetting.is_inactive == constants.NO)
        query = query.filter(AppSetting.is_delete == constants.NO)
        query = query.filter(AppSetting.cd.in_(["time_interval", "price_per_interval"]))
        price_setting_query = query.all()
        price_settings = {
            setting.cd: int(setting.value) for setting in price_setting_query
        }
        jsonStr["price_per_interval"] = price_settings["price_per_interval"]
        jsonStr["time_interval"] = price_settings["time_interval"]

        # const tablePrice = (rawSeconds / 60 / Number(settings.time_interval)) * Number(settings.price_per_interval);

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
        data_list["total_time"] = 0
        data_list["total_amount"] = 0
        sessionList = []
        if table_session:
            time_interval = price_settings["time_interval"]
            price_per_interval = price_settings["price_per_interval"]
            for tbs in table_session:
                session_list = {}
                if tbs.session_is_closed == constants.YES:
                    seconds = round(
                        (tbs.closed_dt - tbs.session_created_dt).total_seconds()
                    )
                    if tbs.session_is_open == constants.NO:
                        data_list["total_time"] += tbs.session_amount
                    else:
                        data_list["total_time"] += seconds
                    minutes = round(seconds / 60)
                    session_list["session_created_dt"] = tbs.session_created_dt
                    session_list["session_closed_dt"] = tbs.closed_dt
                    session_list["session_time_minutes"] = minutes
                    session_price = minutes / time_interval * price_per_interval
                    session_list["session_price"] = session_price
                    data_list["total_amount"] += session_price
                if session_list:
                    sessionList.append(session_list)
        jsonStr["sessionList"] = sessionList
        jsonStr["blData"] = data_list
        jsonStr["total_amount"] = jsonStr["blData"]['total_amount'] + jsonStr["dining_total"]
        jsonStr.update(res)
        jsonStr["print_amount"] = request.print_amount if request.print_amount else 1
        jsonStr["html"] = request.html if request.html else None

        if request.print_to_printer:
            printSelenium.printBill(db, "payment", jsonStr)

        return jsonStr
