from __future__ import annotations

import pytest

from httpx import AsyncClient


@pytest.mark.asyncio
async def test_frame_ingestion_generates_caption(async_client: AsyncClient) -> None:
    create_response = await async_client.post("/sessions", json={"name": "ingest"})
    session_id = create_response.json()["id"]

    files = {"file": ("frame.jpg", b"\xff\xd8\xff", "image/jpeg")}
    ingest_response = await async_client.post(
        f"/sessions/{session_id}/frames", files=files
    )
    assert ingest_response.status_code == 202
    caption = ingest_response.json()["caption"]
    assert "Mock caption" in caption

    session_response = await async_client.get(f"/sessions/{session_id}")
    transcripts = session_response.json()["transcripts"]
    assert len(transcripts) == 1
    assert transcripts[0]["text"] == caption
