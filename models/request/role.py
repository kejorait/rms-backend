from datetime import date
from fastapi import File, Form, UploadFile
from pydantic import BaseModel, Field
from typing import Dict, List, Optional


class Get(BaseModel):
    None