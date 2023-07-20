from sqlalchemy import Column, String, ForeignKey, DateTime, Integer

from app.db import Base
from app.db.models.base import TableMixin


class Document(Base, TableMixin):
    __tablename__ = 'documents'

    user_id = Column(String(100), ForeignKey("users.id"))
    title = Column(String(255))
    extension = Column(String(10))
    pages = Column(Integer())
    current_page = Column(Integer())
    time_opened = Column(DateTime(timezone=True))
    time_created = Column(DateTime(timezone=True))
    document_url = Column(String(255))
    cover_url = Column(String(255))
