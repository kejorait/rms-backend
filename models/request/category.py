from datetime import date
from uuid import UUID
from fastapi import File, Form, UploadFile
from pydantic import BaseModel, Field
from typing import Dict, List, Optional


class Get(BaseModel):
    None

class GetDtl(BaseModel):
    cd : str | None = Field(default=None, examples=["50c29efd3e4947a58bc8b48fc5a33817"])

class Create(BaseModel):
    nm: str | None = Field(default=None, examples=["NIGUN"])
    file: List[UploadFile] | None = File(...) 
    created_by: str | None = Field(default=None, examples=["owner"])

class CreateForm:
    def __init__(
        self,
        nm: Optional[str] = Form(None),
        created_by: Optional[str] = Form(None),
        file: Optional[UploadFile] = File(...),
        is_drink: Optional[str] = Form(None)
    ):
        self.nm = nm
        self.created_by = created_by
        self.file = file
        self.is_drink = is_drink

class Update(BaseModel):
    cd: str | None = Field(default=None, examples=["123e4567-e89b-12d3-a456-426655440000"])
    nm: str | None = Field(default=None, examples=["table1"])
    desc: str | None = Field(default=None, examples=["table1"])
    is_billiard: str | None = Field(default=None, examples=["Y"])
    updated_by: str | None = Field(default=None, examples=["owner"])

class Delete(BaseModel):
    cd: str | None = Field(default=None, examples=["123e4567-e89b-12d3-a456-426655440000"])
    deleted_by: str | None = Field(default=None, examples=["owner"])