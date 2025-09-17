"""Schemas for caption streaming over WebSockets."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class CaptionMessage(BaseModel):
    """Message delivered to WebSocket subscribers."""

    session_id: str
    type: Literal["partial", "final", "history"]
    text: str = Field(default="")
    created_at: datetime = Field(default_factory=utcnow)

    model_config = ConfigDict(from_attributes=True)
