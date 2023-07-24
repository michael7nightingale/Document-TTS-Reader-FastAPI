from pydantic import BaseModel


class DocumentDownload(BaseModel):
    document_id: str


class Document(BaseModel):
    title: str | None = None
