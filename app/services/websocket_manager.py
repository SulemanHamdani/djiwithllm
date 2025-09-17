"""Manages websocket connections for caption streaming."""
from __future__ import annotations

import asyncio
from contextlib import suppress
from typing import Dict, Iterable, Set

from fastapi import WebSocket


class WebSocketManager:
    """Tracks active websocket connections per session."""

    def __init__(self) -> None:
        self._connections: Dict[str, Set[WebSocket]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, session_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            connections = self._connections.setdefault(session_id, set())
            connections.add(websocket)

    async def disconnect(self, session_id: str, websocket: WebSocket) -> None:
        async with self._lock:
            if session_id in self._connections and websocket in self._connections[session_id]:
                self._connections[session_id].remove(websocket)
                if not self._connections[session_id]:
                    del self._connections[session_id]
        with suppress(Exception):
            await websocket.close()

    async def broadcast(self, session_id: str, payload: dict) -> None:
        async with self._lock:
            connections = list(self._connections.get(session_id, set()))
        for connection in connections:
            try:
                await connection.send_json(payload)
            except Exception:
                await self.disconnect(session_id, connection)

    async def list_connections(self, session_id: str) -> Iterable[WebSocket]:
        async with self._lock:
            return tuple(self._connections.get(session_id, set()))
