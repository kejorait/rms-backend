from fastapi import APIRouter

from routers import (app_setting, auth, bill, bill_dtl, category, dining_table,
                     menu, role, stock, table, table_session, uploads, user,
                     waiting_list)

router = APIRouter(prefix="/api/v1")


# health check
@router.get("/health", tags=["Health Check"])
def healthcheck():
    return {"status": "OK"}


router.include_router(bill.router)

router.include_router(bill_dtl.router)

router.include_router(menu.router)

router.include_router(user.router)

router.include_router(auth.router)

router.include_router(table.router)

router.include_router(waiting_list.router)

router.include_router(category.router)

router.include_router(role.router)

router.include_router(app_setting.router)

router.include_router(uploads.router)

router.include_router(stock.router)

router.include_router(table_session.router)

router.include_router(dining_table.router)