from datetime import date
from pydantic import BaseModel, Field
from typing import Dict, List


class Create(BaseModel):
    nm: str | None = Field(default=None, examples=["alexander"])
    amount: int | None = Field(default=None, examples=[100])
    desc: str | None = Field(default=None, examples=["a"])
    price: float | None = Field(default=None, examples=[10000])
    created_by: str | None = Field(default=None, examples=["a"])


class Update(BaseModel):
    cd: str | None = Field(default=None, examples=["de49a436a2b44adf9e83dbf3c3e10c32"])
    nm: str | None = Field(default=None, examples=["alexander"])
    amount: int | None = Field(default=None, examples=[100])
    desc: str | None = Field(default=None, examples=["a"])
    price: float | None = Field(default=None, examples=[10000])
    updated_by: str | None = Field(default=None, examples=["a"])


class Delete(BaseModel):
    cd: str | None = Field(default=None, examples=["a"])
    updated_by: str | None = Field(
        default=None, examples=["76f3ef06-11a3-4526-9cc8-b6f7e03a4c35"]
    )


class GetByCd(BaseModel):
    cd: str | None = Field(
        default=None, examples=["56ec0be5-f911-4ec3-b6a1-4da33d36e2b5"]
    )


class GetAll(BaseModel):
    page: int | None = Field(default=None, examples=[1])
    per_page: int | None = Field(default=None, examples=[10])
    search: str | None = Field(default=None, examples=["a"])
    sort_by: str | None = Field(default=None, examples=["cd"])
    sort_order: str | None = Field(default=None, examples=["asc", "desc"])

class DeleteBulk(BaseModel):
    cd: list | None = Field(default=None, examples=["a", "b", "c"])
    updated_by: str | None = Field(
        default=None, examples=["76f3ef06-11a3-4526-9cc8-b6f7e03a4c35"]
    )