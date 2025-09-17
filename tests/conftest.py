from __future__ import annotations

import asyncio
from typing import AsyncIterator

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.core.config import get_settings
from app.db import session as db_session
from app.main import create_app


@pytest.fixture(scope="session")
def event_loop() -> AsyncIterator[asyncio.AbstractEventLoop]:
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture()
def configure_settings(tmp_path, monkeypatch) -> str:
    database_url = f"sqlite+aiosqlite:///{tmp_path/'test.db'}"
    monkeypatch.setenv("DATABASE_URL", database_url)
    get_settings.cache_clear()
    db_session.configure_engine(database_url)
    return database_url


@pytest_asyncio.fixture()
async def app_fixture(configure_settings) -> FastAPI:
    app = create_app()
    await db_session.init_db()
    return app


@pytest_asyncio.fixture()
async def async_client(app_fixture: FastAPI) -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=app_fixture)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client
