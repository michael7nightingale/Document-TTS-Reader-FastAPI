from app.db.services.base import BaseService
from app.db.repositories.async_mongo import AsyncMongoRepository


def wrap_model(model):
    def wrapper(func):
        async def inner(*args, **kwargs):
            res = await func(*args, **kwargs)
            if "_id" in res:
                res['id'] = str(res["_id"])
                del res['_id']
            return model(**res)
        return inner
    return wrapper


class AsyncMongoService(BaseService):
    """
    Service class to serve sqlalchemy object by async engine and sessions.
    """
    table_name: str
    repository_class = AsyncMongoRepository

    def __init__(self, db):
        self._repository = self.repository_class(table=getattr(db, self.table_name))

    @property
    def repository(self):
        return self._repository

    async def get(self, *args, **kwargs):
        """Get object."""
        return await self.repository.get(*args, **kwargs)

    async def delete(self, id_: str):
        """Delete object."""
        return await self.repository.delete(id_)

    async def update(self, id_: str, **kwargs):
        """Update object."""
        return await self.repository.update(id_, **kwargs)

    async def all(self):
        """Get all objects."""
        return await self.repository.all()

    async def filter(self, **kwargs):
        """Filter objects."""
        return await self.repository.filter(**kwargs)

    async def create(self, **kwargs):
        """Create object."""
        return await self.repository.create(**kwargs)
