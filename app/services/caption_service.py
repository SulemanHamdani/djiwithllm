"""Coordinates frame captioning with the configured LLM adapter."""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException, WebSocket, status

from app.schemas.caption import CaptionMessage
from app.services.llm.base import VisionLLMAdapter
from app.services.session_service import SessionService
from app.services.websocket_manager import WebSocketManager

logger = logging.getLogger(__name__)


class CaptionService:
    """Handles conversion of frames into captions and broadcasting updates."""

    def __init__(
        self,
        session_service: SessionService,
        adapter: VisionLLMAdapter,
        websocket_manager: WebSocketManager,
    ) -> None:
        self._session_service = session_service
        self._adapter = adapter
        self._websocket_manager = websocket_manager

    async def process_frame(self, session_id: str, frame_bytes: bytes) -> str:
        """Generate captions for the frame and broadcast them to listeners."""

        await self._session_service.ensure_session_exists(session_id)
        context = await self._session_service.get_recent_transcripts(session_id)
        context_text = [item.text for item in context]

        caption_parts: list[str] = []
        try:
            async for chunk in self._adapter.generate_caption(frame_bytes, context_text):
                caption_parts.append(chunk)
                message = CaptionMessage(
                    session_id=session_id,
                    type="partial",
                    text="".join(caption_parts).strip(),
                )
                await self._websocket_manager.broadcast(
                    session_id, message.model_dump(mode="json")
                )
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.exception("Caption generation failed: %s", exc)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate caption",
            ) from exc

        final_caption = "".join(caption_parts).strip()
        transcript = None
        if final_caption:
            transcript = await self._session_service.add_transcript(
                session_id, final_caption
            )
        final_message = CaptionMessage(
            session_id=session_id,
            type="final",
            text=final_caption,
            created_at=(
                transcript.created_at if transcript else datetime.now(timezone.utc)
            ),
        )
        await self._websocket_manager.broadcast(
            session_id, final_message.model_dump(mode="json")
        )
        return final_caption

    async def broadcast_history(
        self, session_id: str, websocket: Optional[WebSocket] = None
    ) -> None:
        """Send stored transcripts to subscribers."""

        transcripts = await self._session_service.list_transcripts(session_id)
        for transcript in transcripts:
            message = CaptionMessage(
                session_id=session_id,
                type="history",
                text=transcript.text,
                created_at=transcript.created_at,
            ).model_dump(mode="json")
            if websocket is not None:
                await websocket.send_json(message)
            else:
                await self._websocket_manager.broadcast(session_id, message)
