"""Dependency injection wiring for FastAPI routes."""
from __future__ import annotations

from typing import AsyncIterator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import HTTPConnection

from app.core.config import get_settings
from app.db.session import get_db
from app.repositories.session_repository import SessionRepository
from app.services.caption_service import CaptionService
from app.services.llm.base import VisionLLMAdapter
from app.services.llm.groq import GroqVisionAdapter
from app.services.llm.mock import MockVisionAdapter
from app.services.session_service import SessionService
from app.services.websocket_manager import WebSocketManager


async def get_websocket_manager(connection: HTTPConnection) -> WebSocketManager:
    return connection.app.state.websocket_manager


async def get_vision_adapter(connection: HTTPConnection) -> VisionLLMAdapter:
    adapter = getattr(connection.app.state, "vision_adapter", None)
    if adapter is None:
        settings = get_settings()
        if settings.vision_adapter.lower() == "groq":
            adapter = GroqVisionAdapter()
        else:
            adapter = MockVisionAdapter()
        connection.app.state.vision_adapter = adapter
    return adapter


async def get_session_service(
    db: AsyncSession = Depends(get_db),
) -> AsyncIterator[SessionService]:
    repository = SessionRepository(db)
    yield SessionService(repository)


async def get_caption_service(
    session_service: SessionService = Depends(get_session_service),
    vision_adapter: VisionLLMAdapter = Depends(get_vision_adapter),
    websocket_manager: WebSocketManager = Depends(get_websocket_manager),
) -> AsyncIterator[CaptionService]:
    yield CaptionService(session_service, vision_adapter, websocket_manager)
