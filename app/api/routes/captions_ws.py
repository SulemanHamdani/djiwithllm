"""WebSocket endpoint for streaming captions."""
from __future__ import annotations

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from app.api.deps import (
    get_caption_service,
    get_session_service,
    get_websocket_manager,
)
from app.services.caption_service import CaptionService
from app.services.session_service import SessionService
from app.services.websocket_manager import WebSocketManager

router = APIRouter()


@router.websocket("/ws/captions")
async def captions_stream(
    websocket: WebSocket,
    session_id: str,
    session_service: SessionService = Depends(get_session_service),
    caption_service: CaptionService = Depends(get_caption_service),
    websocket_manager: WebSocketManager = Depends(get_websocket_manager),
) -> None:
    await session_service.ensure_session_exists(session_id)
    await websocket_manager.connect(session_id, websocket)
    await caption_service.broadcast_history(session_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await websocket_manager.disconnect(session_id, websocket)
