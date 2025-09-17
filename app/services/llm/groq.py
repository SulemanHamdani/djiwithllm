"""Groq API implementation of the vision LLM adapter."""
from __future__ import annotations

import base64
import os
from typing import AsyncIterator, Sequence

import httpx

from app.services.llm.base import VisionLLMAdapter


class GroqVisionAdapter(VisionLLMAdapter):
    """Adapter that calls Groq's OpenAI-compatible API for vision captioning."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "llama-3.2-11b-vision-preview",
        endpoint: str = "https://api.groq.com/openai/v1/chat/completions",
        timeout: float = 30.0,
    ) -> None:
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.model = model
        self.endpoint = endpoint
        self.timeout = timeout

    def _build_prompt(self, context: Sequence[str]) -> str:
        parts = [
            "You are a real-time narrator for a DJI Tello drone flight.",
            "Describe the current frame in one concise sentence.",
        ]
        if context:
            parts.append(
                "Recent context: " + " | ".join(context[-3:])
            )
        return "\n".join(parts)

    async def generate_caption(
        self, frame_bytes: bytes, context: Sequence[str]
    ) -> AsyncIterator[str]:
        if not self.api_key:
            raise RuntimeError("GROQ_API_KEY is not configured")

        image_b64 = base64.b64encode(frame_bytes).decode("utf-8")
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant that describes live aerial footage succinctly.",
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": self._build_prompt(context)},
                        {"type": "input_image", "image_base64": image_b64},
                    ],
                },
            ],
            "max_tokens": 128,
            "temperature": 0.2,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                self.endpoint,
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"].strip()
            yield content
