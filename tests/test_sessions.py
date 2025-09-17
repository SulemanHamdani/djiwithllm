from __future__ import annotations

import pytest

from httpx import AsyncClient


@pytest.mark.asyncio
async def test_session_lifecycle(async_client: AsyncClient) -> None:
    create_response = await async_client.post("/sessions", json={"name": "demo"})
    assert create_response.status_code == 201
    session_id = create_response.json()["id"]

    get_response = await async_client.get(f"/sessions/{session_id}")
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "demo"

    delete_response = await async_client.delete(f"/sessions/{session_id}")
    assert delete_response.status_code == 204

    missing_response = await async_client.get(f"/sessions/{session_id}")
    assert missing_response.status_code == 404
