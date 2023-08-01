from datetime import datetime

from app.db.services.async_mongo import AsyncMongoService, wrap_model
from app.models.schemas import Document


class DocumentService(AsyncMongoService):
    table_name = "documents"

    @wrap_model(Document)
    async def get(self, *args, **kwargs):
        return await super().get(*args, **kwargs)

    async def update_time_opened(self, id_: str):
        return await super().update(id_, time_opened=datetime.now())

    async def create(self, **kwargs):
        kwargs['time_created'] = datetime.now()
        return await super().create(**kwargs)

    async def update_time_opened_and_page(self, id_: str, page: int):
        return await super().update(id_, time_opened=datetime.now(), current_page=page)
