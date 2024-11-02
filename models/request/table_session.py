from typing import Optional

from pydantic import BaseModel, Field


class Get(BaseModel):
    None

class Open(BaseModel):
    table_cd: Optional[str] = Field(None, example="1")
    created_by: Optional[str] = Field(None, example="owner")
    bill_cd: Optional[str] = Field(None, example="76f3ef06-11a3-4526-9cc8-b6f7e03a4c35")
    price: Optional[str] = Field(None, example="3600")

class Fixed(BaseModel):
    table_cd: Optional[str] = Field(None, example="1")
    amount: Optional[str] = Field(None, example="3600")
    created_by: Optional[str] = Field(None, example="owner")
    bill_cd: Optional[str] = Field(None, example="76f3ef06-11a3-4526-9cc8-b6f7e03a4c35")
    price: Optional[str] = Field(None, example="3600")

class Close(BaseModel):
    table_cd: Optional[str] = Field(None, example="1")
    closed_by: Optional[str] = Field(None, example="owner")

class Sync(BaseModel):
    None