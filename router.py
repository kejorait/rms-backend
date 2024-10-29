from fastapi import APIRouter

from routers import bill, bill_dtl, menu, stock, table_session, user, auth, table, waiting_list, category, role, app_setting, uploads


router = APIRouter(
    prefix="/api/v1"
)

# health check
@router.get("/health")
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