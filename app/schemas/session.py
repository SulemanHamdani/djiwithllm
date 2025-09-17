"""Pydantic schemas for session management."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class SessionCreate(BaseModel):
    """Payload for creating a session."""

    name: Optional[str] = Field(default=None, max_length=255)


class TranscriptRead(BaseModel):
    """Represents a transcript record."""

    id: int
    text: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SessionRead(BaseModel):
    """Representation of a session."""

    id: str
    name: Optional[str]
    created_at: datetime
    transcripts: List[TranscriptRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
