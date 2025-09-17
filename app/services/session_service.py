"""Domain service for session lifecycle management."""
from __future__ import annotations

from typing import List

from fastapi import HTTPException, status

from app.repositories.session_repository import SessionRepository
from app.schemas.session import SessionCreate, SessionRead, TranscriptRead


class SessionService:
    """High level operations around sessions and transcripts."""

    def __init__(self, repository: SessionRepository):
        self._repository = repository

    async def create_session(self, payload: SessionCreate) -> SessionRead:
        entity = await self._repository.create_session(name=payload.name)
        return SessionRead(
            id=entity.id,
            name=entity.name,
            created_at=entity.created_at,
            transcripts=[],
        )

    async def get_session(self, session_id: str) -> SessionRead:
        entity = await self._repository.get_session(session_id)
        if not entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
            )
        return SessionRead.model_validate(entity)

    async def delete_session(self, session_id: str) -> None:
        deleted = await self._repository.delete_session(session_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
            )

    async def ensure_session_exists(self, session_id: str) -> None:
        entity = await self._repository.get_session(session_id)
        if not entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
            )

    async def add_transcript(self, session_id: str, text: str) -> TranscriptRead:
        await self.ensure_session_exists(session_id)
        transcript = await self._repository.add_transcript(session_id, text)
        return TranscriptRead.model_validate(transcript)

    async def get_recent_transcripts(
        self, session_id: str, limit: int = 5
    ) -> List[TranscriptRead]:
        await self.ensure_session_exists(session_id)
        transcripts = await self._repository.get_recent_transcripts(
            session_id, limit=limit
        )
        return [TranscriptRead.model_validate(item) for item in transcripts]

    async def list_transcripts(self, session_id: str) -> List[TranscriptRead]:
        await self.ensure_session_exists(session_id)
        transcripts = await self._repository.list_transcripts(session_id)
        return [TranscriptRead.model_validate(item) for item in transcripts]
