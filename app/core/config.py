"""Application configuration settings."""
from __future__ import annotations

import os
from functools import lru_cache
from typing import List

from pydantic import BaseModel, Field


class Settings(BaseModel):
    """Runtime configuration loaded from environment variables."""

    app_name: str = Field(default="Tello Live Caption Backend")
    debug: bool = Field(default=False)
    database_url: str = Field(default="sqlite+aiosqlite:///./app.db")
    allowed_origins: List[str] = Field(default_factory=lambda: ["*"])
    vision_adapter: str = Field(default="mock")

    @classmethod
    def from_env(cls) -> "Settings":
        """Create settings instance by reading environment variables."""

        return cls(
            app_name=os.getenv("APP_NAME", cls.model_fields["app_name"].default),
            debug=os.getenv("DEBUG", "false").lower() in {"1", "true", "yes"},
            database_url=os.getenv(
                "DATABASE_URL", cls.model_fields["database_url"].default
            ),
            allowed_origins=[
                origin.strip()
                for origin in os.getenv("ALLOWED_ORIGINS", "").split(",")
                if origin.strip()
            ]
            or cls.model_fields["allowed_origins"].default_factory(),
            vision_adapter=os.getenv(
                "VISION_ADAPTER", cls.model_fields["vision_adapter"].default
            ),
        )


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings instance."""

    return Settings.from_env()
