"""Health check endpoint."""
from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.get("/health", summary="Service health check")
async def health_check() -> dict[str, str]:
    """Return application status information."""

    return {"status": "ok"}
