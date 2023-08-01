import pymongo
from fastapi import FastAPI
from fastapi_authtools import AuthManager
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker
from starlette.staticfiles import StaticFiles

from app.core.config import get_app_settings, get_test_app_settings
from app.api.routes import __api_routers__
from app.db import create_db
from app.models.schemas import UserCustomModel


class Server:
    def __init__(self, test: bool = False):
        self._app = FastAPI()
        if test:
            self._settings = get_test_app_settings()
        else:
            self._settings = get_app_settings()
        self._engine: AsyncEngine
        self._pool: async_sessionmaker

        self._configurate_db()
        self._configurate_app()

    @property
    def app(self) -> FastAPI:
        return self._app

    @property
    def settings(self):
        return self._settings

    def _configurate_db(self):
        db = create_db(
            db_uri=self.settings.db_uri,
            db_name=self.settings.DB_NAME
        )
        db.users.create_index(
            [("username", pymongo.DESCENDING), ("email", pymongo.DESCENDING)], unique=True
        )
        self.app.state.db = db

    def _configurate_app(self) -> None:
        """Configurate FastAPI application."""
        # including routers
        for api_router in __api_routers__:
            self.app.include_router(api_router, prefix="/api/v1")
        # event handlers settings
        self.app.add_event_handler(event_type="startup", func=self._on_startup_event)
        self.app.add_event_handler(event_type="shutdown", func=self._on_shutdown_event)
        # auth manager settings
        self.app.state.auth_manager = AuthManager(
            app=self.app,
            user_model=UserCustomModel,
            algorithm=self.settings.ALGORITHM,
            secret_key=self.settings.SECRET_KEY,
            expire_minutes=self.settings.EXPIRE_MINUTES,
        )
        # static files settings
        self.app.mount("/static", StaticFiles(directory="app/static/"), name='static')
        self.app.state.STATIC_DIR = "app/static/"

    async def _on_startup_event(self):
        """Startup handler."""

    async def _on_shutdown_event(self):
        """Shutdown handler."""
