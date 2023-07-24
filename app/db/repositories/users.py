from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.db.repositories.base import BaseRepository
from app.db.models import User
from app.services.hash import hash_password, verify_password


class UserRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def login(self, username: str, password: str, **kwargs):
        user = await self.get_by(username=username)
        if user is not None:
            if user.is_active:
                if verify_password(password, user.password):
                    return user

    async def register(self, user_data: dict | BaseModel):
        if isinstance(user_data, BaseModel):
            user_data = user_data.model_dump()
        else:
            user_data = user_data.copy()
        user_data.update(password=hash_password(user_data['password']))
        new_user = await self.create(**user_data)
        return new_user

    async def activate(self, user_id: str, email: str):
        user = await super().get(user_id)
        if user is None:
            return None
        if user.email == email:
            user.is_active = True
            await self.save(user)
            return user
