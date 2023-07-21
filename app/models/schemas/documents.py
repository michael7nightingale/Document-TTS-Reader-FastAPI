from pydantic import BaseModel


class DocumentDownload(BaseModel):
    document_id: str


class DocumentUpdate(BaseModel):
    title: str | None = None
