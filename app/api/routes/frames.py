"""Frame ingestion endpoint."""
from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.api.deps import get_caption_service
from app.services.caption_service import CaptionService

router = APIRouter(prefix="/sessions", tags=["frames"])


@router.post("/{session_id}/frames", status_code=status.HTTP_202_ACCEPTED)
async def ingest_frame(
    session_id: str,
    file: UploadFile = File(...),
    caption_service: CaptionService = Depends(get_caption_service),
) -> dict[str, str]:
    """Receive a frame for caption generation."""

    frame_bytes = await file.read()
    if not frame_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty frame payload",
        )
    caption = await caption_service.process_frame(session_id, frame_bytes)
    return {"caption": caption}
