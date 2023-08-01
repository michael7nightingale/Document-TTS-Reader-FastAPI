from typing import Optional
from uuid import uuid4

from app.db.repositories.base import BaseRepository


def string_id(func):
    async def inner(*args, **kwargs):
        res = await func(*args, **kwargs)
        res['_id'] = str(res['_id'])
        return res
    return inner


class AsyncMongoRepository(BaseRepository):

    def __init__(self, table):
        self._table = table

    @property
    def table(self):
        return self._table

    async def update(self, id_: str, **kwargs):
        updated_result = await self.table.update_one({"_id": id_}, {"$set": kwargs})
        if updated_result.modified_count == 1:
            if (updated_obj := await self.table.find_one({"_id": id_})) is not None:
                return updated_obj

    async def all(self):
        return await self.table.find().to_list(10**9)

    async def get(self, *args, **kwargs):
        if len(args):
            if len(args) == 1:
                kwargs.update(_id=args[0])
            else:
                raise ValueError("One arg expected.")
        obj = await self.table.find_one(kwargs)
        return obj

    async def filter(self, **kwargs):
        objs = await self.table.find(kwargs).to_list(10*9)
        return objs

    async def delete(self, id_: str) -> Optional[bool]:
        delete_result = await self.table.delete_one({"_id": id_})
        if delete_result.deleted_count == 1:
            return True

    async def create(self, **kwargs):
        if "_id" not in kwargs:
            kwargs['_id'] = str(uuid4())
        insert_result = await self.table.insert_one(kwargs)
        insert_obj = await self.table.find_one({"_id": insert_result.inserted_id})
        return insert_obj
