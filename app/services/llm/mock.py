"""Mock implementation of the vision LLM adapter for local development."""
from __future__ import annotations

import asyncio
from typing import AsyncIterator, Sequence

from app.services.llm.base import VisionLLMAdapter


class MockVisionAdapter(VisionLLMAdapter):
    """A deterministic caption generator for testing without external APIs."""

    def __init__(self, delay: float = 0.0) -> None:
        self.delay = delay

    async def generate_caption(
        self, frame_bytes: bytes, context: Sequence[str]
    ) -> AsyncIterator[str]:
        words = [
            "Mock",
            "caption",
            "with",
            f"{len(frame_bytes)}",
            "bytes",
        ]
        if context:
            words.append("context:")
            words.extend(list(context)[-2:])
        for index, word in enumerate(words):
            if self.delay:
                await asyncio.sleep(self.delay)
            suffix = " " if index < len(words) - 1 else ""
            yield f"{word}{suffix}"
