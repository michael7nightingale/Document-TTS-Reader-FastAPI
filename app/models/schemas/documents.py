from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Document(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    title: str
    pages: int
    current_page: int
    extension: str
    cover_url: str
    document_url: str
    time_created: datetime
    time_opened: Optional[datetime] = None


class DocumentDownload(BaseModel):
    document_id: str


class DocumentShow(BaseModel):
    title: str
    pages: int
    current_page: int
    extension: str
    cover_url: str
    document_url: str
    time_created: datetime
    time_opened: Optional[datetime] = None


class DocumentUpdate(BaseModel):
    title: str | None = None
