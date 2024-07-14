from datetime import date
from uuid import UUID
from pydantic import BaseModel, Field
from typing import Dict, List


class Update(BaseModel):
    data: Dict[str, float | str] | None = Field(
        default=None, examples=[{"pb1": 0.1, "service": 0.1, "restaurant_enable": "Y"}]
    )
    updated_by: str | None = Field(default=None, examples=["owner"])
