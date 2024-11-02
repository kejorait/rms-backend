from typing import Optional

from fastapi import File, Form, UploadFile
from pydantic import BaseModel, Field


class GetByRole(BaseModel):
    role: str | None = Field(default=None, examples=["kasir"])

class GetAll(BaseModel):
    search: str | None = Field(default=None, examples=["kasir"])

class Get(BaseModel):
    user_cd : str | None = Field(default=None, examples=["cacc5dd8602b4a8883f017be95cb7c9f"])

class Delete(BaseModel):
    cd : str | None = Field(default=None, examples=["cacc5dd8602b4a8883f017be95cb7c9f"])

class Update:
    def __init__(
        self,
        cd: Optional[str] = Form(None, json_schema_extra={
            'example': 'ab296b71e1194053863b9d165d7ee709',
        }),
        name: Optional[str] = Form(None, json_schema_extra={
            'example': 'category1',
        }),
        username: Optional[str] = Form(None, json_schema_extra={
            'example': 'owner',
        }),
        role_cd: Optional[str] = Form(None, json_schema_extra={
            'example': 'owner',
        }),
        password: Optional[str] = Form(None, json_schema_extra={
            'example': 'owner',
        }),
        updated_by: Optional[str] = Form(None, json_schema_extra={
            'example': 'owner',
        }),
        file: Optional[UploadFile] = File(None)  # Set file as optional
    ):
        self.cd = cd
        self.name = name
        self.username = username
        self.role_cd = role_cd
        self.password = password
        self.updated_by = updated_by
        self.file = file

        
class Create:
    def __init__(
        self,
        name: Optional[str] = Form(None, json_schema_extra={
            'example': 'category1',
        }),
        username: Optional[str] = Form(None, json_schema_extra={
            'example': 'owner',
        }),
        role_cd: Optional[str] = Form(None, json_schema_extra={
            'example': 'owner',
        }),
        password: Optional[str] = Form(None, json_schema_extra={
            'example': 'owner',
        }),
        created_by: Optional[str] = Form(None, json_schema_extra={
            'example': 'owner',
        }),
        file: Optional[UploadFile] = File(None)  # Set file as optional
    ):
        self.name = name
        self.username = username
        self.role_cd = role_cd
        self.password = password
        self.created_by = created_by
        self.file = file