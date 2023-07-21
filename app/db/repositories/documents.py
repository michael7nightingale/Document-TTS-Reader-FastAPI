from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.base import BaseRepository
from app.db.models import Document
from app.services import now


class DocumentRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(Document, session)

    async def update_time_opened(self, id_: int | str):
        await super().update(id_, time_opened=now())

    async def update_time_opened_and_page(self, id_: int | str, current_page: int):
        await super().update(id_, time_opened=now(), current_page=current_page)
