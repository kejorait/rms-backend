from typing import Optional

from fastapi import File, Form, UploadFile
from pydantic import BaseModel, Field


class Create:
    def __init__(
        self,
        nm: Optional[str] = Form(None, json_schema_extra={
            'example': 'menu1',
        }),
        desc: Optional[str] = Form(None, json_schema_extra={
            'example': 'menu1 desc',
        }),
        price: Optional[int] = Form(None, json_schema_extra={
            'example': 1000,  # Changed to an integer value
        }),
        discount: Optional[int] = Form(None, json_schema_extra={
            'example': 10,  # Changed to an integer value
        }),
        category_cd: Optional[str] = Form(None, json_schema_extra={
            'example': 'category1',
        }),
        created_by: Optional[str] = Form(None, json_schema_extra={
            'example': 'owner',
        }),
        is_drink: Optional[str] = Form(None, json_schema_extra={
            'example': 'Y',
        }),
        stock: Optional[int] = Form(None, json_schema_extra={
            'example': 100,
        }),
        file: Optional[UploadFile] = File(None)  # Set file as optional
    ):
        self.nm = nm  # Corrected variable name
        self.desc = desc  # Added to store description
        self.price = price  # Added to store price
        self.discount = discount  # Added to store discount
        self.category_cd = category_cd  # Added to store category code
        self.created_by = created_by  # Corrected variable name
        self.is_drink = is_drink  # Added to store drink status
        self.stock = stock
        self.file = file  # Corrected variable name

class Update:
    def __init__(
        self,
        cd: Optional[str] = Form(None, json_schema_extra={
            'example': '56ec0be5-f911-4ec3-b6a1-4da33d36e2b5',
        }),
        nm: Optional[str] = Form(None, json_schema_extra={
            'example': 'menu1',
        }),
        desc: Optional[str] = Form(None, json_schema_extra={
            'example': 'menu1 desc',
        }),
        price: Optional[int] = Form(None, json_schema_extra={
            'example': 1000,  # Changed to an integer value
        }),
        discount: Optional[int] = Form(None, json_schema_extra={
            'example': 10,  # Changed to an integer value
        }),
        category_cd: Optional[str] = Form(None, json_schema_extra={
            'example': 'category1',
        }),
        updated_by: Optional[str] = Form(None, json_schema_extra={
            'example': 'owner',
        }),
        is_drink: Optional[str] = Form(None, json_schema_extra={
            'example': 'Y',
        }),
        stock: Optional[int] = Form(None, json_schema_extra={
            'example': 100,
        }),
        file: Optional[UploadFile] = File(None)  # Set file as optional
    ):
        self.cd = cd
        self.nm = nm  # Corrected variable name
        self.desc = desc  # Added to store description
        self.price = price  # Added to store price
        self.discount = discount  # Added to store discount
        self.category_cd = category_cd  # Added to store category code
        self.updated_by = updated_by  # Corrected variable name
        self.is_drink = is_drink  # Added to store drink status
        self.stock = stock
        self.file = file  # Corrected variable name


class Delete(BaseModel):
    cd: str | None = Field(default=None, examples=["a"])
    updated_by: str | None = Field(default=None, examples=["76f3ef06-11a3-4526-9cc8-b6f7e03a4c35"])

class Get(BaseModel):
    bill_cd: str | None = Field(default=None, examples=["76f3ef06-11a3-4526-9cc8-b6f7e03a4c35"])

class GetByCd(BaseModel):
    cd: str | None = Field(default=None, examples=["56ec0be5-f911-4ec3-b6a1-4da33d36e2b5"])


class GetAll(BaseModel):
    search: str | None = Field(default=None, examples=["heinek"])