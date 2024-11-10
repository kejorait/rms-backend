
from pydantic import BaseModel, Field


class Login(BaseModel):
    username: str | None = Field(default=None, examples=["kasir"])
    password: str | None = Field(default=None, examples=["1111"])
    
class CheckAdmin(BaseModel):
    password: str | None = Field(default=None, examples=["1111"])