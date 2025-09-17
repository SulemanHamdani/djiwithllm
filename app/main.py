"""FastAPI application entrypoint."""
from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import captions_ws, frames, health, sessions
from app.core.config import get_settings
from app.db.session import init_db
from app.services.llm.mock import MockVisionAdapter
from app.services.websocket_manager import WebSocketManager

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(title=settings.app_name, debug=settings.debug)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(sessions.router)
    app.include_router(frames.router)
    app.include_router(captions_ws.router)

    app.state.websocket_manager = WebSocketManager()
    if getattr(app.state, "vision_adapter", None) is None:
        app.state.vision_adapter = MockVisionAdapter()

    @app.on_event("startup")
    async def on_startup() -> None:  # pragma: no cover - event wiring
        logger.info("Initializing database")
        await init_db()

    return app


app = create_app()
