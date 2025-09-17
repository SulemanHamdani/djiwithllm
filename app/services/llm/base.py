"""Interfaces for vision language model integrations."""
from __future__ import annotations

from typing import AsyncIterator, Protocol, Sequence


class VisionLLMAdapter(Protocol):
    """Protocol for adapters capable of generating captions from frames."""

    async def generate_caption(
        self, frame_bytes: bytes, context: Sequence[str]
    ) -> AsyncIterator[str]:
        """Yield caption text chunks for the provided frame and context."""

        ...
