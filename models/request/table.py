
from pydantic import BaseModel, Field


class Get(BaseModel):
    None

class Create(BaseModel):
    nm: str | None = Field(default=None, examples=["table1"])
    desc: str | None = Field(default=None, examples=["table1"])
    is_billiard: str | None = Field(default=None, examples=["Y"])
    created_by: str | None = Field(default=None, examples=["owner"])

class Update(BaseModel):
    cd: str | None = Field(default=None, examples=["123e4567-e89b-12d3-a456-426655440000"])
    nm: str | None = Field(default=None, examples=["table1"])
    desc: str | None = Field(default=None, examples=["table1"])
    is_billiard: str | None = Field(default=None, examples=["Y"])
    updated_by: str | None = Field(default=None, examples=["owner"])

class Delete(BaseModel):
    cd: str | None = Field(default=None, examples=["123e4567-e89b-12d3-a456-426655440000"])
    deleted_by: str | None = Field(default=None, examples=["owner"])

class DeleteBulk(BaseModel):
    cd: list | None = Field(default=None, examples=["123e4567-e89b-12d3-a456-426655440000", "123e4567-e89b-12d3-a456-426655440000"])
    deleted_by: str | None = Field(default=None, examples=["owner"])

class GetByCd(BaseModel):
    cd: str | None = Field(default=None, examples=["123e4567-e89b-12d3-a456-426655440000"])