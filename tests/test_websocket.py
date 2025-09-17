from __future__ import annotations

from starlette.testclient import TestClient

from app.main import create_app


def test_websocket_receives_history(configure_settings) -> None:
    app = create_app()
    with TestClient(app) as client:
        session_response = client.post("/sessions", json={"name": "ws"})
        session_id = session_response.json()["id"]

        files = {"file": ("frame.jpg", b"data", "image/jpeg")}
        client.post(f"/sessions/{session_id}/frames", files=files)

        with client.websocket_connect(f"/ws/captions?session_id={session_id}") as websocket:
            history_message = websocket.receive_json()
            assert history_message["type"] == "history"
            assert "Mock caption" in history_message["text"]
