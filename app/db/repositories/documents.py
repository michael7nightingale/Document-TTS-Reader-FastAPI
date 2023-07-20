from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.base import BaseRepository
from app.db.models import Document


class DocumentRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(Document, session)
