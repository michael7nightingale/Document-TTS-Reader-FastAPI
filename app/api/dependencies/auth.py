from fastapi import Body

from app.models.schemas import UserRegister


async def get_user_register_data(
        user_data: UserRegister = Body()
):
    return user_data
