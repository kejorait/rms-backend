from datetime import date
from pydantic import BaseModel, Field
from typing import List, Optional


class Get(BaseModel):
    table_cd: Optional[str] = Field(None, example="A01")


class GetByCd(BaseModel):
    cd: Optional[str] = Field(None, example="123456")


class Print(BaseModel):
    bill_cd: Optional[str] = Field(None, example="ABC123")


class FromToDt(BaseModel):
    from_dt: Optional[date] = Field(None, example="2024-01-01")
    to_dt: Optional[date] = Field(None, example="2024-12-31")


class Create(BaseModel):
    bill_cd: Optional[str] = Field(None, example="76f3ef06-11a3-4526-9cc8-b6f7e03a4c35")
    process_status: Optional[str] = Field(None, example="ON_PROCESS")
    menu_cd: Optional[str] = Field(None, example="c13bff59-3983-4308-94d0-50a708669d68")
    user_nm: Optional[str] = Field(None, example="Liem")
    qty: Optional[int] = Field(None, example=2)
    created_by: Optional[str] = Field(None, example="system")


class CreateBulkDetail(BaseModel):
    menu_cd: Optional[str] = Field(None, example="c13bff59-3983-4308-94d0-50a708669d68")
    user_nm: Optional[str] = Field(None, example="Liem")
    qty: Optional[int] = Field(None, example=2)
    created_by: Optional[str] = Field(None, example="system")


class CreateBulk(BaseModel):
    bill_cd: Optional[str] = Field(None, example="9f47f518-33a3-4be9-9b9a-e829bf0721f5")
    orders: Optional[List[CreateBulkDetail]] = None


class DeleteBulkDetail(BaseModel):
    bill_dtl_cd: Optional[str] = Field(None, example="6b94ea48aa8044809e44b23808150d89")
    qty: Optional[int] = Field(None, example=1111)


class DeleteBulk(BaseModel):
    data: Optional[List[DeleteBulkDetail]] = None


class UpdateQty(BaseModel):
    bill_dtl_cd: Optional[str] = Field(None, example="3959b5ff8f264a5c8f8db9ed041e9673")
    qty: Optional[int] = Field(None, example=1111)


class Delete(BaseModel):
    cd: Optional[str] = Field(None, example="eac51a0464334c25b2b3eca27ae5792a")


class Update(BaseModel):
    cd: Optional[str] = Field(None, example="eac51a0464334c25b2b3eca27ae5792a")
    process_status: Optional[str] = Field(None, example="12")
