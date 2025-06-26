from datetime import datetime
from typing import List

from pydantic import BaseModel


class User(BaseModel):
    username: str
    password: str


class VisibilityToggleRequest(BaseModel):
    filename: str
    make_public: bool


class FileMetadata(BaseModel):
    filename: str
    content_type: str
    size: int
    upload_time: datetime
    username: str
    shared_with: List[str] = []
