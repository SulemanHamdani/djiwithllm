# tello-live-caption-backend — High-Level TODO

A simple plan for your **codex agent** to implement the backend that ingests frames from a DJI Tello, generates live captions with a Vision LLM, and streams them to a UI. Keep details abstract and focus on good design practices.

---

## Goals

* Live narration of drone video (≈1s latency budget).
* Stream captions/transcripts to multiple clients via WebSocket.
* Clean, maintainable, and extensible backend.

---

## Architecture Overview

* **Capture Client**: Small Python script that connects to Tello, extracts frames (e.g. every 0.5s), and sends them to backend.
* **Backend**: FastAPI app that receives frames, queries a Vision LLM for captions, and streams results to frontend via WebSocket.
* **Frontend**: Displays live video + caption transcript. (Not part of this backend TODO.)

---

## Key Components

1. **Session Management**

   * Create/delete sessions.
   * Associate multiple WebSocket clients to a session.

2. **Frame Ingestion**

   * Endpoint to receive frames (JPEG images).
   * Forward frames to caption service.

3. **Caption Service**

   * Calls Vision LLM with the frame and recent context.
   * Streams tokens or final caption result.

4. **WebSocket Hub**

   * Broadcast captions (partial + final) to all session clients.
   * Handle disconnects and reconnections.

5. **Adapters**

   * Abstract interface for Vision LLM (easy to swap providers).
   * Optional: Mock adapter for local development.

---

## Suggested API Contracts

* `POST /sessions` → create session
* `DELETE /sessions/{id}` → delete session
* `POST /sessions/{id}/frames` → send a frame
* `WS /ws/captions?session_id=...` → stream captions

---

## Implementation Guidelines

* Use **FastAPI** for APIs and WebSockets.
* Use **Pydantic models** for request/response validation.
* Organize code into `routes/`, `services/`, `models/`, `utils/`.
* Keep state ephemeral (in memory) for MVP; add Redis if scaling later.
* Handle errors gracefully and never block the WebSocket stream.
* Add simple logging and health check endpoint.

---

## Development Steps

1. Scaffold FastAPI project with health route.
2. Implement session creation and WebSocket hub.
3. Implement frame ingestion route.
4. Add mock Vision LLM adapter (Groq -> hypothetical api key and use llama 4 scout maybe) → verify full flow.
5. Integrate actual Vision LLM.
6. Add simple logging

---

## Good to have Goals 

* Rate limiting and frame deduplication.
* Storing transcripts in database. Make 1 table (basic)
* TTS narration output.
* Richer insights (objects, OCR, hazards).

---

## Coding Practices

* Follow **clean code structure** (small, testable functions).
* Use **async/await** for non-blocking I/O.
* Write **docstrings** and comments where necessary.
* Add **unit + integration tests**.
* Follow **PEP8 style** and run linters.

---

This is the high-level roadmap. Leave implementation details (prompt templates, Redis schema, etc.) to the coding agent, and let it apply best practices for each step.
