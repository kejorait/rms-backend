from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Create(BaseModel):
    cd: str = Field(..., example="eac51a0464334c25b2b3eca27ae5792a")
    table_cd: str = Field(..., example="A01")
    created_by: str = Field(..., example="system")
    user_nm: str = Field(..., example="Liem")


class Update(BaseModel):
    cd: str = Field(..., example="eac51a0464334c25b2b3eca27ae5792a")
    table_cd: str = Field(..., example="A01")
    moved_by: str = Field(..., example="system")
    user_nm: str = Field(..., example="Liem")


class Delete(BaseModel):
    cd: str = Field(..., example="eac51a0464334c25b2b3eca27ae5792a")
    deleted_by: Optional[str] = Field(None, example="system")


class Close(BaseModel):
    cd: str = Field(..., example="eac51a0464334c25b2b3eca27ae5792a")
    closed_by: Optional[str] = Field(None, example="system")


class Paid(BaseModel):
    cd: str = Field(..., example="eac51a0464334c25b2b3eca27ae5792a")
    paid_type: Optional[str] = Field(None, example="CASH")
    bill_total: Optional[int] = Field(None, example=10000)
    paid_amount: Optional[int] = Field(None, example=10000)
    paid_by: Optional[str] = Field(None, example="system")

class FromToDt(BaseModel):
    from_dt: Optional[datetime] = Field(None, example="1691219")
    to_dt: Optional[datetime] = Field(None, example="2096536019")