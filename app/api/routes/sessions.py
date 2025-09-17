"""Routes for managing captioning sessions."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Response, status

from app.api.deps import get_session_service
from app.schemas.session import SessionCreate, SessionRead
from app.services.session_service import SessionService

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", response_model=SessionRead, status_code=status.HTTP_201_CREATED)
async def create_session(
    payload: SessionCreate,
    session_service: SessionService = Depends(get_session_service),
) -> SessionRead:
    """Create a new captioning session."""

    return await session_service.create_session(payload)


@router.get("/{session_id}", response_model=SessionRead)
async def get_session(
    session_id: str,
    session_service: SessionService = Depends(get_session_service),
) -> SessionRead:
    """Retrieve session details."""

    return await session_service.get_session(session_id)


@router.delete(
    "/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
async def delete_session(
    session_id: str,
    session_service: SessionService = Depends(get_session_service),
) -> Response:
    """Delete a session and associated transcripts."""

    await session_service.delete_session(session_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
