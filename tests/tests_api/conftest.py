import os.path
from shutil import rmtree
from uuid import uuid4
import pytest_asyncio
from httpx import AsyncClient
from fastapi import FastAPI, APIRouter

from app.api.routes import (
    main_router,
    documents_router,
    auth_router,

)
from app.core.server import Server
from app.db.services import UserService, DocumentService
from app.services.documents import get_pages_count_and_cover
from app.services import get_name_and_extension


@pytest_asyncio.fixture
async def app() -> FastAPI:
    server = Server(test=True)
    yield server.app
    db = server.app.state.db
    db['users'].drop()
    db['documents'].drop()


@pytest_asyncio.fixture
async def client(app: FastAPI) -> AsyncClient:
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
async def client_user1(client: AsyncClient, users_test_data: dict, user1: dict):
    user_token_data = {
        "username": user1['username'],
        "password": user1['password']
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
async def client_user2(client: AsyncClient, users_test_data: dict, user2: dict):
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
async def users_test_data(app: FastAPI, user1: dict, user2: dict):
    users_service = UserService(app.state.db)
    user1_ = await users_service.register(user1)
    await users_service.activate(user1_['_id'])
    user2_ = await users_service.register(user2)
    await users_service.activate(user2_['_id'])
    users = user1_, user2_
    yield users
    users_paths = tuple((os.path.join(app.state.STATIC_DIR, user['_id']) for user in users))
    for path in users_paths:
        if os.path.exists(path):
            rmtree(path)


@pytest_asyncio.fixture
async def documents_test_data(app: FastAPI, users_test_data: tuple):
    user1, user2 = users_test_data
    user1_path = user1['_id']
    user1_fullpath = os.path.join(app.state.STATIC_DIR, user1_path)
    user2_path = user1['_id']
    user2_fullpath = os.path.join(app.state.STATIC_DIR, user2_path)
    if not os.path.exists(user1_fullpath):
        os.makedirs(user1_fullpath)
    if not os.path.exists(user2_fullpath):
        os.makedirs(user2_fullpath)
    documents_service = DocumentService(app.state.db)
    with open("tests/tests_api/files/python.pdf", "rb") as file_to_read:
        document1_uuid = str(uuid4())
        filename, extension = get_name_and_extension("python.pdf")
        document1_path = os.path.join(user1_path, document1_uuid)
        document1_fullpath = os.path.join(app.state.STATIC_DIR, document1_path)
        os.makedirs(document1_fullpath)
        document_file_path = os.path.join(document1_path, f"{filename}.{extension}")
        document_file_fullpath = os.path.join(app.state.STATIC_DIR, document_file_path)
        cover_path = os.path.join(document1_path, f"{filename}_cover.png")
        cover_fullpath = os.path.join(app.state.STATIC_DIR, cover_path)
        with open(document_file_fullpath, "wb") as file_to_write:
            file_to_write.write(file_to_read.read())

        pages = get_pages_count_and_cover(extension, document_file_fullpath, cover_fullpath)
        document1 = await documents_service.create(
            _id=document1_uuid,
            title=filename,
            pages=pages,
            current_page=0,
            document_url=document_file_path,
            cover_url=cover_path,
            user_id=user1['_id'],
            extension=extension
        )
    yield document1


@pytest_asyncio.fixture
def user_not_activated():
    return {
        "username": "Notactive",
        "password": "veryactivenot",
        "email": 'notactive229@gmail.com'
    }


@pytest_asyncio.fixture
async def not_active_user(app: FastAPI, user_not_activated: dict):
    user_repo = UserService(app.state.db)
    user = await user_repo.register(user_not_activated)
    yield user


def url_for(router: APIRouter):
    def inner(name: str, **kwargs) -> str:
        return router.url_path_for(name, **kwargs)
    return inner


get_main_url = url_for(main_router)
get_auth_url = url_for(auth_router)
get_document_url = url_for(documents_router)
