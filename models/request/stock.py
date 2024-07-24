from datetime import date
from uuid import UUID
from pydantic import BaseModel, Field
from typing import Dict, List


class Create(BaseModel):
    nm: str | None = Field(default=None, examples=["alexander"])
    amount: int | None = Field(default=None, examples=[100])
    desc: str | None = Field(default=None, examples=["a"])
    price: float | None = Field(default=None, examples=[10000])
    created_by: str | None = Field(default=None, examples=["a"])
    is_drink: bool | None = Field(default=None, examples=["Y"])

class Update(BaseModel):
    cd: str | None = Field(default=None, examples=["de49a436a2b44adf9e83dbf3c3e10c32"])
    nm: str | None = Field(default=None, examples=["alex"])
    desc: str | None = Field(default=None, examples=["alex"])
    updated_by: str | None = Field(default=None, examples=["alex"])
    price: float | None = Field(default=None, examples=[10000])
    category_cd: str | None = Field(default=None, examples=["alex"])

class Delete(BaseModel):
    cd: str | None = Field(default=None, examples=["a"])
    updated_by: UUID | None = Field(default=None, examples=["76f3ef06-11a3-4526-9cc8-b6f7e03a4c35"])

class Get(BaseModel):
    bill_cd: str | None = Field(default=None, examples=["76f3ef06-11a3-4526-9cc8-b6f7e03a4c35"])

class GetByCd(BaseModel):
    cd: str | None = Field(default=None, examples=["56ec0be5-f911-4ec3-b6a1-4da33d36e2b5"])


class GetAll(BaseModel):
    search: str | None = Field(default=None, examples=["heinek"])