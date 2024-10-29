from datetime import date
from fastapi import UploadFile, File, Form
from typing import Dict, List, Optional

from pydantic import BaseModel

class UploadLogo:
    def __init__(
        self,
        file: UploadFile = File(None, content_type="image/*")
    ):
        self.file = file
