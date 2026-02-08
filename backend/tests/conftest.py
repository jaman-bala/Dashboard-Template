# ruff: noqa: E402
import pytest
from httpx import AsyncClient
from typing import AsyncGenerator
from unittest import mock

mock.patch("fastapi_cache.decorator.cache", lambda *args, **kwargs: lambda f: f).start()

from src.apps.api.dependencies import get_db
from src.core.config import settings
from src.core.database.database import (
    Base,
    engine_null_pool,
    async_session_maker_null_pool,
)
from src.core.utils.db_manager import DBManager
from src.main import app
from src.apps.models import *  # noqa


@pytest.fixture(scope="session", autouse=True)
async def check_test_mode():
    assert settings.MODE == "test"


async def get_db_null_pool():
    async with DBManager(session_factory=async_session_maker_null_pool) as db:
        yield db


@pytest.fixture(scope="function")
async def db() -> AsyncGenerator[DBManager, None]:
    async for db in get_db_null_pool():
        yield db


app.dependency_overrides[get_db] = get_db_null_pool


@pytest.fixture(scope="session", autouse=True)
async def setup_database(check_test_mode):
    async with engine_null_pool.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture(scope="session")
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        yield ac


@pytest.fixture(scope="session", autouse=True)
async def register_user(ac: AsyncClient, setup_database):
    await ac.post(
        "/auth/create",
        json={
            "phone": "0500500500",
            "password": "test123",
        },
    )


@pytest.fixture(scope="session")
async def authenticated_ac(ac: AsyncClient, register_user):
    response = await ac.post(
        "/auth/login",
        json={
            "phone": "0500500500",
            "password": "test123",
        },
    )
    assert response.status_code == 200
    assert ac.cookies["access_token"]
    yield ac
