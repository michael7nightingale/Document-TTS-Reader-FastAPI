from pydantic import BaseModel

from app.db.services.async_mongo import AsyncMongoService
from app.services.hash import verify_password, hash_password


class UserService(AsyncMongoService):
    table_name = "users"

    async def login(self, username: str, password: str):
        user = await self.get(username=username)
        if user is not None:
            if verify_password(password, user['password']):
                return user if user['is_active'] else None

    async def register(self, user_data: dict | BaseModel):
        if isinstance(user_data, BaseModel):
            user_data = user_data.model_dump()
        else:
            user_data = user_data.copy()
        user_data.update(
            password=hash_password(user_data['password']),
            is_active=False,
            is_superuser=False,
            is_admin=False
        )
        new_user = await self.repository.create(**user_data)
        return new_user

    async def activate(self, user_id: str):
        return await self.repository.update(user_id, is_active=True)
