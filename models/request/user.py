from datetime import date
from uuid import UUID
from pydantic import BaseModel, Field
from typing import Dict, List


class GetByRole(BaseModel):
    role: str | None = Field(default=None, examples=["kasir"])

class GetAll(BaseModel):
    search: str | None = Field(default=None, examples=["kasir"])

class Get(BaseModel):
    cd : str | None = Field(default=None, examples=["cacc5dd8602b4a8883f017be95cb7c9f"])

class Delete(BaseModel):
    cd : str | None = Field(default=None, examples=["cacc5dd8602b4a8883f017be95cb7c9f"])

class Update(BaseModel):
    cd: str | None = Field(default=None, examples=["bd8ddcbd9bbc4f168bac96dea7610b9c"])
    name: str | None = Field(default=None, examples=["a"])
    username: str  | None = Field(default=None, examples=["aaadwadadawdwadadwadwadwadawdwa"])
    role_cd: str  | None = Field(default=None, examples=["waiter"])
    created_by: str  | None = Field(default=None, examples=["a"])
    password: str  | None = Field(default=None, examples=["a"])

class Create(BaseModel):
    name: str | None = Field(default=None, examples=["a"])
    username: str  | None = Field(default=None, examples=["aaadwadadawdwadadwadwadwadawdwa"])
    role_cd: str  | None = Field(default=None, examples=["waiter"])
    created_by: str  | None = Field(default=None, examples=["a"])
    password: str  | None = Field(default=None, examples=["a"])