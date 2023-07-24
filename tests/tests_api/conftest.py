import pytest
import pytest_asyncio
from httpx import AsyncClient
import os

from app.api.routes import (
    main_router,
    documents_router,
    translator_router,
    auth_router
)
from app.core.server import Server
from app.db import Base
from app.db.repositories import UserRepository


@pytest_asyncio.fixture
async def app():
    os.environ.setdefault("TEST", "1")
    server = Server()
    async with server.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield server.app
    async with server.engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client(app):
    async with AsyncClient(app=app, base_url="http://localhost:8000/api/v1/") as client_:
        yield client_


@pytest_asyncio.fixture
def user1():
    return {
        "username": "michael7",
        "password": "password",
        "email": "asdasd@gmail.com"
    }


@pytest_asyncio.fixture
def user2():
    return {
        "username": "michaasdael7",
        "password": "password123",
        "email": "asdaghhksd@gmail.com"
    }


@pytest_asyncio.fixture
async def authorized_client(client: AsyncClient, users_test_data, user2):
    user_token_data = {
        "username": user2['username'],
        "password": user2['password']
    }
    response = await client.post(
        get_auth_url("get_token"),
        json=user_token_data
    )
    access_token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    client.headers = headers
    yield client


@pytest_asyncio.fixture
async def users_test_data(app, user1, user2):
    async with app.state.pool() as session:
        users_repo = UserRepository(session)
        user1_ = await users_repo.register(user1)
        await users_repo.activate(user1_.id, user1_.email)
        user2_ = await users_repo.register(user2)
        await users_repo.activate(user2_.id, user2_.email)


@pytest_asyncio.fixture
def user_not_activated():
    return {
        "username": "Notactive",
        "password": "veryactivenot",
        "email": 'notactive229@gmail.com'
    }


@pytest_asyncio.fixture
async def not_active_user(app, user_not_activated):
    async with app.state.pool() as session:
        user_repo = UserRepository(session)
        user = await user_repo.register(user_not_activated)
        yield user


def url_for(router):
    def inner(name, **kwargs):
        return router.url_path_for(name, **kwargs)
    return inner


get_main_url = url_for(main_router)
get_auth_url = url_for(auth_router)
get_translator_url = url_for(translator_router)
get_document_url = url_for(documents_router)
