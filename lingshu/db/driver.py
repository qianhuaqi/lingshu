"""Database driver contract definitions."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from .config import DatabaseConfig


@runtime_checkable
class DatabaseDriver(Protocol):
    """Minimal async driver contract for future database extensions."""

    @property
    def backend(self) -> str:
        """Backend kind handled by this driver, such as ``mysql`` or ``redis``."""

    async def startup(self, config: DatabaseConfig) -> object:
        """Acquire driver-owned resources during application startup."""

    async def shutdown(self, handle: object) -> None:
        """Release resources acquired by ``startup`` during shutdown."""


__all__ = ("DatabaseDriver",)
