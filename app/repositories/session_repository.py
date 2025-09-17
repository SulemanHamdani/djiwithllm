"""Data access layer for sessions and transcripts."""
from __future__ import annotations

from typing import List, Optional

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.session import Session as SessionModel, Transcript as TranscriptModel


class SessionRepository:
    """Encapsulates database persistence for sessions and transcripts."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def create_session(self, name: Optional[str] = None) -> SessionModel:
        entity = SessionModel(name=name)
        self._session.add(entity)
        await self._session.commit()
        await self._session.refresh(entity)
        return entity

    async def get_session(self, session_id: str) -> Optional[SessionModel]:
        stmt = select(SessionModel).options(selectinload(SessionModel.transcripts)).where(
            SessionModel.id == session_id
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete_session(self, session_id: str) -> bool:
        stmt = delete(SessionModel).where(SessionModel.id == session_id)
        result = await self._session.execute(stmt)
        await self._session.commit()
        return result.rowcount > 0

    async def add_transcript(self, session_id: str, text: str) -> TranscriptModel:
        transcript = TranscriptModel(session_id=session_id, text=text)
        self._session.add(transcript)
        await self._session.commit()
        await self._session.refresh(transcript)
        return transcript

    async def get_recent_transcripts(self, session_id: str, limit: int = 5) -> List[TranscriptModel]:
        stmt = (
            select(TranscriptModel)
            .where(TranscriptModel.session_id == session_id)
            .order_by(TranscriptModel.created_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        items = list(result.scalars().all())
        items.reverse()
        return items

    async def list_transcripts(self, session_id: str) -> List[TranscriptModel]:
        stmt = (
            select(TranscriptModel)
            .where(TranscriptModel.session_id == session_id)
            .order_by(TranscriptModel.created_at.asc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
