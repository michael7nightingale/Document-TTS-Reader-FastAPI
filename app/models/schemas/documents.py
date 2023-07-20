from enum import StrEnum
from pydantic import BaseModel


class DocumentDownload(BaseModel):
    document_id: str


class LanguageEnum(StrEnum):
    russian = "ru"
    english = "en"
