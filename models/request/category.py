from typing import Optional

from fastapi import File, Form, UploadFile
from pydantic import BaseModel, Field


class Get(BaseModel):
    search: Optional[str] | None = Field(default=None, examples=["category"])

class GetDtl(BaseModel):
    cd : str | None = Field(default=None, examples=["50c29efd3e4947a58bc8b48fc5a33817"])

class Create:
    def __init__(
        self,
        nm: Optional[str] = Form(None, json_schema_extra={
            'example': 'category1',
        }),
        created_by: Optional[str] = Form(None, json_schema_extra={
            'example': 'owner',
        }),
        file: UploadFile = File(None, content_type='image/*')
    ):
        self.nm = nm
        self.created_by = created_by
        self.file = file

class Update:
    def __init__(
        self,
        cd: Optional[str] = Form(None, json_schema_extra={
            'example': 'ab296b71e1194053863b9d165d7ee709',
        }),
        nm: Optional[str] = Form(None, json_schema_extra={
            'example': 'category1',
        }),
        updated_by: Optional[str] = Form(None, json_schema_extra={
            'example': 'owner',
        }),
        file: UploadFile = File(None, content_type='image/*')
    ):
        self.cd = cd
        self.nm = nm
        self.updated_by = updated_by
        self.file = file

class Delete(BaseModel):
    cd: str | None = Field(default=None, examples=["123e4567-e89b-12d3-a456-426655440000"])
    deleted_by: str | None = Field(default=None, examples=["owner"])