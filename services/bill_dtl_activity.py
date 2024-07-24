import json
from datetime import datetime
import datetime as dt
from rich.console import Console
from uuid import uuid4
from models.bill_dtl import BillDtl
from models.menu import Menu
from models.table import Table
from models.bill import Bill
from models.table_session import TableSession
from models.waiting_list import WaitingList
from helper.jsonHelper import ExtendEncoder
from helper import constants
from utils.tinylog import getLogger, setupLog
from sqlalchemy import func
from fastapi.requests import Request
from fastapi import HTTPException


class BillDtlService:

    name = "billDtl"
    setupLog(serviceName=__file__)

    def __init__(self):
        self.log = getLogger(serviceName=__file__)
        # self.log.info(" init  BillDtlService ")

    # Get Bill Detail
    def getBillDtlByTable(self, request, db):
        waiting_list = False
        jsonStr = {}
        bill_cd = None
        try:
            res = {}
            # self.log.info("Response "+str(jsonStr))
            res["table_session"] = ""
            table_cd = request.table_cd

            query = db.query(Bill.cd, Bill.is_closed, Bill.is_paid, Bill.user_nm)
            query = query.filter(Bill.table_cd == table_cd)
            # query = query.filter(Bill.is_closed == constants.NO)
            query = query.filter(Bill.is_delete == constants.NO)
            query = query.filter(Bill.is_inactive == constants.NO)
            query = query.filter(Bill.is_paid == constants.NO)
            query = query.order_by(Bill.created_dt.desc())
            row = query.first()
            if row:
                bill_cd = row.cd

                query = db.query(TableSession)
                query = query.filter(TableSession.table_cd == table_cd)
                query = query.filter(TableSession.is_inactive == constants.NO)
                query = query.filter(TableSession.is_delete == constants.NO)
                query = query.filter(TableSession.is_closed == constants.NO)
                query = query.filter(TableSession.is_paid == constants.NO)
                query = query.filter(TableSession.bill_cd == bill_cd)
                query = query.order_by(TableSession.created_dt.desc())
                table_session = query.all()

                res["table_session"] = table_session

            # self.log.info(query.statement.compile(compile_kwargs={"literal_binds": True}))
            db.close()

            query = db.query(
                Table.cd,
                Table.nm.label("table_nm"),
                BillDtl,
                Menu.price,
                Menu.nm.label("menu_nm"),
                Menu.img,
                Bill.user_nm,
            )

            query = query.join(Menu, Menu.cd == BillDtl.menu_cd)
            query = query.join(Bill, Bill.cd == BillDtl.bill_cd)
            query = query.join(Table, Table.cd == Bill.table_cd)
            if bill_cd:
                query = query.filter(Bill.cd == bill_cd)
            query = query.filter(BillDtl.qty > 0)
            query = query.order_by(BillDtl.created_dt.asc())
            data = query.all()
            # self.log.info(query.statement.compile(compile_kwargs={"literal_binds": True}))
            db.close()

            status = "EMPTY"
            listData = []
            res["subtotal"] = 0
            for mdl in data:
                data_list = {}
                if int(mdl.BillDtl.qty) > 0:
                    data_list["cd"] = mdl.BillDtl.cd
                    data_list["bill_cd"] = mdl.BillDtl.bill_cd
                    data_list["created_dt"] = datetime.timestamp(mdl.BillDtl.created_dt)
                    data_list["created_by"] = mdl.BillDtl.created_by
                    data_list["is_inactive"] = mdl.BillDtl.is_inactive
                    data_list["is_delete"] = mdl.BillDtl.is_delete
                    data_list["process_status"] = mdl.BillDtl.process_status
                    data_list["menu_cd"] = mdl.BillDtl.menu_cd
                    data_list["user_nm"] = mdl.BillDtl.user_nm
                    data_list["menu_nm"] = mdl.menu_nm
                    data_list["menu_img"] = mdl.img
                    data_list["qty"] = int(mdl.BillDtl.qty)
                    data_list["desc"] = mdl.BillDtl.desc
                    data_list["split_qty"] = int(
                        mdl.BillDtl.qty - mdl.BillDtl.split_qty
                    )
                    data_list["init_qty"] = mdl.BillDtl.init_qty
                    data_list["updated_dt"] = mdl.BillDtl.updated_dt
                    data_list["price"] = mdl.price
                    data_list["total"] = float(mdl.price) * data_list["qty"]
                    res["subtotal"] += float(mdl.price) * data_list["qty"]
                    listData.append(data_list)
            if row:

                if row.is_closed == constants.NO and row.is_paid == constants.YES:
                    status = "EMPTY"
                if row.is_closed == constants.YES and row.is_paid == constants.NO:
                    status = "CLOSED"
                if row.is_closed == constants.NO and row.is_paid == constants.NO:
                    status = "OCCUPIED"
            else:
                status = "EMPTY"
            res["pb1"] = res["subtotal"] * 0.1
            res["service"] = res["subtotal"] * 0.05
            res["total"] = res["service"] + res["pb1"] + res["subtotal"]
            res["bill_status"] = status

            query = db.query(Table.nm)
            query = query.filter(Table.cd == table_cd)
            row2 = query.first()
            db.close()
            res["table_cd"] = table_cd

            if row2:
                res["table_nm"] = row2.nm
            else:
                query = db.query(
                    WaitingList.cd,
                    WaitingList.nm.label("table_nm"),
                    BillDtl,
                    Menu.price,
                    Menu.nm.label("menu_nm"),
                    Menu.img,
                    Bill.user_nm,
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

                if data:
                    res["table_nm"] = data[0].table_nm
                    if waiting_list:
                        res["table_nm"] = "Waiting List - " + data[0].table_nm
                else:
                    res["table_nm"] = ""
                listData = []
                for mdl in data:

                    if int(mdl.BillDtl.qty) > 0:
                        data_list = {}
                        data_list["cd"] = mdl.BillDtl.cd
                        data_list["bill_cd"] = mdl.BillDtl.bill_cd
                        data_list["created_dt"] = datetime.timestamp(
                            mdl.BillDtl.created_dt
                        )
                        data_list["created_by"] = mdl.BillDtl.created_by
                        data_list["is_inactive"] = mdl.BillDtl.is_inactive
                        data_list["is_delete"] = mdl.BillDtl.is_delete
                        data_list["process_status"] = mdl.BillDtl.process_status
                        data_list["menu_cd"] = mdl.BillDtl.menu_cd
                        data_list["user_nm"] = mdl.BillDtl.user_nm
                        data_list["menu_nm"] = mdl.menu_nm
                        data_list["menu_img"] = mdl.img
                        data_list["qty"] = int(mdl.BillDtl.qty)
                        data_list["desc"] = mdl.BillDtl.desc
                        data_list["split_qty"] = int(
                            mdl.BillDtl.qty - mdl.BillDtl.split_qty
                        )
                        data_list["updated_dt"] = mdl.BillDtl.updated_dt
                        data_list["price"] = mdl.price
                        data_list["total"] = float(mdl.price) * data_list["qty"]
                        listData.append(data_list)

            if row is not None:
                res["user_nm"] = row.user_nm
                res["bill_cd"] = row.cd
            else:
                res["user_nm"] = ""
                res["bill_cd"] = ""
            res["data"] = listData
            res["status"] = "Success"
            res["isError"] = constants.NO
            jsonStr = res
        except Exception as ex:
            self.log.exception(" BillDtlService")
            jsonStr["isError"] = constants.YES
            jsonStr["status"] = "Failed"

            return jsonStr, 500
        # self.log.info("Response " + str(jsonStr))
        return jsonStr

    def getBillDtlByBillCd(self, request, db):
        waiting_list = False
        jsonStr = {}
        try:
            # self.log.info("Response "+str(jsonStr))
            bill_cd = request.bill_cd

            query = db.query(
                Table.cd,
                BillDtl,
                Menu.price,
                Menu.nm,
                Menu.img,
                Bill.is_closed,
                Bill.is_paid,
            )

            query = query.join(Menu, Menu.cd == BillDtl.menu_cd)
            query = query.join(Bill, Bill.cd == BillDtl.bill_cd)
            query = query.join(Table, Table.cd == Bill.table_cd)
            query = query.filter(Bill.cd == bill_cd)
            query = query.filter(BillDtl.qty > 0)
            query = query.order_by(BillDtl.created_dt.asc())
            data = query.all()
            # self.log.info(query.statement.compile(compile_kwargs={"literal_binds": True}))
            db.close()
            res = {}

            listData = []
            if data:
                for mdl in data:
                    if mdl.BillDtl.qty > 0:
                        data_list = {}
                        data_list["table_cd"] = mdl.cd
                        data_list["cd"] = mdl.BillDtl.cd
                        data_list["bill_cd"] = mdl.BillDtl.bill_cd
                        data_list["created_dt"] = datetime.timestamp(
                            mdl.BillDtl.created_dt
                        )
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
                        data_list["price"] = mdl.price
                        data_list["total"] = float(mdl.price) * data_list["qty"]
                        listData.append(data_list)
            else:
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
                # self.log.info(query.statement.compile(compile_kwargs={"literal_binds": True}))
                db.close()
                waiting_list = True

                if data:
                    res["table_nm"] = data[0].table_nm
                    if waiting_list:
                        res["table_nm"] = "Waiting List - " + data[0].table_nm
                else:
                    res["table_nm"] = ""
                listData = []
                for mdl in data:
                    if mdl.BillDtl.qty > 0:
                        data_list = {}
                        data_list["cd"] = mdl.BillDtl.cd
                        data_list["bill_cd"] = mdl.BillDtl.bill_cd
                        data_list["bill_cd"] = mdl.BillDtl.bill_cd
                        data_list["created_dt"] = datetime.timestamp(
                            mdl.BillDtl.created_dt
                        )
                        data_list["created_by"] = mdl.BillDtl.created_by
                        data_list["is_inactive"] = mdl.BillDtl.is_inactive
                        data_list["is_delete"] = mdl.BillDtl.is_delete
                        data_list["process_status"] = mdl.BillDtl.process_status
                        data_list["menu_cd"] = mdl.BillDtl.menu_cd
                        data_list["user_nm"] = mdl.BillDtl.user_nm
                        data_list["menu_nm"] = mdl.menu_nm
                        data_list["menu_img"] = mdl.img
                        data_list["qty"] = int(mdl.BillDtl.qty)
                        data_list["desc"] = mdl.BillDtl.desc
                        data_list["split_qty"] = int(
                            mdl.BillDtl.qty - mdl.BillDtl.split_qty
                        )
                        data_list["init_qty"] = mdl.BillDtl.init_qty
                        data_list["updated_dt"] = mdl.BillDtl.updated_dt
                        data_list["price"] = mdl.price
                        data_list["total"] = float(mdl.price) * data_list["qty"]
                        listData.append(data_list)

            query = db.query(Bill)
            query = query.filter(Bill.cd == bill_cd)
            data_bill = query.first()
            # self.log.info(query.statement.compile(compile_kwargs={"literal_binds": True}))
            db.close()
            status = ""
            if data_bill:
                if (
                    data_bill.is_closed == constants.NO
                    and data_bill.is_paid == constants.YES
                ):
                    status = "EMPTY"
                if (
                    data_bill.is_closed == constants.YES
                    and data_bill.is_paid == constants.NO
                ):
                    status = "CLOSED"
                if (
                    data_bill.is_closed == constants.NO
                    and data_bill.is_paid == constants.NO
                ):
                    status = "OCCUPIED"
            res["data"] = listData
            res["status"] = "Success"
            res["bill_status"] = status
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
                    data_list["price"] = mdl.price
                    data_list["total"] = float(mdl.price) * int(mdl.BillDtl.qty)
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
                for mdl in request.orders:
                    billDtl = BillDtl()
                    billDtl.cd = uuid4().hex
                    billDtl.bill_cd = request.bill_cd
                    billDtl.process_status = "NEW_ORDER"
                    billDtl.menu_cd = mdl["menu_cd"]
                    if "desc" in mdl:
                        billDtl.desc = mdl["desc"]
                    else:
                        billDtl.desc = ""
                    billDtl.qty = mdl["qty"]
                    billDtl.init_qty = mdl["qty"]
                    billDtl.split_qty = 0
                    billDtl.created_dt = dt.datetime.now()
                    billDtl.created_by = mdl["created_by"]
                    billDtl.is_delete = constants.NO
                    billDtl.is_inactive = constants.NO

                    db.add(billDtl)
                    db.commit()

                    jsonStr["data"] = constants.STATUS_SUCCESS
                    jsonStr["isError"] = constants.NO
                    jsonStr["status"] = "Success"
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
