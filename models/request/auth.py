from datetime import date
from uuid import UUID
from pydantic import BaseModel, Field
from typing import Dict, List


class Login(BaseModel):
    username: str | None = Field(default=None, examples=["kasir"])
    password: str | None = Field(default=None, examples=["1111"])