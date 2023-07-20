from sqlalchemy import Column, String, ForeignKey, DateTime, Integer, func

from app.db import Base
from app.db.models.base import TableMixin
from app.services import now


class Document(Base, TableMixin):
    __tablename__ = 'documents'

    user_id = Column(String(100), ForeignKey("users.id"))
    title = Column(String(255))
    extension = Column(String(10))
    pages = Column(Integer())
    current_page = Column(Integer())
    time_opened = Column(DateTime(timezone=True))
    time_created = Column(DateTime(timezone=True), default=now)
    document_url = Column(String(255))
    cover_url = Column(String(255))
